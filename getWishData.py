from json import loads
from os import path
from re import search
from urllib.parse import urlsplit
from requests import get


# 获取数据
class Data:
    def __init__(self, fp=path.expanduser('~') + "\AppData\LocalLow\miHoYo\原神\output_log.txt"):
        # 日志文件路径
        self.fp = fp
        self.url = self.getURL()
        res = urlsplit(self.url)
        self.authkey = self.splitQuery(res.query)["authkey"]
        self.data = self.getData()

    # 从日志文件中获取url
    def getURL(self):
        urlList = []
        p = r'http(s)?://.+(log)$'
        with open(self.fp, encoding="utf-8") as f:
            for lines in f.readlines():
                a = search(p, lines)
                if a is not None:
                    urlList.append(a.group())
        return urlList[0]

    # url参数切分(获取authkey)
    def splitQuery(self, query: str):
        res = query.split("&")
        queryDict = {}
        for item in res:
            queryDict[item.split("=")[0]] = item.split("=")[1]
        self.authkey = queryDict["authkey"]
        return queryDict

    # ['角色活动', '301'],
    # ['武器活动', '302'],
    # ['常驻', '200'],
    # ['新手', '100']
    # 根据类型，authkey获取原始祈愿数据
    def getDataList(self, authkey, type, name):
        dL = []
        url = "https://hk4e-api.mihoyo.com/event/gacha_info/api/getGachaLog?authkey_ver=1&lang=zh-cn&authkey=" + authkey + "&size=6&gacha_type=" + type
        endId = "0"
        page = 1
        hasData = True
        while hasData:
            tmpurl = url + "&page=" + str(page) + "&end_id=" + str(endId)
            # print(tmpurl)
            resp = get(tmpurl).content.decode(encoding="utf-8")
            r = loads(resp)
            dataList = r["data"]["list"]
            if len(dataList) == 0 or len(dataList)<6:
                hasData = False
            else:
                endId = dataList[-1]['id']
            print(name + "第" + str(page) + "页,获取完毕")
            page = page + 1
            for item in r["data"]["list"]:
                dL.append(item)
        return dL

    # 获取全部json数据
    def getData(self):
        authkey = self.authkey
        normData = self.getDataList(authkey, "200", "常驻祈愿")
        xsData = self.getDataList(authkey, "100", "新手祈愿")
        weaponData = self.getDataList(authkey, "302", "武器活动祈愿")
        roleData = self.getDataList(authkey, "301", "角色活动祈愿")
        data = {"normData": {"name": "normData", "text": "常驻祈愿", "data": normData},
                "weaponData": {"name": "weaponData", "text": "武器活动祈愿", "data": weaponData},
                "roleData": {"name": "roleData", "text": "角色活动祈愿", "data": roleData},
                "xsData": {"name": "xsData", "text": "新手祈愿", "data": xsData}
                }
        return data

    # def getDataNew(self):
    #     authkey = self.authkey
    #     normData = self.getDataList(authkey, "200", "常驻祈愿")
    #     xsData = self.getDataList(authkey, "100", "新手祈愿")
    #     weaponData = self.getDataList(authkey, "302", "武器活动祈愿")
    #     roleData = self.getDataList(authkey, "301", "角色活动祈愿")
    #     data = {"normData": {"name": "normData", "text": "常驻祈愿", "data": normData},
    #             "weaponData": {"name": "weaponData", "text": "武器活动祈愿", "data": weaponData},
    #             "roleData": {"name": "roleData", "text": "角色活动祈愿", "data": roleData},
    #             "xsData": {"name": "xsData", "text": "新手祈愿", "data": xsData}
    #             }
# if __name__=="__main__":
#     d = Data()
#     print(d.data)

