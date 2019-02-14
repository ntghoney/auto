# -*- coding: utf-8 -*-
'''
@File  : log.py
@Date  : 2019/1/15/015 17:35
'''
import logging
from common.parseConfig import setPath
import datetime
import os


def get_now():
    return datetime.datetime.now()


class Log(object):
    def __init__(self):
        filename = "{}.log".format(get_now().strftime("%Y%m%d"))
        self.logPath = setPath(pathName="log", fileName=filename)
        self.logger = logging.getLogger(__name__)
        # 将当前文件的handlers 清空
        self.logger.handlers = []
        # 然后再次移除当前文件logging配置
        self.logger.removeHandler(self.logger.handlers)
        # 这里进行判断，如果logger.handlers列表为空，则添加，否则，直接去写日志
        if not self.logger.handlers:
            # loggger 文件配置路径
            self.handler = logging.FileHandler(self.logPath,encoding="gbk")
        # logger 配置等级
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s -%(filename)s : %(lineno)d :%(funcName)s - %(message)s')
        self.console = logging.StreamHandler()
        self.console.setLevel(logging.INFO)
        self.console.setFormatter(formatter)
        # 添加输出格式进入handler
        self.handler.setFormatter(formatter)
        # 添加文件设置金如handler
        self.logger.addHandler(self.handler)
        self.logger.addHandler(self.console)

    def getLog(self):
        return self.logger


if __name__ == '__main__':
    log = Log()
    log.info("hello")
