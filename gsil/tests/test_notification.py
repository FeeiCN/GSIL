# -*- coding: utf-8 -*-

"""
    tests.text_notification
    ~~~~~~~~~~~~~~~~~~~~~~~

    Implements test notification

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/FeeiCN/gsil
    :license:   GPL, see LICENSE for more details.
    :copyright: Copyright (c) 2018 Feei. All rights reserved
"""
from gsil.notification import Notification
from gsil.process import send_running_data_report


def test_send():
    assert True is Notification('Test', 'feei@feei.cn').notification('This is a test mail')


def test_send_running_data():
    assert send_running_data_report()
