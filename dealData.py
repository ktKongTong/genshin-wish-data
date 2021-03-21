# 使用pandas处理data
# 池子时长-池子是什么
# 1.饼图
# 2.词云
# 3.抽卡次数
from datetime import datetime
from pandas import DataFrame
from getWishData import Data
from getStaticData import getRoleInfo, getWeaponInfo
from utils import loadDataFromJF,saveToJF
from pandas import concat


class GachaData():
    def __init__(self):
        try:
            data = loadDataFromJF("./ysdata.json")
        except FileNotFoundError as e:
            d = Data()
            data = d.data
            saveToJF(data, "ysdata")
        self.getMyData(data)
        self.charList = getRoleInfo()
        self.weaponList = getWeaponInfo()
    # 获取数据，total和分开
    def getMyData(self,data):
        self.xsDF = DataFrame(data["xsData"]["data"])
        self.normDF = DataFrame(data["normData"]["data"])
        self.roleDF = DataFrame(data["roleData"]["data"])
        self.weaponDF = DataFrame(data["weaponData"]["data"])
        for item in [self.xsDF,self.normDF,self.roleDF,self.weaponDF]:
            item.drop("uid", axis=1, inplace=True)
            item.drop("item_id", axis=1, inplace=True)
            item.drop("lang", axis=1, inplace=True)
            item['time'] = item['time'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
        self.totalDF = self.normDF.copy()
        self.totalDF = self.totalDF.append(self.xsDF.copy())
        self.totalDF = self.totalDF.append(self.weaponDF.copy())
        self.totalDF = self.totalDF.append(self.roleDF.copy())

    # 日期，类型筛选
    # 传入起止时间以及涉及的池子列表，以及要处理的df
    # 返回DataFrame
    def filterData(self,df, startTime="2020-09-15 08:00:00", endTime=datetime.now().strftime('%Y-%m-%d %H:%M:%S'), gachaTypeList=None, rankList=None):
        # 祈愿类型
        if gachaTypeList is None:
            gachaTypeList = ["100","200", "301", "302"]
        if rankList is None:
            rankList = [3, 4, 5]
        typeQuery = ''
        for item in gachaTypeList:
            typeQuery = typeQuery + " or " + 'gacha_type == "{}"'.format(item)
        if len(typeQuery) > 0:
            typeQuery = typeQuery[4:]
        df = df.query(typeQuery)
        rankQuery = ''
        for item in rankList:
            rankQuery = rankQuery + " or " + 'rank_type == "{}"'.format(item)
        if len(rankQuery) > 0:
            rankQuery = rankQuery[4:]
        df = df.query(rankQuery)
        # 时间
        timeQuery = "'{}'< time < '{}'".format(startTime, endTime)
        df = df.query(timeQuery)
        df = df.sort_values(by=["id"])
        return df
    # 条形图，祈愿次数
    # 3星武器，4星武器,4星角色，5星角色，5星武器
    def gachaCount(self,df):
        df = df[["item_type","rank_type",'time',"count"]].copy()
        df["time"] = df["time"].astype("datetime64[D]")
        countDict:DataFrame = df.groupby(["time", "rank_type", "item_type"]).count().unstack().unstack().fillna(0)
        indexList = [("count","武器","3"),("count","武器","4"),("count","角色","4"),("count","角色","5"),("count","武器","5")]
        for i in indexList:
            if i not in countDict.columns:
                countDict.insert(0,column=i,value=[0 for i in range(len(countDict.index))])
        if ("count","角色","3") in countDict.columns:
            countDict = countDict.drop([("count","角色","3")],axis=1)
        # 时间重采样
        res: DataFrame = countDict.resample('D').last().fillna(0)
        index = res.index.astype(str).tolist()
        legendData = [item[2]+"星"+item[1] for item in res.columns.values]
        series =  [{"name":item[2]+"星"+item[1],
                "type":"bar",
                "stack":"day",
                "emphasis":{"focus":"series"},
                "data":res[item].values.tolist()} for item in res.columns.values]
        return {
            "xAxisData":index,
            "series":series,
            "legendData":legendData
        }
    # 饼图
    # [{"name":"text","value":300},]
    # todo 空数据排错
    def gachaPie(self, df: DataFrame):
        countDict: dict = df[["item_type", "rank_type", "count"]].groupby(["rank_type", "item_type"]).count().to_dict()[
            "count"]
        countDictList = [{"name": item[0] + "星" + item[1], "value": countDict[item]} for item in countDict]
        return countDictList
    # 词云 传入dataFrame
    # 返回列表字典
    # [{"name":"text","value":300},]
    def getDictListForWorldCloud(self, df):
        wordDict = df[["name", "count"]].groupby("name").count().to_dict()["count"]
        wordDictList = [{"name": item, "value": wordDict[item]} for item in wordDict]
        return wordDictList

    #     获取所有4星,五星数据
    def getRankList(self):
        def getRankCount( df, rank):
            df.iloc[:] = df.iloc[::-1].values
            df = df.reset_index()
            df = df.sort_values(by=["id"], ascending=False)
            query = "rank_type=='{}'".format(rank)
            if rank == "4":
                query = "rank_type=='4' or rank_type =='5'"
            df: DataFrame = df.query(query)
            df.iloc[:] = df.iloc[::-1].values
            df.loc[:, "pre_index"] = df.loc[:, "index"].shift(1).fillna(-1)
            df["rank_count"] = df["index"] - df["pre_index"]
            if rank == "4":
                df = df.query('rank_type=="4"')
            df.drop("index", axis=1, inplace=True)
            df.drop("pre_index", axis=1, inplace=True)
            return df
        res = DataFrame([],columns=['gacha_type', 'count', 'time', 'name','item_type',"rank_type","id","rank_count"])
        for item in [self.roleDF,self.xsDF,self.weaponDF,self.normDF]:
            lastDF = getRankCount(item.copy(), "5")
            lastDF2 = getRankCount(item.copy(), "4")
            res = concat([lastDF2.copy(),res.copy()])
            res = concat([lastDF.copy(), res.copy()])
        res:DataFrame = res.sort_values(by=["id"]).reset_index(drop=True)
        res.loc[:,"time"] = res.loc[:,"time"].astype(str)
        df = DataFrame(self.charList)
        df2 = DataFrame(self.weaponList)
        df = df.merge(df2, how="outer").fillna("None")
        result = res.merge(df[["name","avatar"]],on='name').sort_values(by=["id"]).reset_index(drop=True)
        return result



# if __name__=="__main__":
#     pd.set_option('display.max_rows', 500)
#     pd.set_option('display.max_columns', 500)
#     pd.set_option('display.width', 1000)
#     d = GachaData()
#     res = d.getRankList()
#     res=d.filterData(res,gachaTypeList=["100","200"],rankList=[5])
#     res = res.reset_index(drop=True)
#     print(res)
# 这个只应该允许获取全部数据之后再筛选
# 加入count4，5列
# 获取单个池子












# if __name__ == "__main__":
#     df = getMyData()
#     df:DataFrame = filterData(df,gachaTypeList=["200","302"],rankList=["4","5"])
# #     按时间排序
#     df["time"]=df["time"].astype(str)
#     res = list(df.T.to_dict().values())
#     url = "https://api-takumi.mihoyo.com/event/e20200928calculate/v1/avatar/list"
    # payload={
    #     "element_attr_ids":[],
    #     "weapon_cat_ids":[],
    #     "page":1,
    #     "size":20
    # }
    #
    # res = requests.post(url=url,data=json.dumps(payload))
    # print(res.text)
    # print(res)
    # for item in df:
    #     print(item)
    # print(df.to_dict())
# t = {
#     "normData": {
#         "name": "normData",
#         "text": "常驻",
#         "data": [
#             {
#                 "uid": 101431554,
#                 "gacha_type": 200,
#                 "item_id": "",
#                 "count": 1,
#                 "time": "2020-12-25 23:49:28",
#                 "name": "飞天御剑",
#                 "lang": "zh-cn",
#                 "rank_type": 3,
#                 "item_type": "武器",
#                 "id": 1608908400001426366
#             }
#         ]
#     }
# }