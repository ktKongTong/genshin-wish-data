# 角色，元素等静态信息
from re import search, findall, sub
from requests import get
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


# 元素与颜色
def elementColor():
    return {
        "草": "#96cd17",
        "火": "#f38b6f",
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


# if __name__=="__main__":
#     # charList = getRoleInfo()
#     # weaponList = getWeaponInfo()
#     # df = DataFrame(charList)
#     # df2 = DataFrame(weaponList)
#     # df = df.merge(df2,how="outer").fillna("None")
#     # df = df.set_index(['name'])
#     # print(df.index.tolist())
#     # res = df.loc["安柏"]
#     # print(res.to_dict())
#     data = loadDataFromJF("./ysdata.json")
#     df = DataFrame(data["roleData"]["data"])
#     df.drop("uid", axis=1, inplace=True)
#     df.drop("item_id", axis=1, inplace=True)
#     df.drop("lang", axis=1, inplace=True)
#     df.drop("id", axis=1, inplace=True)
#     df['time'] = df['time'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
