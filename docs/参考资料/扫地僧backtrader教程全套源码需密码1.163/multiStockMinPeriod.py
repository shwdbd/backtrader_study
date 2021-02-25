import datetime
import glob
import os.path

import backtrader as bt


# 创建策略
class SmaCross(bt.Strategy):
    # 可配置策略参数
    params = dict(
        pfast=2,  # 短期均线周期
    )

    def __init__(self):
        self.sma = [bt.ind.SMA(d, period=self.p.pfast) for d in self.datas]

    def prenext(self):
        print(
            'prenext self {} len {}| data0 {} close {} len {} | data1 {} close {} len {} '
            .format(self.datetime.date(), len(self),
                    self.data0.datetime.date(), self.data0.close[0],
                    len(self.data0), self.data1.datetime.date(),
                    self.data1.close[0], len(self.data1)))

    def next(self):
        print(
            'next self {} len {}| data0 {} close {} len {} | data1 {} close {} len {} '
            .format(self.datetime.date(), len(self),
                    self.data0.datetime.date(), self.data0.close[0],
                    len(self.data0), self.data1.datetime.date(),
                    self.data1.close[0], len(self.data1)))
   

##########################
# 主程序开始
#########################

cerebro = bt.Cerebro()

datadir = './test'  # 数据文件位于本脚本所在目录的data子目录中
datafilelist = glob.glob(os.path.join(datadir, '*'))  # 数据文件路径列表
maxstocknum = 2  # 股票池最大股票数目
datafilelist = datafilelist[0:maxstocknum]  # 截取指定数量的股票池

# 将目录datadir中的所有数据文件加载进系统
for fname in datafilelist:
    data = bt.feeds.GenericCSVData(
        dataname=fname,
        datetime=2,  # 日期行所在列
        open=4,  # 开盘价所在列
        high=5,  # 最高价所在列
        low=6,  # 最低价所在列
        close=3,  # 收盘价价所在列
        volume=10,  # 成交量所在列
        openinterest=-1,  # 无未平仓量列
        dtformat=('%Y%m%d'),  # 日期格式
        fromdate=datetime.datetime(2010, 1, 1),  # 起始日
        todate=datetime.datetime(2020, 7, 10),  # 结束日
        timeframe=bt.TimeFrame.Months  # 月线数据
    )
    cerebro.adddata(data)

# 注入策略
cerebro.addstrategy(SmaCross)

cerebro.run()
