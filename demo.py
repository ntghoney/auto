# -*- coding: utf-8 -*-
'''
@File  : demo.py
@Date  : 2019/1/15/015 16:18
'''
from configparser import ConfigParser
import os
import json
import pytest_html



import requests
headers={"cookie":'DIS4=f3002ea4638a4b8b902b4da0a9c882b8; Expires=Wed, 22-Jan-2020 03:11:05 GMT; Max-Age=31536000; Path=/, lu=26; Expires=Wed, 22-Jan-2020 03:11:05 GMT; Max-Age=31536000; Path=/, ln=1; Expires=Wed, 22-Jan-2020 03:11:05 GMT; Max-Age=31536000; Path=/',
         # "User-Agent":"Mozilla/5.0 (iPhone; CPU iPhone OS 12_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16B92 version=2.0.2018101201 bid=com.he.ar",
         # "Accept":"application/json"
         }
url="http://fp02.ops.gaoshou.me/s4/login.mobile"
url1="http://fp02.ops.gaoshou.me/s4/dashboard"
url2="http://fp02.ops.gaoshou.me/s5/create_user"
url3="http://fp02.ops.gaoshou.me/s4/bindMobile"
url4="http://fp01.ops.gaoshou.me/a/5.0/bindMobile.occupied"
url5="http://fp02.ops.gaoshou.me/s4/users.accounts.getDetail"

data={"phone":"17711794026","code":"4883"}
data3={"phone":"17711794252","code":"123456"}
h={'Server': 'nginx', 'Date': 'Tue, 22 Jan 2019 03:11:05 GMT', 'Content-Type': 'application/json', 'Transfer-Encoding': 'chunked', 'Connection': 'keep-alive', 'Vary': 'Accept-Encoding', 'cookie': 'DIS4=c569c211fe8546fcb201cc934af7dc64; Expires=Thu, 23-Jan-2020 05:56:00 GMT; Max-Age=31536000; Path=/; Expires=Wed, 22-Jan-2020 03:11:05 GMT; Max-Age=31536000; Path=/, lu=26; Expires=Wed, 22-Jan-2020 03:11:05 GMT; Max-Age=31536000; Path=/, ln=1; Expires=Wed, 22-Jan-2020 03:11:05 GMT; Max-Age=31536000; Path=/', 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Credentials': 'true', 'X-Diablo-Revision': 'cd7ee62', 'X-Hebe-Host': 'h1571', 'X-Qk-Lb-Overloading-Level': '0', 'Content-Encoding': 'gzip'}
a={"cookie":"DIS4=e47adf7295bb40b39fbfcd06e2904011"}
data11={}
# print(s4.headers)
# s5=requests.post(url3,data=data3,headers=headers)
# print(s5.text)
# print(s4.headers)
#Set-Cookie
#DIS4=8ab9c1277d2141148369de04857578b7

h1={"Set-Cookie":"DIS4=2c4867920f3e4bf2b08a5297c7bc7ed6"}
# s1=requests.post(url2)
#cookie-------------------------->DIS4=b449e073554343e699448eeb7b630d06; Expires=Tue, 28-Jan-2020 09:46:18 GMT; Max-Age=31536000; Path=/, DIS4=2c4867920f3e4bf2b08a5297c7bc7ed6; Expires=Tue, 28-Jan-2020 09:46:18 GMT; Max-Age=31536000; Path=/, lu=312; Expires=Tue, 28-Jan-2020 09:46:18 GMT; Max-Age=31536000; Path=/, mu=; Expires=Thu, 01-Jan-1970 00:00:00 GMT; Path=/, ln=1; Expires=Tue, 28-Jan-2020 09:46:18 GMT; Max-Age=31536000; Path=/

# s2=requests.post(url3,data=data,headers=hh)
s3=requests.post(url,data=data)
print(s3.headers["Set-Cookie"])
# print("s3 headers---------->%s" %s3.headers)
# print("cookie-------------------------->%s" %s3.headers["Set-Cookie"])
# hh={"cookie":s3.headers["Set-Cookie"],"X-Hebe-Host":"h1571", 'X-Diablo-Revision':"1ff8c9c"}
# print("hh------------------>%s" %h1)
# hhhh={'cookie': '741b5ebd73d7442aa7416626efde3bb8'}
# s4=requests.get(url1,headers=a)
# print(s4.text)

# if "headers" not in cf.sections():
#     cf.add_section("headers")
# cf.set("headers","headers",h)
# with open("e:/project/ApiTest/config/conf.ini","w") as f:
#     cf.write(f)
#     f.close()
# cf.remove_option("headers","headers")
# with open("e:/project/ApiTest/config/conf.ini","w") as f:
#     cf.write(f)
#     f.close()

