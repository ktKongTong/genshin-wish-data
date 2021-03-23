import sys
from datetime import datetime
import webview
from dealData import GachaData
from getWishData import State, setState
from utils import base64encode


class Api():
    def init(self,isLoadFromJF=True):
        try:
            self.gacha = GachaData(isLoadFromJF)
            self.df = self.gacha.totalDF
            # 四星五星list
            self.rank45DF = self.gacha.getRankList()
            setState(6, "数据处理完成")
            setState(7, "完成")
        except Exception as e:
            print("init"+str(e))

    # 获取饼图
    def getPieData(self, startTime="2020-09-15 08:00:00", endTime=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                   gachaTypeList=None, rankList=None):
        try:
            df = self.df
            df = self.gacha.filterData(df, startTime, endTime, gachaTypeList, rankList)
            data = self.gacha.gachaPie(df)
            response = {'data': data}
            return response
        except Exception as e:
            print("0"+str(e))

    # 获取词云
    def getWordData(self, startTime="2020-09-15 08:00:00", endTime=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    gachaTypeList=None, rankList=None):
        try:
            df = self.df
            df = self.gacha.filterData(df, startTime, endTime, gachaTypeList, rankList)
            data = self.gacha.getDictListForWorldCloud(df)
            response = {'data': data}
            return response
        except Exception as e:
            print("1"+str(e))

    # 获取条形图
    def getBarData(self, startTime="2020-09-15 08:00:00", endTime=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                   gachaTypeList=None, rankList=None):
        try:
            df = self.df
            df = self.gacha.filterData(df, startTime, endTime, gachaTypeList, rankList)
            data = self.gacha.gachaCount(df)
            response = {'data': data}
            return response
        except Exception as e:
            print("2"+str(e))


    # 获取时间轴,总览数据
    def getTimeLine(self, startTime="2020-09-15 08:00:00", endTime=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    gachaTypeList=None, rankList=None):
        try:
            df = self.rank45DF
            df = self.gacha.filterData(df, startTime, endTime, gachaTypeList, rankList).reset_index(drop=True)
            ave = 0
            if df["count"].astype(int).sum() != 0:
                ave = df["rank_count"].astype(int).sum() / df["count"].astype(int).sum()
            res = df.T.to_dict().values()
            response = {'data': list(res),
                        'ave': '%.4f' % ave}
            return response

        except Exception as e:
            print("3"+str(e))

    # 获取比率
    def getRateData(self, startTime="2020-09-15 08:00:00", endTime=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    gachaTypeList=None, rankList=None):
        try:
            df = self.df
            df = self.gacha.filterData(df, startTime, endTime, gachaTypeList, rankList)
            rate5, rate4, rate3 = 0, 0, 0
            if df["count"].astype(int).sum() != 0:
                rate5 = df.query("rank_type=='5'")["count"].astype(int).sum() / df["count"].astype(int).sum() * 100
                rate4 = df.query("rank_type=='4'")["count"].astype(int).sum() / df["count"].astype(int).sum() * 100
                rate3 = df.query("rank_type=='3'")["count"].astype(int).sum() / df["count"].astype(int).sum() * 100
            totalCount = df["count"].astype(int).sum()
            response = {'rate': ['%.4f' % rate5, '%.4f' % rate4, '%.4f' % rate3],
                        'totalCount': int(totalCount)}
            return response
        except Exception as e:
            print("4"+str(e))


    def genExcel(self):
        self.gacha.genExcelData()
        response = {'msg':"excel文件导出完成"}
        return response
    # todo 添加自定义图片
    def getWordPic(self, fp='./wordpic.png'):
        try:
            if getattr(sys, 'frozen', None):
                basedir = sys._MEIPASS
            else:
                basedir = "."
            # 传给词云的pic
            wordCloudPicSrc = base64encode(basedir + "/wordpic.png")
            # 用于显示的pic
            picSrc = base64encode(basedir + '/origin.png')
            return {"data": wordCloudPicSrc, "src": picSrc}
        except Exception as e:
            print(str(e))


    # 加载时数据显示状态
    def getState(self):
        try:
            loadTitle = "状态"
            loadMsg = State.MsgState
            loadStep = State.StepState
            return {
                "loadTitle": loadTitle, "loadMsg": loadMsg, "loadStep": loadStep
            }
        except Exception as e:
            print("state"+str(e))



api = Api()
window = webview.create_window('gachaTool', url="index.html", js_api=api, min_size=(1200, 900))
webview.start()
