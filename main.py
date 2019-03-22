# -*- encoding=utf-8
import requests
import hashlib
import time
import json
from mailSender import sendMail


class fileLoad():
    def __init__(self, fileName):
        self.failName = fileName
        try:
            with open(self.failName, "r") as f:
                self.d = json.loads(f.read())
        except IOError:
            data = {
                "loginFailed": "7364cbf35aa828ba6aa5a9334faf4645",
                # This is the page hash when cookies are lost or gone.
                "failed": "a9897117eec5eee62199f4d063824446",
                "content": ""
            }
            self.d = data
            with open(self.failName, "w") as f:
                f.write(json.dumps(data))

    def clear(self):
        with open(self.failName, "w") as f:
            f.seek(0)
            f.truncate()

    def update(self, hash):
        self.clear()
        self.d["content"] = hash
        with open(self.failName, "w") as f:
            f.write(json.dumps(self.d))

    def failedHash(self):
        return self.d["failed"]

    def oldHash(self):
        return self.d["content"]

    def loginFailed(self):
        return self.d["loginFailed"]


def callSend(content):
    info = getInfo()
    bot = info["bot"]
    email = info["email"]
    sendMail(bot, email, content)


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
        if curHash == fileLoad("data.json").loginFailed():
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
    data = fileLoad("data.json")
    oldHash = data.oldHash()
    failedHash = data.failedHash()
    while True:
        r = requests.post(url, data=payLoad, cookies=cookies)
        r.encoding = "utf-8"
        curHash = hashlib.md5(r.text.encode("utf-8")).hexdigest()
        if curHash == failedHash:
            cookies = getCookies()
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "\t", end='')
        if oldHash == curHash:
            print("No news.\tHash: {}".format(oldHash))
        else:
            if oldHash == "":
                print("Insert hash: {}".format(curHash))
            else:
                print("Have news!\tHash: {}".format(curHash))
                callSend("")
            data.update(curHash)
            oldHash = curHash

        time.sleep(300)


if __name__ == "__main__":
    print("Service Start!")
    main()
