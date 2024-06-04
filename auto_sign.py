# https://github.com/lyk0803/liantong/blob/master/sign.py
# 联通每日签到
import os
import re
from time import sleep
import datetime
import requests
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
import base64
from requests import post

from email.mime.text import MIMEText
from email.header import Header
from smtplib import SMTP_SSL

# 此处改为自己的配置 手机号, 密码, appId
pid = "1f7af72ad6912d306b5053abf90c7ebb356bab253596c9c254729ca49f37de962553ae681182622b4658d917b5cfd62357cca9d8311495f28dfd5bb08b845e6d3474ac89a77f47af4e26dee8fc036812"


class UnicomSign:
    def __init__(self):
        self.UA = None
        self.VERSION = "8.0200"
        self.request = requests.Session()
        self.pid = pid
        self.result = ""  # 签到结果

    # 加密算法
    def rsa_encrypt(self, str):
        # 公钥
        publickey = """-----BEGIN PUBLIC KEY-----
        MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDc+CZK9bBA9IU+gZUOc6
        FUGu7yO9WpTNB0PzmgFBh96Mg1WrovD1oqZ+eIF4LjvxKXGOdI79JRdve9
        NPhQo07+uqGQgE4imwNnRx7PFtCRryiIEcUoavuNtuRVoBAm6qdB0Srctg
        aqGfLgKvZHOnwTjyNqjBUxzMeQlEC2czEMSwIDAQAB
        -----END PUBLIC KEY-----"""
        rsakey = RSA.importKey(publickey)
        cipher = Cipher_pkcs1_v1_5.new(rsakey)
        cipher_text = base64.b64encode(cipher.encrypt(str.encode("utf-8")))
        return cipher_text.decode("utf-8")

    # 用户登录
    def login(self, mobile, passwd):
        self.UA = (
            "Mozilla/5.0 (Linux; Android 9; MI 6 Build/PKQ1.190118.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/80.0.3987.99 Mobile Safari/537.36; unicom{version:android@"
            + self.VERSION
            + ",desmobile:"
            + mobile
            + "};devicetype{deviceBrand:Xiaomi,deviceModel:MI 6};{yw_code:}"
        )
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        headers = {
            "Host": "m.client.10010.com",
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded",
            "Connection": "keep-alive",
            "Cookie": "devicedId=20be54b981ba4188a797f705d77842d6",
            "User-Agent": self.UA,
            "Accept-Language": "zh-cn",
            "Accept-Encoding": "gzip",
            "Content-Length": "1446",
        }
        login_url = "https://m.client.10010.com/mobileService/login.htm"
        login_data = {
            "deviceOS": "android9",
            "mobile": self.rsa_encrypt(mobile),
            "netWay": "Wifi",
            "deviceCode": "20be54b981ba4188a797f705d77842d6",
            "isRemberPwd": "true",
            "version": "android@" + self.VERSION,
            "deviceId": "20be54b981ba4188a797f705d77842d6",
            "password": self.rsa_encrypt(passwd),
            "keyVersion": 1,
            "provinceChanel": "general",
            "appId": self.pid,
            "deviceModel": "MI 6",
            "deviceBrand": "Xiaomi",
            "timestamp": timestamp,
        }

        try:
            res1 = self.request.post(login_url, data=login_data, headers=headers)
            if res1.status_code == 200:
                print(">>>获取登录状态成功！")

            else:
                print(">>>获取登录状态失败！")
        except Exception as e:
            print(">>>登录失败！！！")
            self.result = "登录失败！！！"

        sleep(3)

    # 每日签到
    def daysign(self):
        headers = {
            "user-agent": self.UA,
            "referer": "https://img.client.10010.com",
            "origin": "https://img.client.10010.com",
        }

        try:
            res1 = self.request.post(
                "https://act.10010.com/SigninApp/signin/getContinuous", headers=headers
            )
            sleep(3)
            if res1.json()["data"]["todaySigned"] == "1":
                res2 = self.request.post(
                    "https://act.10010.com/SigninApp/signin/daySign", headers=headers
                )

                print(">>>签到成功！")
                self.result = "签到成功！"
            else:
                print(">>>今天已签到！")
                self.result = "今天已签到！"

        except Exception as e:
            print(">>>签到失败！！！")
            self.result = "失败！！！"

    # 发邮件提醒结果
    def sendmail(self, mail_addr, pwd):
        # qq邮箱smtp服务器
        host_server = "smtp.qq.com"
        # 邮件的正文内容
        mail_content = self.result
        # 邮件标题
        mail_title = "联通每日签到结果：" + self.result

        # ssl登录
        smtp = SMTP_SSL(host_server)
        # set_debuglevel()是用来调试的。参数值为1表示开启调试模式，参数值为0关闭调试模式
        smtp.set_debuglevel(1)
        smtp.ehlo(host_server)
        smtp.login(mail_addr, pwd)

        msg = MIMEText(mail_content, "plain", "utf-8")
        msg["Subject"] = Header(mail_title, "utf-8")
        msg["From"] = mail_addr
        msg["To"] = mail_addr
        smtp.sendmail(mail_addr, mail_addr, msg.as_string())
        smtp.quit()


if __name__ == "__main__":
    phone = os.environ["PHONE"]
    phone_pwd = os.environ["PHONE_PWD"]
    mail = os.environ["MAIL"]
    mail_pwd = os.environ["MAIL_PWD"]

    user = UnicomSign()
    user.login(phone, phone_pwd)  # 用户登录   这里需要更改
    user.daysign()  # 日常签到
    user.sendmail(mail, mail_pwd)
