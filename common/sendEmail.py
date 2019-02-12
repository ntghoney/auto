# -*- coding: utf-8 -*-
'''
@File  : sendEmail.py
@Date  : 2019/1/15/015 17:32
'''
import smtplib
from email.mime.text import MIMEText
from email.header import Header
class SendEmail(object):
    def __init__(self):
        self.stmp = smtplib.SMTP("smtp.qq.com")
        self.msg = None

    def set_msg(self, text):
        message = MIMEText(text, 'plain', 'utf-8')
        message['From'] = Header("测试", 'utf-8')  # 发送者
        message['To'] = Header("测试", 'utf-8')  # 接收者
        subject = 'Python SMTP 邮件测试'
        message['Subject'] = Header(subject, 'utf-8')
        self.msg=message

    def send_email(self, sender, recivers):
        self.stmp.login("740207942@qq.com", "gvbvpqbosvrybcic")
        self.stmp.sendmail(sender, recivers, self.msg.as_string())


if __name__ == '__main__':
    sender = '740207942@qq.com'
    receivers = ['2395027402@qq.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
    se=SendEmail()
    se.set_msg("哈哈哈哈哈哈，臭女人")
    se.send_email(sender,receivers)
