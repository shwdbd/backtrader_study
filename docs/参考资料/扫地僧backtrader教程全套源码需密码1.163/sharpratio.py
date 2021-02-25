from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from datetime import datetime

import backtrader as bt

import os.path  # 管理路径
import sys  # 发现脚本名字

cerebro = bt.Cerebro()

# 获取本脚本文件所在路径
modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
# 拼接得到数据文件全路径
datapath = os.path.join(modpath, './600000qfq.csv')

# 创建行情数据对象，加载数据
data = bt.feeds.GenericCSVData(
    dataname=datapath,
    datetime=2,  # 日期行所在列
    open=3,  # 开盘价所在列
    high=4,  # 最高价所在列
    low=5,  # 最低价所在列
    close=6,  # 收盘价价所在列
    volume=10,  # 成交量所在列
    openinterest=-1, # 无未平仓量列.(openinterest是期货交易使用的)
    dtformat=('%Y%m%d'),  # 日期格式
    fromdate=datetime(2019, 1, 1),  # 起始日
    todate=datetime(2020, 7, 8))  # 结束日

cerebro.adddata(data)

# strategy
cerebro.addstrategy(bt.strategies.SMA_CrossOver)

# Analyzer
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='mysharpe', timeframe = bt.TimeFrame.Months)
cerebro.addanalyzer(bt.analyzers.SharpeRatio_A, _name='mysharpeA')

thestrats = cerebro.run()
thestrat = thestrats[0]

print('Sharpe Ratio:', thestrat.analyzers.mysharpe.get_analysis())
print('Sharpe RatioA:', thestrat.analyzers.mysharpeA.get_analysis())