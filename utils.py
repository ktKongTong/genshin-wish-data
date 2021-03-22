import base64
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



def base64encode(fp):
    with open(fp, 'rb') as img_file:
        img_b64encode = base64.b64encode(img_file.read())
        s = img_b64encode.decode()
        res = 'data:image/jpeg;base64,%s' % s
        return res

# def saveToExcel(d,filename):