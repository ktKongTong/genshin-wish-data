# 使用pandas处理data
# 池子时长-池子是什么
# 1.饼图
# 2.词云
# 3.抽卡次数
from datetime import datetime
from pandas import DataFrame, ExcelWriter
from getWishData import Data, setState
from getStaticData import getRoleInfo, getWeaponInfo
from utils import loadDataFromJF, saveToJF
from pandas import concat


class GachaData():
    def __init__(self, isLoadFromJF=True):
        if isLoadFromJF:
            try:
                setState(0, "尝试从json文件中加载数据")
                data = loadDataFromJF("./ysdata.json")
                setState(5, "成功从json文件获取数据")
            except FileNotFoundError as e:
                d = Data()
                data = d.data
                saveToJF(data, "ysdata")
        else:
            d = Data()
            data = d.data
            saveToJF(data, "ysdata")
        setState(5, "开始进行数据处理")
        self.weaponList = getWeaponInfo()
        self.charList = getRoleInfo()
        self.getMyData(data)
        setState(5, "数据处理")

    # 刷新数据
    def flashData(self):
        d = Data()
        data = d.data
        saveToJF(data, "ysdata")
        self.getMyData(data)

    # 获取数据，total和分开
    def getMyData(self, data):
            self.xsDF = DataFrame(data["xsData"]["data"])
            self.normDF = DataFrame(data["normData"]["data"])
            self.roleDF = DataFrame(data["roleData"]["data"])
            self.weaponDF = DataFrame(data["weaponData"]["data"])
            for item in [self.xsDF, self.normDF, self.roleDF, self.weaponDF]:
                if not item.empty:
                    item.drop("uid", axis=1, inplace=True)
                    item.drop("item_id", axis=1, inplace=True)
                    item.drop("lang", axis=1, inplace=True)
                    item['time'] = item['time'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
            self.totalDF = self.normDF.copy()
            for item in [self.xsDF, self.roleDF, self.weaponDF]:
                if not item.empty:
                    self.totalDF = self.totalDF.append(item.copy())
    # 日期，类型筛选
    # 传入起止时间以及涉及的池子列表，以及要处理的df
    # 返回DataFrame
    def filterData(self, df, startTime="2020-09-15 08:00:00", endTime=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                   gachaTypeList=None, rankList=None):
        # 祈愿类型
        if gachaTypeList is None:
            gachaTypeList = ["100", "200", "301", "302"]
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
    def gachaCount(self, df):
        df = df[["item_type", "rank_type", 'time', "count"]].copy()
        df["time"] = df["time"].astype("datetime64[D]")
        countDict: DataFrame = df.groupby(["time", "rank_type", "item_type"]).count().unstack().unstack().fillna(0)
        indexList = [("count", "武器", "3"), ("count", "武器", "4"), ("count", "角色", "4"), ("count", "角色", "5"),
                     ("count", "武器", "5")]
        for i in indexList:
            if i not in countDict.columns:
                countDict.insert(0, column=i, value=[0 for i in range(len(countDict.index))])
        if ("count", "角色", "3") in countDict.columns:
            countDict = countDict.drop([("count", "角色", "3")], axis=1)
        # 时间重采样
        res: DataFrame = countDict.resample('D').last().fillna(0)
        index = res.index.astype(str).tolist()
        legendData = [item[2] + "星" + item[1] for item in res.columns.values]
        series = [{"name": item[2] + "星" + item[1],
                   "type": "bar",
                   "stack": "day",
                   "emphasis": {"focus": "series"},
                   "data": res[item].values.tolist()} for item in res.columns.values]
        return {
            "xAxisData": index,
            "series": series,
            "legendData": legendData
        }

    # 饼图
    # [{"name":"text","value":300},]
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

    def getRankCount(self, df, rank):
        df.iloc[:] = df.iloc[::-1].values
        df = df.sort_values(by=["id"], ascending=True)
        query = "rank_type=='{}'".format(rank)
        if rank == "4":
            query = "rank_type=='4' or rank_type =='5'"
        df: DataFrame = df.query(query)
        rankCount: DataFrame = df.index.to_frame() - df.index.to_frame().shift(1).fillna(-1)
        df.insert(df.shape[1], "rank_count", rankCount[0])
        if rank == "4":
            df = df.query('rank_type=="4"')
        return df

    #     获取所有4星,五星数据
    def getRankList(self):
        res = DataFrame([],
                        columns=['gacha_type', 'count', 'time', 'name', 'item_type', "rank_type", "id", "rank_count"])
        for item in [self.roleDF, self.xsDF, self.weaponDF, self.normDF]:
            if not item.empty:
                lastDF = self.getRankCount(item.copy(), "5")
                lastDF2 = self.getRankCount(item.copy(), "4")
                res = concat([lastDF2.copy(), res.copy()])
                res = concat([lastDF.copy(), res.copy()])
        res: DataFrame = res.sort_values(by=["id"]).reset_index(drop=True)
        res.loc[:, "time"] = res.loc[:, "time"].astype(str)
        df = DataFrame(self.charList)
        df2 = DataFrame(self.weaponList)
        df = df.merge(df2, how="outer").fillna("None")
        result = res.merge(df[["name", "avatar"]], on='name').sort_values(by=["id"]).reset_index(drop=True)
        return result

    # 生成excel文件
    def genExcelData(self):
        writer = ExcelWriter('ysdata.xlsx', engine='xlsxwriter')
        for df, name in [(self.normDF.copy(), "常驻祈愿"), (self.xsDF.copy(), "新手祈愿"),
                         (self.roleDF.copy(), "角色活动祈愿"), (self.weaponDF.copy(), "武器活动祈愿")]:
            if not df.empty:
                res = self.getRankCount(df, "5")
                df = df.sort_values(by="id").reset_index(drop=True)
                df["time"] = df["time"].astype(str)
                df.insert(df.shape[1], "totalCount", df.index + 1)
                if len(res.index)>0:
                    count5List = [i + 1 for item in res["rank_count"] for i in range(int(item))] + [i for i in range(1, 1 + int(
                        df.index[-1] - res.index[-1]))]
                else:
                    tmp=df.index+1
                    count5List =tmp.tolist()
                df.insert(df.shape[1], 'count5', count5List)
                df["rank_type"] = df["rank_type"].astype(int)
                df.rename(columns={'time': '时间', 'name': '名称', 'item_type': "类别", "rank_type": "星级", "totalCount": '总次数',
                                   'count5': "保底内"}, inplace=True)
                df.to_excel(writer, columns=['时间', '名称', '类别', '星级', '总次数', '保底内',"id"], index=False, encoding='utf-8',
                            sheet_name=name)
            # else:
            #     df.columns=['时间', '名称', '类别', '星级', '总次数', '保底内',"id"]
            #     df.to_excel(writer, columns=['时间', '名称', '类别', '星级', '总次数', '保底内',"id"], index=False, encoding='utf-8',
            #                 sheet_name=name)
        writer.save()


# 加载新数据
from pandas import set_option

if __name__ == "__main__":
    set_option('display.max_rows', 500)
    set_option('display.max_columns', 500)
    set_option('display.width', 1000)
    d = GachaData()
    d.genExcelData()
    # print()
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
