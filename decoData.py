# 对数据进行加工，便于渲染
def decoData(data, name, text):
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