import sys
from traceback import format_exc
from jinja2 import Template
from decoData import decoData
from getStaticData import staticData
from getWishData import Data
from utils import saveToJF

# 渲染HTML
def renderHTML(data):
    data = [decoData(item["data"], item["name"], item["text"]) for item in data]
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
    print(format_exc())
    print("哦,是Error,如果你愿意的话，可以用上述信息百度，有助于问题解决，也可在GitHub反馈给开发者")
    input("按回车键关闭...")