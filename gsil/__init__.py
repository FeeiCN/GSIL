# -*- coding: utf-8 -*-

"""
    GSIL
    ~~~~

    Implements Github Sensitive Information Leak

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/FeeiCN/gsil
    :license:   GPL, see LICENSE for more details.
    :copyright: Copyright (c) 2018 Feei. All rights reserved
"""
import sys
import time
import traceback
import multiprocessing
from .engine import Engine
from .log import logger
from .config import Config, get_rules, tokens, daily_run_data
from .process import send_running_data_report

running_data = []
token_dict = multiprocessing.Manager().dict()
scan_rule_queue = multiprocessing.Queue()

for t in tokens:
    token_dict[t] = False


# search single rule
def search(idx, lock):
    """
    class instance can't pickle in apply_async
    :param idx:
    :param rule:
    :return:
    """
    while True:
        token = ''
        lock.acquire()
        for t in tokens:
            if not token_dict[t]:
                token = t
                token_dict[t] = True
                break
        rule = scan_rule_queue.get()
        lock.release()
        if token == '':
            logger.critical('subprocess more than token number!')
            exit(0)
        try:
            ret = Engine(token=token).search(rule)
            lock.acquire()
            token_dict[token] = False
            store_result(ret)
            scan_rule_queue.put(rule)
            lock.release()
        except Exception as e:
            traceback.print_exc()
            #return False, None, traceback.format_exc()

# store search result
def store_result(result):
    """
    store running result
    :param result:
    :return:
    """
    r_ret, r_rule, r_msg = result
    if r_ret:
        r_datetime = time.strftime("%Y-%m-%d %H:%M:%S")
        # 不需要的类型过滤掉
        if r_rule.corp.lower() in ['vulbox']:
            return
        with open(Config().run_data, 'a') as f:
            rule = '[{t}][{c}][{k}]'.format(t=r_rule.types, c=r_rule.corp, k=r_rule.keyword)
            f.write('{datetime} {ret} {rule} {msg}\r\n'.format(datetime=r_datetime, ret=r_ret, rule=rule, msg=r_msg))
        # store list
        running_data.append([r_datetime, r_ret, rule, r_msg])

# start
def start(rule_types):
    rules = get_rules(rule_types)
    if len(rules) == 0:
        logger.critical('get rules failed, rule types not found!')
        exit(0)
    logger.info('rules length: {rl}'.format(rl=len(rules)))
    lock = multiprocessing.Manager().Lock()
    pool = multiprocessing.Pool(len(tokens))
    for idx, rule_object in enumerate(rules):
        logger.info('>>>>>>>>>>>>> {n} > {r} >>>>>>'.format(n=rule_object.corp, r=rule_object.keyword))
        scan_rule_queue.put(rule_object)
        pool.apply_async(search, args=(idx, lock))
    pool.close()
    pool.join()


# generate report file
def generate_report(data):
    for rd in data:
        datetime, ret, rule, msg = rd
        html = '<li> {datetime} {ret} {rule} {msg}</li>'.format(datetime=datetime, ret=ret, rule=rule, msg=msg)
        run_data = daily_run_data()
        run_data['list'].append(html)
        if ret:
            run_data['found_count'] += msg
            run_data['job_success'] += 1
        else:
            run_data['job_failed'] += 1
        daily_run_data(run_data)


def gsil():
    if sys.argv[1] == '--report':
        # send daily running data report
        send_running_data_report()
    elif sys.argv[1] == '--verify-tokens':
        # verify tokens
        for i, token in enumerate(tokens):
            ret, msg = Engine(token=token).verify()
            logger.info('{i} {ret} token: {token} {msg}'.format(i=i, msg=msg, token=token, ret=ret))
    else:
        logger.info('start monitor github information leakage: {types}'.format(types=sys.argv[1]))
        # start
        start(sys.argv[1])
        # start generate report file
        generate_report(running_data)


if __name__ == '__main__':
    gsil()
