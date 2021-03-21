import sys
from datetime import datetime
# from os.path import abspath, dirname
import webview
from pandas import DataFrame
from dealData import GachaData
import base64


class Api():
    def init(self):
        self.gacha = GachaData()
        self.df = self.gacha.totalDF
        # 四星五星list
        self.rank45DF = self.gacha.getRankList()
    # 获取饼图
    def getPieData(self, startTime="2020-09-15 08:00:00", endTime=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                   gachaTypeList=None,rankList=None):
        df = self.df
        df = self.gacha.filterData(df, startTime, endTime, gachaTypeList,rankList)
        data = self.gacha.gachaPie(df)
        response = {'data': data}
        return response

    # 获取词云
    def getWordData(self, startTime="2020-09-15 08:00:00", endTime=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    gachaTypeList=None,rankList=None):
        df = self.df
        df = self.gacha.filterData(df, startTime, endTime, gachaTypeList, rankList)
        data = self.gacha.getDictListForWorldCloud(df)
        response = {'data': data}
        return response

    # 获取条形图
    def getBarData(self, startTime="2020-09-15 08:00:00", endTime=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                   gachaTypeList=None,rankList=None):
        df = self.df
        df = self.gacha.filterData(df, startTime, endTime, gachaTypeList, rankList)
        data = self.gacha.gachaCount(df)
        response = {'data': data}
        return response

    def getTimeLine(self,startTime="2020-09-15 08:00:00", endTime=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                   gachaTypeList=None,rankList=None):
        df = self.rank45DF
        df:DataFrame = self.gacha.filterData(df, startTime, endTime, gachaTypeList, rankList).reset_index(drop=True)
        ave = 0
        if df["count"].astype(int).sum() != 0:
            ave = df["rank_count"].astype(int).sum()/df["count"].astype(int).sum()
        res = df.T.to_dict().values()
        response = {'data': list(res),
                    'ave':'%.4f'%ave}
        return response
    # 获取比率
    def getRateData(self,startTime="2020-09-15 08:00:00", endTime=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                   gachaTypeList=None,rankList=None):
        df = self.df
        df:DataFrame = self.gacha.filterData(df, startTime, endTime, gachaTypeList, rankList)
        rate5,rate4,rate3=0,0,0
        if df["count"].astype(int).sum() != 0:
            rate5 = df.query("rank_type=='5'")["count"].astype(int).sum()/df["count"].astype(int).sum()*100
            rate4 = df.query("rank_type=='4'")["count"].astype(int).sum()/df["count"].astype(int).sum()*100
            rate3 = df.query("rank_type=='3'")["count"].astype(int).sum() / df["count"].astype(int).sum()*100
        totalCount =df["count"].astype(int).sum()
        response = {'rate': ['%.4f'% rate5,'%.4f'% rate4,'%.4f'% rate3],
                    'totalCount':int(totalCount)}
        return response

    def getWorldPic(self,fp='./wordpic.png'):
        resbase64=''
        src=''
        if getattr(sys, 'frozen', None):
            basedir = sys._MEIPASS
        else:
            basedir = "."
        with open(basedir+"/wordpic.png", 'rb') as img_file:
            img_b64encode = base64.b64encode(img_file.read())
            s = img_b64encode.decode()
            resbase64 = 'data:image/jpeg;base64,%s' % s
        with open(basedir+'/origin.png', 'rb') as img_file:
            img_b64encode = base64.b64encode(img_file.read())
            s = img_b64encode.decode()
            src = 'data:image/jpeg;base64,%s' % s
        return {"data": resbase64,
                    "src":src}
    def getState(self):
        title="状态提示"
        message="正在加载数据"
        return {
            "title":title,"message":message
        }
    # def toggleFullscreen(self):
    #     webview.windows[0].toggle_fullscreen()

#


# current_path = abspath(dirname(__file__))
api = Api()

window =webview.create_window('gachaTool', url="index.html", js_api=api, min_size=(1200, 900))
webview.start()
