# -*- coding: utf-8 -*-
'''
@File  : newRun.py
@Date  : 2019/1/25/025 15:40
'''
from common.conDatabase import ConMysql, get_base_info
from common.log import Log
from common.handleCase import HandleCase, get_case_path
# from common.httputils import Http
from common.parseConfig import ParseConfig
from common.report import get_now
import string
import datetime, time
from common.report import Report
import json
import re
from common.config import *
import random
import requests

import sys, argparse

log = Log().getLog()
pc = ParseConfig()
pat = re.compile("DIS4=(.*?);")
report = Report()  # 测试报告实例


def get_env():
    """
    执行参数判定当前测试执行环境
    0：真实环境
    1：fp01
    2:fp02
    3:fp03
    默认执行fp02
    :return: environment 测试环境域名，database_info测试环境数据库连接信息
    """
    parse = argparse.ArgumentParser(description="execution environment")
    parse.add_argument("-env", type=int, default=1)
    arg = parse.parse_args()
    env = arg.env
    if env == 0:
        environment = TESTDEV0
        database_info = get_base_info(pc.get_info("ServerDatabase0"))
    elif env == 1:
        environment = TESTDEV1
        database_info = get_base_info(pc.get_info("ServerDatabase1"))
    elif env == 2:
        environment = TESTDEV2
        database_info = get_base_info(pc.get_info("ServerDatabase2"))
    else:
        environment = TESTDEV2
        database_info = get_base_info(pc.get_info("ServerDatabase2"))
        log.error("参数错误，执行fp02环境")
    return environment, database_info


test_env, server_database = get_env()
print("当前执行环境-------{}，数据库地址-------{}".format(test_env, server_database["host"]))
con_server = ConMysql(server_database)  # 服务器数据库链接
con = ConMysql()  # 本地数据库连接对象


class Http(object):
    """
    请求封装，post,get
    """
    @classmethod
    def get(cls, path, params=None, headers=None):
        res = requests.get(test_env + path, params=params, headers=headers)
        return res

    @classmethod
    def post(cls, path, params=None, headers=None):
        res = requests.post(test_env + path, data=params, headers=headers)
        return res


def generate_random_str(randomlength=16):
    """
    生成一个指定长度的随机字符串
    :param randomlength: 指定长度，默认16
    :return:random_str str
    """
    random_str = ''
    base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
    length = len(base_str) - 1
    for i in range(randomlength):
        random_str += base_str[random.randint(0, length)]
    return random_str


def get_headers():
    """
    :从配置文件中获得请求头信息
    :return:headers dict
    """
    headers = {"Accept": "*/*", "Content-Type": "application/json;charset=utf-8"}
    cookies = pc.get_info("headers")
    headers.update(cookies)
    return headers


def get_all_case():
    """
    获得所有测试用例集合
    :return:cases list
    """
    cases = []
    case_path = get_case_path()
    for path in case_path:
        hc = HandleCase(path)
        cases.extend(hc.get_cases())
    return cases


def update_message(number):
    """
    更新t_user_verify表信息
    :param number: 用户手机号，从apiParams中获取
    :return:
    """
    result = con_server.query_one(
        "select * from t_user_verify where number ={}".format(number)
    )
    timedelta = datetime.datetime.now() - datetime.timedelta(minutes=10)  # 十分钟前的时间
    if not result:
        con_server.insert_data("t_user_verify", number=number, call_sid=generate_random_str(32), verify="4883",
                               date_created=get_now().strftime(FORMORT),
                               status=1)
        return
    if result["date_created"] < timedelta:
        sql = f"update t_user_verify set date_created='{get_now().strftime(FORMORT)}'where number={number}"
        con_server.update_data(sql)
    if result["status"] == 0:
        con_server.update_data(
            "update t_user_verify set status=1 where number={}".format(number)
        )


def get_all_related_apiinfo(case_api_id, relatedApi):
    """
    获得当前执行用例的api以及与该api相关的api信息集合
    获得的接口信息会反转，最后关联的接口在最前，用例执行的接口在最后
    :param case_api_id:当前执行用例时的apiId
    :param relatedApi:关联接口的apiId
    :return:关联接口信息 list
    """
    all_related_apiinfo = []
    # 当前用例执行的接口信息
    case_api_info = con.query_one(
        "select * from apiInfo where apiId={}".format(case_api_id)
    )
    # 将当前用例执行的接口保存到接口信息集合
    all_related_apiinfo.append(case_api_info)
    while True:
        if relatedApi is not None:
            relatedApiInfo = con.query_one(
                "select * from apiInfo where apiId={}".format(relatedApi)
            )
            if relatedApiInfo:
                relatedApi = relatedApiInfo[RELATEDAPI]
                all_related_apiinfo.append(relatedApiInfo)
                all_related_apiinfo.reverse()
            else:
                log.error("接口{}所关联的接口{}在用例中没有选择执行".format(caseId, relatedApi))
                return "ERRRR:接口{}所关联的接口{}在用例中没有选择执行".format(caseId, relatedApi)
        else:
            break
    return all_related_apiinfo


def request_api(host, params, headers, request_method):
    """
    接口请求
    """
    if request_method == "post":
        res = Http.post(host, params=params, headers=headers)
    elif request_method == "get":
        res = Http.get(host, params=params, headers=headers)
    else:
        log.error("ERRRR:暂不支持{}这种请求方式".format(method))
        return "ERRRR：暂不支持{}这种请求方式".format(method)
        # 如果调用创建用户或登录接口，将headers信息写入配置文件
    if "login.mobile" in host or "create_user" in host and res is not None:
        dis4 = re.findall(pat, res.headers["Set-Cookie"])
        if len(dis4) > 1:
            pc.wirte_info(HEADERS, "cookie", "DIS4={}".format(dis4[1]))
            log.info("headers信息写入配置文件成功--->{}".format(dis4[1]))
        else:
            pc.wirte_info(HEADERS, "cookie", "DIS4={}".format(dis4[0]))
            log.info("headers信息写入配置文件成功--->{}".format(dis4[0]))
    return res


def excute_case(case):
    """
    执行用例的方法
    :param case: 单条用例
    :return: 接口执行结果，Response
    """
    global caseId, apiId, apiHost, params, method, headers, relatedApi, relatedParams
    allRelatedApi = []  # 所有关联api的信息
    res = {}
    relatedApi = case[RELATEDAPI]
    if not case:
        log.error("没有可执行的用例")
        return
    if CASEID in case.keys():
        caseId = case[CASEID]
    if APIID in case.keys():
        apiId = case[APIID]
    host = case[APIHOST]

    # 判断接口参数是否有参数化
    if "$" in case[PARMAS]:
        params = case[PARMAS]
    else:
        if PARMAS in case.keys() and case[PARMAS]:
            params = json.loads(case[PARMAS], encoding="utf8")
            # 如果接口中有参数为phone，可能这个接口需要验证码，则调用updata_message初始化t_user_verify表
            if "phone" in params.keys():
                update_message(params["phone"])
        else:
            params = ""
    if METHOD in case.keys():
        method = case[METHOD]
    # 如果调用创建用户接口，不需要headers信息
    if "create_user" in host or "login.mobile" in host:
        headers = None
    else:
        headers = get_headers()
    log.info("此次接口请求的header信息为--->{}".format(headers))
    # 获得关联接口信息
    allRelatedApi = get_all_related_apiinfo(caseId, relatedApi)
    # 如果len(allRelatedApi)>1,说明该接口没有关联接口
    if len(allRelatedApi) > 1:
        apiHeaders = headers
        for i in range(len(allRelatedApi)):
            if i < len(allRelatedApi) - 1:
                a = allRelatedApi[i]  # 当前执行接口
                b = allRelatedApi[i + 1]  # 下一个接口
            else:
                a = allRelatedApi[i]
                b = allRelatedApi[i]
            apiHost = a[APIHOST]
            apiParams = a[PARMAS]
            apiMethod = a[METHOD]
            relatedApiId = a[RELATEDAPI]
            # 当前接口执行结果其实是为了下一个接口的关联参数
            relatedParams = b[RELEATEDPARAMS]
            # 判断是否有多个关联参数，如果有，返回参数集合
            if relatedParams and ";" in relatedParams:
                relatedParams = relatedParams.split(";")
            if 0 != i and apiParams:
                apiParams = string.Template(apiParams)
                apiParams = apiParams.substitute(vars())
                apiParams = json.loads(apiParams, encoding="utf8")
            if apiMethod == "post":
                res = Http.post(apiHost, params=apiParams, headers=apiHeaders)
            elif apiMethod == "get":
                res = Http.get(apiHost, params=apiParams, headers=apiHeaders)
            else:
                log.error("ERRRR:关联接口{}的请求方式为{}，暂不支持{}这种请求方式".format(apiHost, apiMethod, apiMethod))
                return "ERRRR：关联接口{}的请求方式为{}，暂不支持{}这种请求方式".format(apiHost, apiMethod, apiMethod)
            if not isinstance(res, str):
                try:
                    respJson = res.json()
                except:
                    log.error("接口调用出错{}".format(res))
                    respJson = {}
                # 判断relatedParams的数据类型，可能为list和str
                if relatedParams is not None and respJson:
                    if isinstance(relatedParams, str):
                        if relatedParams == HEADERS:
                            apiHeaders = {"cookie": res.headers["Set-Cookie"]}
                        else:
                            var = locals()
                            var[relatedParams] = respJson[relatedParams]
                    elif isinstance(relatedParams, list):
                        for j in relatedParams:
                            if isinstance(j, str):
                                var = locals()
                                var[j] = respJson[j]
                            elif isinstance(j, list):
                                var = locals()
                                var[j[1]] = respJson[j[0]][j[1]]
                            else:
                                log.error("参数错误")
                if "login.mobile" in apiHost or "create_user" in apiHost and res is not None:
                    dis4 = re.findall(pat, res.headers["Set-Cookie"])
                    if isinstance(dis4, list):
                        if len(dis4) > 1:
                            pc.wirte_info(HEADERS, "cookie", "DIS4={}".format(dis4[-1]))
                        else:
                            pc.wirte_info(HEADERS, "cookie", "DIS4={}".format(dis4[0]))
                    elif isinstance(dis4, str):
                        pc.wirte_info(HEADERS, "cookie", "DIS4={}".format(dis4))
                    log.info("headers信息写入配置文件成功--->{}".format(res.headers["Set-Cookie"]))
                # 判断执行的接口是否为当前用例的接口，如果是，则将测试结果中参数化的参数替换为参数化后的参数
                if apiHost == host:
                    return res, apiParams
    else:
        res = request_api(host, params, headers, method)
    return res


# 测试报告模板

def get_report_data(caseID, caseDesciribe, apiHost,
                    apiParams, expect, fact, time="", isPass=PASS, reason="", databaseResutl="", databaseExpect=""):
    result = {}
    result[CASEID] = caseID
    # result[APIID] = apiId
    result[CASEDESCRIBE] = caseDesciribe
    result[APIHOST] = apiHost
    result[PARMAS] = apiParams
    result[EXPECT] = expect
    result[FACT] = fact
    result[DATABASERESUTL] = databaseResutl
    result[DATABASEEXPECT] = databaseExpect
    result[ISPASS] = isPass
    result[TIME] = time
    result[REASON] = reason
    return result


def check(fact, expect, result):
    """
    检查点验证
    :param fact:实际结果
    :param expect: 预期结果
    :param result: 报告模板
    :return:
    """
    if "ERRRR" in fact:
        result[ISPASS] = FAIL
        result[REASON] = fact
        result[TIME] = get_now().strftime(FORMORT)
        return
    if isinstance(fact, tuple):
        result[PARMAS] = json.dumps(fact[-1], ensure_ascii=False)
        fact = fact[0]
    try:
        response = fact.json()
        temp = ""
        if not expect:
            result[ISPASS] = BLOCK
            result[FACT] = fact.text
            result[EXPECT] = " "
            result[TIME] = get_now().strftime(FORMORT)
            result[REASON] = "检查点未设置"
            return
        for key in expect.keys():
            if key not in response.keys():
                result[FACT] = fact.text
                result[ISPASS] = FAIL
                result[TIME] = get_now().strftime(FORMORT)
                result[REASON] = "实际结果中没有{}这个字段,检查用例是否错误或接口返回结果错误".format(key)
                return
            if not isinstance(expect[key], dict):
                # 判断检查点中的字段是否在响应结果中
                # 判断检查点中字段的值和返回结果字段的值是否一致
                if not str(expect[key]).__eq__(str(response[key])):
                    result[FACT] = fact.text
                    result[ISPASS] = FAIL
                    result[TIME] = get_now().strftime(FORMORT)
                    temp += "{}的值预期为：{}，实际为：{}\n".format(key, expect[key], response[key])
                    result[REASON] = temp
                else:
                    # 判断是否有检查点判断失败，如果有，ispass值仍然为fail
                    if result[ISPASS].__eq__(FAIL):
                        result[ISPASS] = FAIL
                    else:
                        result[FACT] = fact.text
                        result[ISPASS] = PASS
                    result[TIME] = get_now().strftime(FORMORT)
            # 判断双重检查点，例如payload.message的形式
            else:
                for key1 in expect[key].keys():
                    if not key1 in response[key].keys():
                        result[FACT] = fact.text
                        result[ISPASS] = FAIL
                        result[TIME] = get_now().strftime(FORMORT)
                        result[REASON] = "实际结果中没有{}:{}这个字段,检查用例是否错误或接口返回结果错误".format(key, key1)
                        return
                    if str(response[key][key1]).__eq__(str(expect[key][key1])):
                        result[FACT] = fact.text
                        result[ISPASS] = PASS
                        result[TIME] = get_now().strftime(FORMORT)
                    else:
                        result[FACT] = fact.text
                        result[ISPASS] = FAIL
                        result[TIME] = get_now().strftime(FORMORT)
                        temp += "{}的值预期为：{}，实际为：{}\n".format(key, expect[key], response[key])
                        result[REASON] = temp
    except Exception as e:
        result[ISPASS] = FAIL
        result[FACT] = ""
        result[TIME] = get_now().strftime(FORMORT)
        result[REASON] = "程序出错：{}".format(str(e))
        log.error(e)
        return


def checkDatabase(databaseExpect, databaseResult, result, fact):
    """
    数据库验证
    :param databaseExpect: 数据库期望
    :param databaseResult: sql执行结果
    :param result: 报告模板
    :param fact: 接口返回实际结果
    :return:
    """
    if databaseExpect:
        result[DATABASEEXPECT] = databaseExpect
    else:
        result[DATABASEEXPECT] = " "
    if not databaseResult:
        result[DATABASERESUTL] = " "
    if result[ISPASS] == "pass":
        if databaseResult is None:
            result[FACT] = fact.text
            result[ISPASS] = BLOCK
            result[TIME] = get_now().strftime(FORMORT)
            result[REASON] = "用例sql语句书写错误"
            return
        if databaseResult is not "" and databaseExpect is "":
            result[ISPASS] = BLOCK
            result[FACT] = fact.text
            result[TIME] = get_now().strftime(FORMORT)
            result[REASON] = "数据库检查点未设置"
            return
        if databaseExpect:
            if int(databaseExpect) == len(databaseResult):
                result[FACT] = fact.text
                result[ISPASS] = PASS
                result[TIME] = get_now().strftime(FORMORT)
            else:
                result[FACT] = fact.text
                result[ISPASS] = FAIL
                result[TIME] = get_now().strftime(FORMORT)
                result[REASON] = "数据库检查失败，预期返回{}条数据，实际返回{}条数据".format(int(databaseExpect),
                                                                      len(databaseResult))


def runAll():
    """
    运行所有用例
    :return:
    """
    # if os.path.exists(report.reportPath) and report.reportPath.c

    # 开始测试之前先清除数据库前一次测试储存的数据
    con.truncate_data(TABLECASE)
    con.truncate_data(TABLERESULT)
    con.truncate_data(TABLEAPIINFO)
    resultSet = []  # 执行结果集
    cases = get_all_case()  # 测试用例集
    start_time = time.time()
    if not cases:
        log.error("用例为空，无匹配格式的.xlsx文件或文件中暂无用例数据")
        return
    log.info("共获取{}条用例".format(len(cases)))
    for case in cases:
        # 将用例存入数据库临时保存
        con.insert_data(TABLECASE, **case)
        # 将接口数据插入数据库apiInfo表中暂时保存
        apiInfo = {APIID: int(case[APIID]), APIHOST: case[APIHOST], PARMAS: case[PARMAS],
                   METHOD: case[METHOD], RELATEDAPI: case[RELATEDAPI], RELEATEDPARAMS: case[RELEATEDPARAMS]}
        # 如果数据库中不存在apiId的接口，则插入
        if not con.query_all(
                "select * from apiInfo  where apiId={}"
                        .format(apiInfo[APIID])):
            con.insert_data(TABLEAPIINFO, **apiInfo)

    for case in cases:
        log.info("正在执行caseId={}的用例".format(case[CASEID]))
        databaseExpect = case[DATABASEEXPECT]
        sqlStatement = case[SQLSTATEMENT]
        # 执行用例
        res = excute_case(case)
        if sqlStatement:
            sqlResult = con_server.query_all(sqlStatement)
        else:
            sqlResult = ""
        # 报告模板
        result = get_report_data(case[CASEID], case[CASEDESCRIBE], case[APIHOST], case[PARMAS],
                                 json.dumps(case[EXPECT], ensure_ascii=False), res, databaseExpect=databaseExpect,
                                 databaseResutl=str(sqlResult))
        # 检查点验证
        check(res, case[EXPECT], result)
        # 数据库验证
        checkDatabase(databaseExpect, sqlResult, result, res)
        # 将执行结果写入数据库临时保存
        con.insert_data(TABLERESULT, **result)
        resultSet.append(result)
    end_time = time.time()
    time_consum = end_time - start_time  # 测试耗时
    case_count = con.query_all(
        "SELECT caseId FROM {}".format(TABLERESULT)
    )  # 执行用例
    fail_case = con.query_all(
        "SELECT caseId FROM {} WHERE ispass='{}'".format(TABLERESULT, FAIL)
    )  # 执行失败的用例
    block_case = con.query_all(
        "SELECT caseId FROM {} WHERE ispass='{}'".format(TABLERESULT, BLOCK)
    )  # 执行阻塞的用例
    success_case = con.query_all(
        "SELECT caseId FROM {} WHERE ispass='{}'".format(TABLERESULT, PASS)
    )  # 执行成功的用例
    if case_count is None:
        case_count = 0
    else:
        case_count = len(case_count)
    if fail_case is None:
        fail_case = 0
    else:
        fail_case = len(fail_case)
    if block_case is None:
        block_case = 0
    else:
        block_case = len(block_case)
    if success_case is None:
        success_case = 0
    else:
        success_case = len(success_case)
    result_info = "本次测试执行完毕，本次测试环境为：{}，共耗时{}秒，共执行用例：{}条，成功：{}条，失败：{}条，阻塞：{}条" \
        .format(test_env,float("%.2f" % time_consum), case_count, success_case, fail_case, block_case)
    log.info(result_info)
    # 将测试结果写入测试报告
    report.set_result_info(result_info)
    report.get_report(resultSet)

    # log.error("{}文件没有关闭".format(report.reportPath))
    # 关闭数据库
    con.close()
    con_server.close()


if __name__ == '__main__':
    runAll()
