from re import search, findall, sub
from urllib.parse import urlsplit
from requests import get
from json import loads, dumps
from os import path
from jinja2 import Template
from traceback import format_exc
import sys


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
        page = 1
        hasData = True
        while hasData:
            tmpurl = url + "&page=" + str(page)
            resp = get(tmpurl).content.decode(encoding="utf-8")
            print("正在获取" + name + ",第" + str(page) + "页")
            page = page + 1
            r = loads(resp)
            dataList = r["data"]["list"]
            for item in r["data"]["list"]:
                dL.append(item)
            if len(dataList) == 0:
                hasData = False
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


# 对数据进行加工，便于渲染
def anyData(data, name, text):
    data.reverse()
    timeList, nameList, itemTypeList, rankTypeList, rank5WeaponList, rank5RoleList, rank5List = [], [], [], [], [], [], []
    weapon3Count, weapon4Count, role4Count, weapon5Count, role5Count = 0, 0, 0, 0, 0
    # 五星计数器
    count5 = 1
    for item in data:
        timeList.append(item["time"])
        nameList.append(item["name"])
        itemTypeList.append(item["item_type"])
        rankTypeList.append(item["rank_type"])
        if item["rank_type"] == "5":
            item["count5"] = str(count5)
            count5 = 1
            rank5List.append(item)
            if item["item_type"] == "武器":
                weapon5Count = weapon5Count + 1
                rank5WeaponList.append(item)
            elif item["item_type"] == "角色":
                rank5RoleList.append(item)
                role5Count = role5Count + 1
        elif item["rank_type"] == "4":
            count5 += 1
            if item["item_type"] == "武器":
                weapon4Count = weapon4Count + 1
            else:
                role4Count = role4Count + 1
        elif item["rank_type"] == "3":
            count5 += 1
            weapon3Count = weapon3Count + 1
    labelsList = ['3星武器', '4星武器', '4星角色', '5星武器', '5星角色']
    dataList = [weapon3Count, weapon4Count, role4Count, weapon5Count, role5Count]
    #
    labels, data, total = [], [], 0
    for i in range(len(dataList)):
        if dataList[i] > 0:
            total = dataList[i] + total
            labels.append(labelsList[i])
            data.append(dataList[i])
    d = dict()
    rank5List.reverse()
    d["values"] = data
    d["no5"] = count5 - 1
    d["labels"] = labels
    d["timeList"] = timeList
    d["nameList"] = nameList
    d['itemTypeList'] = itemTypeList
    d["rankTypeList"] = rankTypeList
    d["rank4RoleCount"] = role4Count
    d["rank4WeaponCount"] = weapon4Count
    d["rank3WeaponCount"] = weapon3Count
    d["rank5RoleList"] = rank5RoleList
    d["rank5WeaponList"] = rank5WeaponList
    d["rank5List"] = rank5List
    # 饼图数据
    series = dict()
    series["name"] = "Brands"
    series["data"] = []
    for i in range(len(labels)):
        series["data"].append({"name": labels[i], "y": int(data[i]) / total, "values": int(data[i])})
    d["total"] = total
    d["series"] = [series]
    d["name"] = name
    d["text"] = text
    return d


# 保存数据到json文件中
def saveToJF(d, filename):
    with open('./' + filename + '.json', 'w', encoding="utf-8") as f:
        s = dumps(d, ensure_ascii=False, indent=2)
        s.encode("utf-8")
        f.write(s)


# 从json文件中加载数据
def loadDataFromJF(filename):
    data = {}
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = loads(f.read())
    except:
        print("似乎读取json文件有点问题")
        input("按任意键退出.....")
        exit()
    return data


# 角色，元素等静态信息
def staticData():
    d = {
        "elementColor": elementColor(),
        "charAndWeaponData": {}
    }
    RoleAndWeaponInfoList = getWeaponInfo() + getRoleInfo()
    for item in RoleAndWeaponInfoList:
        d["charAndWeaponData"][item["name"]] = item
    return d


# 元素与颜色对应
def elementColor():
    return {
        "草": "#96cd17",
        "火": "#e36651",
        "水": "#0ac4df",
        "雷": "#c689fc",
        "冰": "#b7fbfe",
        "岩": "#f7e595",
        "风": "#4dcda7",
    }


# 从米游社观测枢抓取武器信息
def getWeaponInfo():
    html = get("https://bbs.mihoyo.com/ys/obc/content/640/detail?bbs_presentation_style=no_header")
    res = search('<tbody data-filter="main.data" class="obc-tmpl__filter-target">.+</tbody>', html.text).group()
    t = findall("<tr.+?>.+?</tr>", res)
    weaponList = []
    # 武器类型 - 单手剑
    # 武器星级 - 三星
    # 属性加成 - 暴击伤害
    # 获取途径 - 祈愿
    for s in t:
        item = findall("<td.+?>.+?</td>", s)
        info = search('".+?"', s).group()
        info = info.strip('"').split(" ")
        info = [item.split("-")[1] for item in info]
        affix = search('[\u2E80-\u9FFF].*[\u2E80-\u9FFF]?', item[3]).group()

        #
        if info[1] == "五星" or info[1] == "四星":
            weaponList.append({
                "name": search('([\u2E80-\u9FFF]+)', item[0]).group(),
                "avatar": search('https?://.+?\.png', item[0]).group(),
                "markupType": info[2],
                "weaponType": info[0],
                "affix": sub("<.+?>", "", affix),
                "type": "武器"
            })
    return weaponList


# 从米游社观测枢抓取角色信息
def getRoleInfo():
    html = get("https://bbs.mihoyo.com/ys/obc/content/90/detail?bbs_presentation_style=no_header")
    res = search('<tbody data-filter="main.data" class="obc-tmpl__filter-target">.+</tbody>', html.text).group()
    t = findall("<tr.+?>.+?</tr>", res)
    charList = []
    for s in t:
        item = findall("<td.+?>.+?</td>", s)
        charList.append({
            "name": search('([\u2E80-\u9FFF]+)', item[0]).group(),
            "avatar": search('https?://.+?\.png', item[0]).group(),
            "elemType": search('([\u2E80-\u9FFF]+)', item[1]).group(),
            "atkType": search('([\u2E80-\u9FFF]+)', item[2]).group(),
            "weaponType": search('([\u2E80-\u9FFF]+)', item[3]).group(),
            "type": "角色"
        })
    return charList


# 渲染HTML
def renderHTML(data):
    data = [anyData(item["data"], item["name"], item["text"]) for item in data]
    if getattr(sys, 'frozen', None):
        basedir = sys._MEIPASS
    else:
        basedir = "."
    with open(basedir + "/charts.html", "r", encoding='utf-8') as f:
        t = f.read()
        template = Template(t)
        ret = template.render(data=data, staticdata=staticData())
    with open("ysdata.html", "w", encoding="utf-8") as f:
        f.write(ret)


def run(name="ysdata"):
    if len(sys.argv) > 1:
        fp = sys.argv[1]
        d = Data(fp)
    else:
        d = Data()
    data = list(d.data.values())
    saveToJF(d.data, name)
    renderHTML(data)


try:
    run()
except Exception as e:
    with open("ysWishData.log","w") as f:
        f.write(format_exc())
