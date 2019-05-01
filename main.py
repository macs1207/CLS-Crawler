# -*- encoding=utf-8
import requests
import hashlib
import time
import json
import logging
import re
from lxml import etree
from Module.MailSender import sendMail
from Module import FileProcess


def callSend(content):
    info = getInfo()
    bot = info["bot"]
    email = info["email"]
    sendMail(bot, email, content)


def getHwList(text):
    root = etree.HTML(text)
    lastHw = {"value": 0}
    for i in range(2, 4):
        targets = root.xpath(
            "//div[@class='news_{}']//table//tr".format(i))
        for target in targets:
            try:
                a = target.xpath("td")
                match = re.search(r'(?P<value>\d+)', a[0].text)
                # Get the newest hw.
                if int(match.groupdict()["value"]) > lastHw["value"]:
                    lastHw = {"value": int(match.groupdict()["value"]),
                              "title": a[1].text,
                              "deadline": a[3].text}
            except IndexError:
                continue
    return lastHw


def confIpt(bot, config):
    account = input("Username: ")
    password = input("Password: ")
    email = input("Your email: ")
    if bot:
        botEmail = input("Bot email: ")
        botPwd = input("Bot Password: ")
        config = {
            "user": {
                "school_id": "24",  # KUAS id
                "account": account,
                "password": password
            },
            "email": email,
            "bot": {
                "email": botEmail,
                "password": botPwd
            }
        }
    else:
        config["user"]["account"] = account
        config["user"]["password"] = password
        config["email"] = email
    with open("config.json", "w") as f:
        f.seek(0)
        f.truncate()
        f.write(json.dumps(config))
    return config


def getInfo():
    try:
        with open("config.json", "r") as f:
            config = json.loads(f.read())
    except IOError:
        config = confIpt(True, {})
    return config


def getCookies():
    while True:
        url = "http://cls.kuas.edu.tw/home/login"
        payLoad = getInfo()
        r = requests.post(url, data=payLoad["user"])
        r.encoding = "utf-8"
        curHash = hashlib.md5(r.text.encode("utf-8")).hexdigest()
        if curHash == FileProcess.fileLoad("data.json").loginFailed():
            print("Login Failed! Input your info again.")
            confIpt(False, payLoad)
        else:
            break
    rcvCookie = {"ci_session": r.cookies["ci_session"]}
    return rcvCookie


def main():
    url = "http://cls.kuas.edu.tw/admin/managehomework/uploadhw"
    payLoad = {"course_id": 73625}
    cookies = getCookies()
    data = FileProcess.fileLoad("data.json")
    failedHash = data.failedHash()
    while True:
        # Fetch the informamtion of cls every five minutes.
        r = requests.post(url, data=payLoad, cookies=cookies)
        r.encoding = "utf-8"
        curHash = hashlib.md5(r.text.encode("utf-8")).hexdigest()
        cache = data.getCache()
        if curHash == failedHash:
            # Request with new cookie.
            cookies = getCookies()
            logging.warning("Cookies are refreshed!")
            continue
        lstHw = getHwList(r.text)
        logMsg = "\tHW{}: {}\tHash: {}".format(
            lstHw["value"], lstHw["title"], curHash)
        if cache == {}:
            logging.warning("Initial." + logMsg)
            data.update(lstHw)
        else:
            if lstHw["value"] == cache["value"]:
                # If cls doesn't update.
                logging.warning("No news." + logMsg)
            else:
                # If cls update.
                logging.warning("Have news!" + logMsg)
                callSend(time.strftime("YYYY-MM-DD HH:mm:SS", time.localtime())
                         + "Have news!" + logMsg)
                data.update(lstHw)
        time.sleep(300)


if __name__ == "__main__":
    logging.basicConfig(filename="log",
                        datefmt="%y-%m-%d %H:%M:%S",
                        format="%(asctime)s  %(levelname)s: %(message)s")
    print("Service Start!")
    main()
