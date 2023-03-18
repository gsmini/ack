# -*- coding:utf-8 -*-
import logging

from ack.settings import DEBUG

LOGGER_NAME = "ack"


# 终端输出日志，可以用来部署在k8s上捕捉docker的标准输出记录日志
def init_logger_handler():
    logger = logging.getLogger(LOGGER_NAME)

    logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)

    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG if DEBUG else logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


logger = init_logger_handler()
