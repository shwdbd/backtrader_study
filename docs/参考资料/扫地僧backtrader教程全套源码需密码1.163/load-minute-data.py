from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


import backtrader as bt
import backtrader.feeds as btfeeds
from datetime import datetime


class testStrategy(bt.Strategy):
    def next(self):
        print(self.data0.datetime.datetime(0), len(self.data0),
              self.data0.open[0], self.data0.high[0], self.data0.low[0], self.data0.close[0],)


# Create a cerebro entity
cerebro = bt.Cerebro(stdstats=False)

# Add a strategy
cerebro.addstrategy(testStrategy)

# Load the Data
datapath = './2006-min-005.csv'



# 创建行情数据对象，加载数据
data = bt.feeds.GenericCSVData(
    dataname=datapath,
    datetime=0,  # 日期行所在列
    time = 1,
    open=2,  # 开盘价所在列
    high=3,  # 最高价所在列
    low=4,  # 最低价所在列
    close=5,  # 收盘价价所在列
    volume=6,  # 成交量所在列
    openinterest=-1,  # 无未平仓量列.(openinterest是期货交易使用的)
    dtformat=('%Y-%m-%d'),  # 日期格式
    tmformat = ('%H:%M:%S'), # 时间格式
    fromdate=datetime(2006, 1, 1),  # 起始日
    todate=datetime(2006, 1, 3),
    timeframe=bt.TimeFrame.Minutes
    )  # 结束日

cerebro.adddata(data)
cerebro.run()
