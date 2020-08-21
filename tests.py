#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    GSIL
    ~~~~

    TESTS

    Usage:
        python tests.py

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/FeeiCN/GSIL
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2018 Feei. All rights reserved
"""
import unittest


class Tests(unittest.TestCase):
    def test_notification(self):
        """
        测试邮件通知功能是否可正常使用
        :return:
        """
        from gsil.notification import Notification
        subject = 'test from GSIL'
        to = cc = 'feei@feei.cn'
        html = '<h1>Test Content from GSIL</h1>'
        self.assertTrue(Notification(subject, to, cc).notification(html))

    def test_github_token(self):
        import base64
        from github import Github, BadCredentialsException

        token = base64.b64decode('NGI0NTA5Y2Y2NWYxN2M4MjI0NDczODk3NzgzYzVkODBjNWEzNzMzMwo=').decode().strip()
        g = Github(login_or_token=token)
        self.assertRaises(BadCredentialsException, g.rate_limiting)

    def test_clone(self):
        from gsil.process import clone
        clone('https://github.com/FeeiCN/dict', 'ttt')

    def test_generate_tests_honeypot_cases(self):
        import codecs
        from gsil.config import get_rules
        with codecs.open('honeypot/services.java', 'w', encoding='utf-8-sig') as f:
            f.write("// 如果你的GitHub泄漏监控到此条记录，并且发现时间和本文件的最后修改时间大于十分钟，请扔掉你的GitHub泄漏监控，来使用https://github.com/FeeiCN/GSIL\r\n")
            f.write(
                "// if your GitHub leak monitors this record, and the time of discovery and the last modification time of this file is greater than ten minutes, please discard it and use https://github.com/FeeiCN/GSIL\r\n")
            rules = get_rules('alibaba')
            for idx, rule_object in enumerate(rules):
                f.write(f'http://gsil.honeypot.{rule_object.keyword}/api?appid=eQcZ8nR1bTFPNs1aEtP9XVMhLqNiIB&secretKey=bmkPGK7Bqnv7kbbBla4amaDvb8ImHQ\r\n')


if __name__ == '__main__':
    unittest.main()
