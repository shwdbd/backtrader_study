#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   quickstart_demo0.py
@Time    :   2020/10/29 15:25:16
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   官方QuickStart第1个策略示例

使用本地的股票csv文件，每日输出开盘价

'''
import backtrader as bt
import os, sys, datetime
import bc_study.data_downloader as dl
import pandas as pd


# 演示用策略，每日输出开盘价
class TestStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "open" line in the data[0] dataseries
        self.dataopen = self.datas[0].open
        print("TestStrategy init function called")

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Open, %.2f' % self.dataopen[0])


# 加载数据
def get_data():
    """取得数据包
    """

    # 加载数据
    start = "20190101"
    end = "20190110"
    stock_id = "600016.SH"
    file_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), '../fd_data/') + stock_id + ".csv"
    if not os.path.exists(file_path):
        dl.stock_daily_to_csv(stock_id, start, end)

    # 数据清洗
    df = pd.read_csv(filepath_or_buffer=file_path)
    df.sort_values(by=["trade_date"], ascending=True, inplace=True)    # 按日期先后排序
    df.index = pd.to_datetime(df.trade_date, format='%Y%m%d')
    df['openinterest']=0
    df=df[['open','high','low','close','vol','openinterest']]
    # print(df.shape[0])
    data = bt.feeds.PandasData(dataname = df, fromdate = datetime.datetime(2019, 1, 1), todate = datetime.datetime(2019, 1, 10))
    return data


# 启动回测
def engine_run():
    # 初始化引擎
    cerebro = bt.Cerebro()

    # 给Cebro引擎添加策略
    cerebro.addstrategy(TestStrategy)

    # 设置初始资金：
    cerebro.broker.setcash(200000.0)

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
    
