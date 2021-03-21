原神祈愿记录汇总工具
====
感谢[biuuu](https://github.com/biuuu)

[genshin-gacha-export](https://github.com/biuuu/genshin-gacha-export)

最初在某论坛上看到分享

自己使用后效果如图，只是需要环境配置，花了好些时间😑。

![P1](https://cdn.jsdelivr.net/gh/ktKongTong/genshin-wish-data/pic/p1.png)

全新升级
- 增加支持缩放的条形图，词云，5星时间轴
- <h3 style="color:#f7ba2a">支持范围时间<h3>
- 支持任意祈愿组合

目前效果如图
![P3](https://cdn.jsdelivr.net/gh/ktKongTong/genshin-wish-data/pic/p3.png)
![P4](https://cdn.jsdelivr.net/gh/ktKongTong/genshin-wish-data/pic/p4.png)
![P5](https://cdn.jsdelivr.net/gh/ktKongTong/genshin-wish-data/pic/p5.png)
![P6](https://cdn.jsdelivr.net/gh/ktKongTong/genshin-wish-data/pic/p6.png)

### 获取数据的方式

在使用PC端原神进行祈愿查询后，会在一个日志文件中有记录

路径为`用户目录/AppData/LocalNow/miHoYo/原神/output_log.txt`

其中包含了查询祈愿的URL，获取到URL中的参数authkey，即可获取到祈愿数据。目前估计authkey的有效时间是24h。


### 使用说明

- 仅适用于国服PC
- 正常运行的前提是24h内登入原神且有查询过祈愿记录(否则闪退)
- 运行之后点击加载数据，等待一段时间(取决于你的祈愿数量)

#### 运行结果
会生成ysData.json文件，json文件是获取到的数据。

#### TODO

- [ ] 添加excel数据导出，方便用户使用[抽卡记录分析(成就)工具](https://genshin-gacha-analyzer.vercel.app/)
- [ ] 界面优化