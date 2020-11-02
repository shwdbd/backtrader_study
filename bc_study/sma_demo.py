#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   quickstart_demo0.py
@Time    :   2020/10/29 15:25:16
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   最简单的SMA均线策略 示例

20日均线，如果今天开盘价小于SMA则买入，大于SMA则卖

'''
import backtrader as bt
import os, sys, datetime
import bc_study.data_downloader as dl
import pandas as pd


# 最简单的SMA策略
class SMAStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # 建立开盘价的引用
        self.dataopen = self.datas[0].open
        self.sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=120)

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Open, %.2f' % self.dataopen[0])
        self.log('SMA last, %.2f' % self.sma[-1])

        if not self.position:
            if self.dataopen[0] < self.sma[-1]:
                # 买入
                self.log('买入, 挂单价格 = %.2f' % self.dataopen[0])
                self.buy()
        else:
            if self.dataopen[0] > self.sma[-1]:
                # 卖出
                self.log('卖出, 挂单价格 = %.2f' % self.dataopen[0])
                self.sell()

# 加载数据
def get_data():
    """取得数据包
    """

    # 加载数据
    stock_id = "600016.SH"
    file_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), '../fd_data/') + stock_id + ".csv"
    if not os.path.exists(file_path):
        dl.stock_daily_to_csv(stock_id, "20190101", "20191231")

    # 数据清洗
    df = pd.read_csv(filepath_or_buffer=file_path)
    df.sort_values(by=["trade_date"], ascending=True, inplace=True)    # 按日期先后排序
    df.index = pd.to_datetime(df.trade_date, format='%Y%m%d')
    df['openinterest']=0
    df=df[['open','high','low','close','vol','openinterest']]
    # print(df.shape[0])
    data = bt.feeds.PandasData(dataname = df, fromdate = datetime.datetime(2019, 1, 1), todate = datetime.datetime(2019, 12, 31))
    return data


# 启动回测
def engine_run():
    # 初始化引擎
    cerebro = bt.Cerebro()

    # 给Cebro引擎添加策略
    cerebro.addstrategy(SMAStrategy)

    # 设置初始资金：
    cerebro.broker.setcash(200000.0)
    # Set the commission - 0.1% ... divide by 100 to remove the %
    cerebro.broker.setcommission(commission=0.001)

    # 从csv文件加载数据    
    data = get_data()
    cerebro.adddata(data)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    # 回测启动运行
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

if __name__ == '__main__':
    # get_data()
    engine_run()
    
