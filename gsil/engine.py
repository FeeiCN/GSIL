# -*- coding: utf-8 -*-

"""
    engine
    ~~~~~~

    Implements Github search engine

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/FeeiCN/gsil
    :license:   GPL, see LICENSE for more details.
    :copyright: Copyright (c) 2018 Feei. All rights reserved
"""
import re
import socket
import traceback
import requests
from github import Github, GithubException
from bs4 import BeautifulSoup
from gsil.config import Config, public_mail_services, exclude_repository_rules, exclude_codes_rules
from .process import Process, clone
from IPy import IP
from tld import get_tld
from .log import logger

regex_mail = r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
regex_host = r"@([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
regex_pass = r"(pass|password|pwd)"
regex_title = r"<title>(.*)<\/title>"
regex_ip = r"^((([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))$"

# Increase the number of single pages to reduce the number of requests
# https://developer.github.com/v3/#pagination
# 每一页的数量（会影响到报告的效率）
per_page = 50

# TODO The number of pre calculated requests according to rule number and number of pages
#
# pages * per_page * rules = requests
# 2 * 30 * 24 = 1440
#
# 默认扫描页数
default_pages = 4


class Engine(object):
    def __init__(self, token):
        """
        GitHub engine
        """
        self.token = token
        self.g = Github(login_or_token=token, per_page=per_page)
        self.rule_object = None
        self.code = ''
        # jquery/jquery
        self.full_name = ''
        self.sha = ''
        self.url = ''
        # src/attributes/classes.js
        self.path = ''

        self.result = None
        # 被排除掉的结果，为防止误报，将发送邮件人工核查
        self.exclude_result = None
        self.hash_list = None
        self.processed_count = None
        self.next_count = None

    def process_pages(self, pages_content, page, total):
        for index, content in enumerate(pages_content):
            current_i = page * per_page + index
            base_info = f'[{self.rule_object.keyword}] [{current_i}/{total}]'

            # 没有处理成功的，且遇到三个已处理的则跳过之后所有的
            if self.next_count == 0 and self.processed_count > 3:
                logger.info(
                    f'{base_info} Has encountered {self.processed_count} has been processed, skip the current rules!')
                return False

            # html_url
            self.url = content.html_url

            # sha
            try:
                self.sha = content.sha
            except Exception as e:
                logger.warning(f'sha exception {e}')
                self.sha = ''
                self.url = ''

            if self.sha in self.hash_list:
                # pass already processed
                logger.info(f'{base_info} Processed, skip! ({self.processed_count})')
                self.processed_count += 1
                continue

            # path
            self.path = content.path

            # full name
            self.full_name = content.repository.full_name.strip()
            if self._exclude_repository():
                # pass exclude repository
                logger.info(f'{base_info} Excluded because of the path, skip!')
                continue

            # code
            try:
                self.code = content.decoded_content.decode('utf-8')
            except Exception as e:
                logger.warning(f'Get Content Exception: {e} retrying...')
                continue

            match_codes = self.codes()
            if len(match_codes) == 0:
                logger.info(f'{base_info} Did not match the code, skip!')
                continue
            result = {
                'url': self.url,
                'match_codes': match_codes,
                'hash': self.sha,
                'code': self.code,
                'repository': self.full_name,
                'path': self.path,
            }
            if self._exclude_codes(match_codes):
                logger.info(f'{base_info} Code may be useless, do not skip, add to list to be reviewed!')
                self.exclude_result[current_i] = result
            else:
                self.result[current_i] = result

            # 独立进程下载代码
            git_url = content.repository.html_url
            clone(git_url, self.sha)
            logger.info(f'{base_info} Processing is complete, the next one!')
            self.next_count += 1

        return True

    def verify(self):
        try:
            ret = self.g.rate_limiting
            return True, f'TOKEN-PASSED: {ret}'
        except GithubException as e:
            return False, f'TOKEN-FAILED: FAILED'

    def search(self, rule_object):
        """
        Search content by rule on GitHub
        :param rule_object:
        :return: (ret, rule, msg)
        """
        self.rule_object = rule_object

        # 已经处理过的数量
        self.processed_count = 0
        # 处理成功的数量
        self.next_count = 0

        # max 5000 requests/H
        try:
            rate_limiting = self.g.rate_limiting
            rate_limiting_reset_time = self.g.rate_limiting_resettime
            logger.info('----------------------------')

            # RATE_LIMIT_REQUEST: rules * 1
            # https://developer.github.com/v3/search/#search-code
            ext_query = ''
            if self.rule_object.extension is not None:
                for ext in self.rule_object.extension.split(','):
                    ext_query += f'extension:{ext.strip().lower()} '
            keyword = f'{self.rule_object.keyword} {ext_query}'
            logger.info(f'Search keyword: {keyword}')
            resource = self.g.search_code(keyword, sort="indexed", order="desc")
        except GithubException as e:
            msg = f'GitHub [search_code] exception(code: {e.status} msg: {e.data} {self.token}'
            logger.critical(msg)
            return False, self.rule_object, msg

        logger.info(
            f'[{self.rule_object.keyword}] Speed Limit Results (Remaining Times / Total Times): {rate_limiting}  Speed limit reset time: {rate_limiting_reset_time}')
        logger.info(
            '[{k}] The expected number of acquisitions: {page}(Pages) * {per}(Per Page) = {total}(Total)'.format(
                k=self.rule_object.keyword, page=default_pages, per=per_page, total=default_pages * per_page))

        # RATE_LIMIT_REQUEST: rules * 1
        try:
            total = resource.totalCount
            logger.info(f'[{self.rule_object.keyword}] The actual number: {total}')
        except socket.timeout as e:
            return False, self.rule_object, e
        except GithubException as e:
            msg = f'GitHub [search_code] exception(code: {e.status} msg: {e.data} {self.token}'
            logger.critical(msg)
            return False, self.rule_object, msg

        self.hash_list = Config().hash_list()
        if total < per_page:
            pages = 1
        else:
            pages = default_pages
        for page in range(pages):
            self.result = {}
            self.exclude_result = {}
            try:
                # RATE_LIMIT_REQUEST: pages * rules * 1
                pages_content = resource.get_page(page)
            except socket.timeout:
                logger.info(f'[{self.rule_object.keyword}] [get_page] Time out, skip to get the next page！')
                continue
            except GithubException as e:
                msg = f'GitHub [get_page] exception(code: {e.status} msg: {e.data} {self.token}'
                logger.critical(msg)
                return False, self.rule_object, msg

            logger.info(f'[{self.rule_object.keyword}] Get page {page} data for {len(pages_content)}')
            if not self.process_pages(pages_content, page, total):
                # 若遇到处理过的，则跳过整个规则
                break
            # 每一页发送一份报告
            Process(self.result, self.rule_object).process()
            # 暂时不发送可能存在的误报 TODO
            # Process(self.exclude_result, self.rule_object).process(True)

        logger.info(
            f'[{self.rule_object.keyword}] The current rules are processed, the process of normal exit!')
        return True, self.rule_object, len(self.result)

    def codes(self):
        # 去除图片的显示
        self.code = self.code.replace('<img', '')
        codes = self.code.splitlines()
        codes_len = len(codes)
        keywords = self._keywords()
        match_codes = []
        if self.rule_object.mode == 'mail':
            return self._mail()
        elif self.rule_object.mode == 'only-match':
            # only match mode(只匹配存在关键词的行)
            for code in codes:
                for kw in keywords:
                    if kw in code:
                        match_codes.append(code)
            return match_codes
        elif self.rule_object.mode == 'normal-match':
            # normal-match（匹配存在关键词的行及其上下3行）
            for idx, code in enumerate(codes):
                for keyword in keywords:
                    if keyword in code:
                        idxs = []
                        # prev lines
                        for i in range(-3, -0):
                            i_idx = idx + i
                            if i_idx in idxs:
                                continue
                            if i_idx < 0:
                                continue
                            if codes[i_idx].strip() == '':
                                continue
                            logger.debug(f'P:{i_idx}/{codes_len}: {codes[i_idx]}')
                            idxs.append(i_idx)
                            match_codes.append(codes[i_idx])
                        # current line
                        if idx not in idxs:
                            logger.debug(f'C:{idx}/{codes_len}: {codes[idx]}')
                            match_codes.append(codes[idx])
                        # next lines
                        for i in range(1, 4):
                            i_idx = idx + i
                            if i_idx in idxs:
                                continue
                            if i_idx >= codes_len:
                                continue
                            if codes[i_idx].strip() == '':
                                continue
                            logger.debug(f'N:{i_idx}/{codes_len}: {codes[i_idx]}')
                            idxs.append(i_idx)
                            match_codes.append(codes[i_idx])
            return match_codes
        else:
            # 匹配前20行
            return self.code.splitlines()[0:20]

    def _keywords(self):
        if '"' not in self.rule_object.keyword and ' ' in self.rule_object.keyword:
            return self.rule_object.keyword.split(' ')
        else:
            if '"' in self.rule_object.keyword:
                return [self.rule_object.keyword.replace('"', '')]
            else:
                return [self.rule_object.keyword]

    def _mail(self):
        logger.info(f'[{self.rule_object.keyword}] mail rule')
        match_codes = []
        mails = []
        # 找到所有邮箱地址
        # TODO 此处可能存在邮箱账号密码是加密的情况，导致取不到邮箱地址
        mail_multi = re.findall(regex_mail, self.code)
        for mm in mail_multi:
            mail = mm.strip().lower()
            if mail in mails:
                logger.info('[SKIPPED] Mail already processed!')
                continue
            host = re.findall(regex_host, mail)
            host = host[0].strip()
            if host in public_mail_services:
                logger.info('[SKIPPED] Public mail services!')
                continue
            mails.append(mail)

            # get mail host's title
            is_inner_ip = False
            if re.match(regex_ip, host) is None:
                try:
                    top_domain = get_tld(host, fix_protocol=True)
                except Exception as e:
                    logger.warning(f'get top domain exception {e}')
                    top_domain = host
                if top_domain == host:
                    domain = f'http://www.{host}'
                else:
                    domain = f'http://{host}'
            else:
                if IP(host).iptype() == 'PRIVATE':
                    is_inner_ip = True
                domain = f'http://{host}'
            title = '<Unknown>'
            if is_inner_ip is False:
                try:
                    response = requests.get(domain, timeout=4).content
                except Exception as e:
                    title = f'<{e}>'
                else:
                    try:
                        soup = BeautifulSoup(response, "html5lib")
                        if hasattr(soup.title, 'string'):
                            title = soup.title.string.strip()[0:150]
                    except Exception as e:
                        title = 'Exception'
                        traceback.print_exc()

            else:
                title = '<Inner IP>'

            match_codes.append(f"{mail} {domain} {title}")
            logger.info(f' - {mail} {domain} {title}')
        return match_codes

    def _exclude_repository(self):
        """
        Exclude some repository(e.g. github.io blog)
        :return:
        """
        ret = False
        # 拼接完整的项目链接
        full_path = f'{self.full_name.lower()}/{self.path.lower()}'
        for err in exclude_repository_rules:
            if re.search(err, full_path) is not None:
                return True
        return ret

    @staticmethod
    def _exclude_codes(codes):
        ret = False
        for ecr in exclude_codes_rules:
            if re.search(ecr, '\n'.join(codes)) is not None:
                return True
        return ret
