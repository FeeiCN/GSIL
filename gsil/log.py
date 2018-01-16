# -*- coding: utf-8 -*-

"""
    log
    ~~~

    Implements color logger

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2018 Feei. All rights reserved
"""
import os
import colorlog
import logging
from logging import handlers

log_path = 'logs'
if os.path.isdir(log_path) is not True:
    os.mkdir(log_path, 0o755)
logfile = os.path.join(log_path, 'gsil.log')

handler = colorlog.StreamHandler()
formatter = colorlog.ColoredFormatter(
    '%(log_color)s%(asctime)s [%(name)s] [%(levelname)s] %(message)s%(reset)s',
    datefmt=None,
    reset=True,
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    },
    secondary_log_colors={},
    style='%'
)
handler.setFormatter(formatter)

file_handler = handlers.RotatingFileHandler(logfile, maxBytes=(1048576 * 5), backupCount=7)
file_handler.setFormatter(formatter)

logger = colorlog.getLogger('GSIL')
logger.addHandler(handler)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)
