# -*- coding: utf-8 -*-

"""
    tests.test_github
    ~~~~~~~~~~~~~~~~~

    Implements test GitHub API

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/FeeiCN/gsil
    :license:   GPL, see LICENSE for more details.
    :copyright: Copyright (c) 2018 Feei. All rights reserved
"""
import base64
import pytest
from github import Github, BadCredentialsException

TOKEN = base64.b64decode('YzA4YTVhOTA1ZGExYjg5YTc1ZmI4NmE3MmM3ZjUyNzg2NmRmZmRlNA==').decode()


def test_init_success():
    g = Github(login_or_token=TOKEN)
    try:
        limit, limit2 = g.rate_limiting
        assert limit > 4900
    except BadCredentialsException as e:
        assert False

    g = Github(login_or_token=TOKEN[0:18])
    with pytest.raises(BadCredentialsException) as e:
        g = g.rate_limiting
