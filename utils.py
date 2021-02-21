from json import loads,dumps


# 保存数据到json文件中
def saveToJF(d, filename):
    with open('./' + filename + '.json', 'w', encoding="utf-8") as f:
        s = dumps(d, ensure_ascii=False, indent=2)
        s.encode("utf-8")
        f.write(s)


# 从json文件中加载数据
def loadDataFromJF(filename):
    data = {}
    with open(filename, "r", encoding="utf-8") as f:
        data = loads(f.read())
    return data