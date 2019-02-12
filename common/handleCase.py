# -*- coding: utf-8 -*-
'''
@File  : handleCase.py
@Date  : 2019/1/15/015 18:24
'''
from common.parseExc import *
from common.log import Log
from common.config import *
import logging
import re
import os

log = logging.getLogger()


# 去掉换行符
def quchu_n(str):
    str = str.replace("\n", "")
    return str


def get_case_path():
    """
    用例路径，以case_开头的.xlsx文件
    :return:
    """
    path = os.path.dirname(__file__).replace("common", "cases")
    rep = re.compile(r"^case_")
    dir_name = os.listdir(path)
    case_path = []
    for file in dir_name:
        extension = os.path.splitext(file)[1]  # 文件拓展名
        file_name = os.path.splitext(file)[0]  # 文件名
        if extension == ".xlsx" and re.findall(rep, file_name):
            case_path.append(os.path.join(path, file))
        else:
            log.info("{}不符合规则".format(file))
    return case_path


class HandleCase(object):
    def __init__(self,case_path):
        # 实例parseExc对象
        self.log = Log().getLog()
        self.pe = PaserExc(case_path, 0)

    # 总用例数
    def get_totals(self):
        return self.pe.get_nrows() - 1

    # 处理检查点中数据
    def handle_checkPoint(self, item):
        global key, value
        checkPints = {}

        key, value = item.split("=")
        if ":" in value:
            value = value.replace(":", "：")
        if "." in key:
            temp = {}
            key1 = (str(key).split("."))[0]  # payload.coin类型的集合点解析
            key2 = (str(key).split("."))[1]
            temp[key2] = value
            checkPints[key1] = temp
        else:
            checkPints[key] = value
        return checkPints

    # 处理关联参数
    def handle_related_params(self, item):
        related_params = []
        if item:
            if ";" in item:
                #     for i in item.split(";"):
                #         if "." in i:
                #             related_params.append(i.split("."))
                #         else:
                #             related_params.append(i)
                # elif "." in item:
                #     related_params.append(item.split("."))
                # else:
                #     related_params.append(item)
                related_params = item.split(";")
        return related_params

    def handle_data(self, datas):
        """
        处理用例的数据格式
        """
        global cid, apiId, describe, host, expect, method, params, checkPints, relatedApi, relatedParams
        checkPints = {}
        # relatedParamsInfo = {}
        if isinstance(datas, dict):
            cid = int(datas[CASEID])
            apiId = int(datas[APIID])
            describe = str(quchu_n(datas[CASEDESCRIBE]))
            host = str(quchu_n(datas[APIHOST]))
            expect = str(datas[EXPECT])
            method = str(datas[METHOD])
            params = str(datas[PARMAS])
            relatedParams = str(datas[RELEATEDPARAMS])
            if expect:
                if expect.split(";")[-1] != "":
                    for item in expect.split(";"):
                        checkPints.update(self.handle_checkPoint(item))
                else:
                    checkPints = self.handle_checkPoint(expect.replace(";", ""))
                datas[EXPECT] = checkPints
            else:
                datas[EXPECT] = {}
            return datas
        else:
            raise Exception("参数错误，所传参数datas必须是字典")

    # 获得所有测试用例
    def get_cases(self):
        values = []
        cases = []
        result = []
        rowValues = self.pe.get_row()[1:]
        for row in rowValues:
            values.append(dict(zip(CASENAME, row)))
        # 去掉不执行的用例
        for case in values:
            if case["isExcute"] == "y" or case["isExcute"] == "Y" or case["isExcute"] == "":
                cases.append(case)
            case.pop("isExcute")
        # 转换用例字段的数据格式
        for case in cases:
            case[CASEID] = int(case[CASEID])
            case[APIID] = int(case[APIID])
            case[CASEDESCRIBE] = quchu_n(str(case[CASEDESCRIBE]))
            case[APIHOST] = quchu_n(str(case[APIHOST]))
            case[PARMAS] = quchu_n(case[PARMAS])
            case["apiHeaders"] = quchu_n(case["apiHeaders"])
            case[METHOD] = quchu_n(case[METHOD])
            if isinstance(case[RELATEDAPI], float):
                case[RELATEDAPI] = int(case[RELATEDAPI])
            else:
                case[RELATEDAPI] = None
            case[RELEATEDPARAMS] = quchu_n(case[RELEATEDPARAMS])
            case[RELEATEDPARAMS] = case[RELEATEDPARAMS]
            case[EXPECT] = quchu_n(case[EXPECT])
            self.handle_data(case)
            result.append(case)
        return result


if __name__ == '__main__':
    cases=[]
    for i in get_case_path():
        hc=HandleCase(i)
        cases.extend(hc.get_cases())
    print(len(cases))
