# -*- coding: utf-8 -*-
'''
@File  : config.py.py
@Date  : 2019/1/15/015 17:28
'''
import os, platform

# 测试环境域名
# TESTDEV1 = "http://fp02.ops.gaoshou.me"
# TESTDEV2 = "http://fp02.ops.gaoshou.me"
# TESTDEV = "http://www.baidu.com"
TESTDEV0 = "http://fp02.ops.gaoshou.me"
TESTDEV1 = "http://fp01.ops.gaoshou.me"
TESTDEV2 = "http://fp02.ops.gaoshou.me"

# 用例字段名
CASENAME = ["caseId", "apiId", "caseDescribe", "apiHost", "apiParams", "apiHeaders", "method", "relatedApi",
            "relatedParams", "expect", "sqlStatement", "databaseExpect", "isExcute"]
if platform.system() == "Windows":
    # 用例存放路径
    CASEPATH = os.path.dirname(__file__).replace("common", "cases") + "\exmple.xlsx"
else:
    CASEPATH = os.path.dirname(__file__).replace("common", "cases") + "/case_exmple.xlsx"
TABLECASE = "testCase"
TABLERESULT = "testResult"
TABLEAPIINFO = "apiInfo"
CASEID = "caseId"
APIID = "apiId"
CASEDESCRIBE = "caseDescribe"
APIHOST = "apiHost"
PARMAS = "apiParams"
METHOD = "method"
HEADERS = "headers"
RELATEDAPI = "relatedApi"
RELEATEDPARAMS = "relatedParams"
FACT = "fact"
EXPECT = "expect"
SQLSTATEMENT = "sqlStatement"
DATABASERESUTL = "databaseResult"
DATABASEEXPECT = "databaseExpect"
ISPASS = "ispass"
TIME = "time"
FORMORT = "%Y/%m/%d %H:%M:%S"
PASS = "pass"
FAIL = "fail"
BLOCK = "block"
REASON = "reason"
