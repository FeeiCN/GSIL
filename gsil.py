#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    GSIL
    ~~~~

    Implements GSIL entry

    Usage:
        python gsil.py test

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2018 Feei. All rights reserved
"""
import sys
import traceback
from gsil import gsil
from gsil.notification import Notification

if __name__ == '__main__':
    try:
        if len(sys.argv) < 2:
            print('python gsil.py <rules_type>')
            exit(0)
        sys.exit(gsil())
    except Exception as e:
        # 发送异常报告
        content = '{a}\r\n{e}'.format(a=' '.join(sys.argv), e=traceback.format_exc())
        Notification('GSIL Exception').notification(content)
