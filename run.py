# -*- coding: utf-8 -*-
'''
@File  : run.py
@Date  : 2019/1/15/015 18:45
'''
from common.handleCase import HandleCase
from common.report import Report
from common.httputils import Http
import time
from common.conDatabase import ConMysql, get_base_info
from common.log import Log
from common.report import get_now
import json
from common.parseConfig import ParseConfig, setPath
import string
import logging

log = Log().getLog()
pc = ParseConfig()
server_database = get_base_info(pc.get_info("ServerDatabase"))
con_server = ConMysql(server_database)  # 服务器数据库链接
con = ConMysql()  # 本地数据库连接对象


def write_headers(headers):
    pc.wirte_info("headers", "headers", headers)


# 从配置文件中获得默认headers
def get_default_headers():
    headers = {"cookie": pc.get_info("headers")["headers"]}
    return headers


# 参数化赋值，参数分别为参数化的参数以及赋值的json字符串
def parameterize(mparams, mJson):
    print(mparams, mJson)
    if mparams and mJson:
        for i in mparams:
            if isinstance(i, str):
                var = locals()
                var[i] = mJson[i]
            elif isinstance(i, list):
                var = locals()
                var[i[1]] = mJson[i[0]][i[1]]
            else:
                log.error("参数错误")

# 检查期望与实际是否相匹配
def check(expect, fact, result, databaseResult="", databaseExpect=""):
    # 默认结果为pass
    result["ispass"] = "pass"
    # if fact.status_code == 200:
    try:
        response = fact.json()
        # 循环检查点与响应结果是否匹配
        temp = ""
        if not expect:
            result["ispass"] = "block"
            result["time"] = get_now().strftime("%Y/%m/%d %H:%M:%S")
            result["reason"] = "检查点未设置"
            return
        if databaseResult and not databaseExpect:
            result["ispass"] = "block"
            result["time"] = get_now().strftime("%Y/%m/%d %H:%M:%S")
            result["reason"] = "数据库检查点未设置"
            return
        if databaseExpect:
            if int(databaseExpect) == len(databaseResult):
                result["ispass"] = "pass"
                result["time"] = get_now().strftime("%Y/%m/%d %H:%M:%S")
            else:
                result["ispass"] = "fail"
                result["time"] = get_now().strftime("%Y/%m/%d %H:%M:%S")
                result["reason"] = "数据库检查失败，预期返回{}条数据，实际返回{}条数据".format(int(databaseExpect), len(databaseResult))

        for key in expect.keys():
            if not isinstance(expect[key], dict):
                # 判断检查点中的字段是否在响应结果中
                if key not in response.keys():
                    result["ispass"] = "fail"
                    result["time"] = get_now().strftime("%Y/%m/%d %H:%M:%S")
                    result["reason"] = "实际结果中没有{}这个字段,检查用例是否错误或接口返回结果错误".format(key)
                    return
                # 判断检查点中字段的值和返回结果字段的值是否一致
                if not str(expect[key]).__eq__(str(response[key])):
                    result["ispass"] = "fail"
                    result["time"] = get_now().strftime("%Y/%m/%d %H:%M:%S")
                    temp += "{}的值预期为：{}，实际为：{}\n".format(key, expect[key], response[key])
                    result["reason"] = temp
                else:
                    # 判断是否有检查点判断失败，如果有，ispass值仍然为fail
                    if result["ispass"].__eq__("fail"):
                        result["ispass"] = "fail"
                    else:
                        result["ispass"] = "pass"
                    result["time"] = get_now().strftime("%Y/%m/%d %H:%M:%S")
            # 判断双重检查点，例如payload.message的形式
            else:
                for key1 in expect[key].keys:
                    if str(response[key][key1]).__eq__(str(expect[key][key1])):
                        result["ispass"] = "fail"
                        result["time"] = get_now().strftime("%Y/%m/%d %H:%M:%S")
                        temp += "{}的值预期为：{}，实际为：{}\n".format(key, expect[key], response[key])
                        result["reason"] = temp
                    else:
                        result["ispass"] = "pass"
                        result["time"] = get_now().strftime("%Y/%m/%d %H:%M:%S")
    except Exception as e:
        result["ispass"] = "fail"
        result["time"] = get_now().strftime("%Y/%m/%d %H:%M:%S")
        result["reason"] = "程序出错：{}".format(str(e))
    return result


def run():
    global cid, describe, host, method, params, checkPints, con, relatedApi, relatedParams, apiInfo, sqlStatement, databaseExpect, sqlResult

    '''
    是否为第一条用例，每次执行是获取第一条用例执行的headers信息写入配置文件
    之后接口测试用例中如果headers信息为空，则自动调用配置文件中的headers信息
    '''
    defaultHeaders = get_default_headers()  # 头信息
    # 开始测试之前先清除数据库前一次测试储存的数据
    con.truncate_data("testCase")
    con.truncate_data("testResult")
    con.truncate_data("apiInfo")
    # 测试结果集
    resultSet = []
    start_time = time.time()
    # 获取所有用例
    cases = HandleCase().get_cases()
    for case in cases:

        # 将用例存入数据库临时保存
        con.insert_data("testcase", **case)
        # 将接口数据插入数据库apiInfo表中暂时保存
        apiInfo = {"apiId": int(case["apiId"]), "apiHost": case["apiHost"], "apiParams": case["apiParams"],
                   "method": case["method"], "relatedApi": case["relatedApi"], "relatedParams": case["relatedParams"]}
        # 如果数据库中不存在apiId的接口，则插入
        if not con.query_all("select * from apiInfo  where apiId={}".format(apiInfo["apiId"])):
            con.insert_data("apiInfo", **apiInfo)

    for case in cases:
        allRelatedApi = []  # 所有关联api的信息
        result = {}
        relatedApi = case["relatedApi"]
        # relatedParams = case["relatedParams"]
        cid = case["caseId"]
        log.info("正在执行第{}条用例".format(cid))
        describe = str(case["caseDescribe"])
        host = str(case["apiHost"])
        checkPints = case["expect"]
        method = str(case["method"])
        params = str(case["apiParams"])
        headers = case["apiHeaders"]
        sqlStatement = str(case["sqlStatement"])
        databaseExpect = case["databaseExpect"]
        result["caseId"] = cid
        caseApi = con.query_one("select * from apiInfo where apiId={}".format(cid))  # 用例对应的api信息
        allRelatedApi.append(caseApi)
        result["caseDescribe"] = describe
        result["apiHost"] = host
        # 如果用例中headers信息没写，则调用配置文件中的headers信息
        if headers:
            headers = json.loads(headers, encoding="utf8")
        else:
            if host != "/s5/create_user":
                headers = defaultHeaders
            else:
                headers = ""
        if databaseExpect:
            result["databaseExpect"] = databaseExpect
        else:
            result["databaseExpect"] = " "
        if sqlStatement:
            sqlResult = con_server.query_all(sqlStatement)
        else:
            sqlResult = ""
        if sqlResult:
            result["databaseResult"] = str(sqlResult)
        else:
            result["databaseResult"] = " "
        if checkPints:
            result["expect"] = str(checkPints)
        else:
            result["expect"] = ""
        # 先获得用例执行时相关联的接口信息
        while True:
            if relatedApi is not None:
                relatedApiInfo = con.query_one("select * from apiInfo where apiId={}".format(relatedApi))
                relatedApi = relatedApiInfo["relatedApi"]
                allRelatedApi.append(relatedApiInfo)
                allRelatedApi.reverse()
            else:
                break
        if allRelatedApi:
            apiHeaders=headers
            for i in range(len(allRelatedApi)):
                if i < len(allRelatedApi) - 1:
                    a = allRelatedApi[i]  # 当前执行
                    b = allRelatedApi[i + 1]  # 下一个
                else:
                    a = allRelatedApi[i]
                    b = allRelatedApi[i]
                apiHost = a["apiHost"]
                apiParams = a["apiParams"]
                apiMethod = a["method"]
                relatedParams = b["relatedParams"]
                if relatedParams and ";" in relatedParams:
                    relatedParams = relatedParams.split(";")
                relatedApiId = a["relatedApi"]
                if 0 != i and apiParams:
                    # apiParams = json.loads(str(apiParams), encoding="utf8")
                    apiParams = string.Template(apiParams)
                    apiParams = apiParams.substitute(vars())
                    result["apiParams"] = apiParams
                    params = json.loads(apiParams, encoding="utf8")
                if apiMethod == "post":
                    resp = Http.post(apiHost, apiParams, headers=apiHeaders)
                else:
                    resp = Http.get(apiHost, params=apiParams, headers=apiHeaders)
                try:
                    respJson = resp.json()
                except:
                    log.error("接口调用出错{}".format(resp))
                    respJson = {}
                # 判断relatedParams的数据类型，可能为list和str
                if relatedParams is not None and respJson:
                    if isinstance(relatedParams, str):
                        if relatedParams == "headers":
                            apiHeaders={"cookie": resp.headers["Set-Cookie"]}
                    elif isinstance(relatedParams, list):
                        for i in relatedParams:
                            if isinstance(i, str):
                                var = locals()
                                var[i] = respJson[i]
                            elif isinstance(i, list):
                                var = locals()
                                var[i[1]] = respJson[i[0]][i[1]]
                            else:
                                log.error("参数错误")
                if apiHost == host:
                    result["fact"] = resp.text
                    check(expect=checkPints, fact=resp, result=result, databaseExpect=databaseExpect,
                          databaseResult=sqlResult)
                    # 如果调用了creat_user的接口，就将接口的headers信息写入配置文件
                    if host == "/s5/create_user" or host == "/s4/login.mobile":
                        write_headers((str(resp.headers["Set-Cookie"])))

        # 将执行结果写入数据库临时保存
        con.insert_data("testResult", **result)
        resultSet.append(result)
    end_time = time.time()
    time_consum = end_time - start_time  # 测试耗时
    case_count = con.query_all("SELECT caseId FROM testresult")  # 执行用例
    fail_case = con.query_all("SELECT caseId FROM testresult WHERE ispass='fail'")  # 执行失败的用例
    block_case = con.query_all("SELECT caseId FROM testresult WHERE ispass='block'")  # 执行阻塞的用例
    success_case = con.query_all("SELECT caseId FROM testresult WHERE ispass='pass'")  # 执行成功的用例
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
    result_info = "本次测试执行完毕，共耗时{}秒，共执行用例：{}条，成功：{}条，失败：{}条，阻塞：{}条".format(float("%.2f" % time_consum), case_count,

                                                                          success_case, fail_case, block_case)
    log.info(result_info)
    # 将测试结果写入测试报告
    report = Report()
    report.set_result_info(result_info)
    report.get_report(resultSet)
    # 关闭数据库
    con.close()
    con_server.close()


if __name__ == '__main__':
    # data = {"phone": "17711794059", "code": "123456"}
    # s = Http.post("/s5/login.mobile", params=data)
    #
    # print(type(s.json()))
    #
    # s = HandleCase().get_cases()[0]
    # c = dict(s["expect"])
    # for key in c.keys():
    #
    #     nt(key)
    # s = "是dfdsfds发的规范的施工的双方各地方个的双方各得十分个收到"
    run()
