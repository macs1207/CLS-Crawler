import json


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
                "content": {}
            }
            self.d = data
            with open(self.failName, "w") as f:
                f.write(json.dumps(data))

    def clear(self):
        with open(self.failName, "w") as f:
            f.seek(0)
            f.truncate()

    def update(self, lstHw):
        self.clear()
        self.d["content"] = lstHw
        with open(self.failName, "w") as f:
            f.write(json.dumps(self.d))

    def failedHash(self):
        return self.d["failed"]

    def getCache(self):
        return self.d["content"]

    def loginFailed(self):
        return self.d["loginFailed"]
