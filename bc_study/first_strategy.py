#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   first_strategy.py
@Time    :   2020/10/22 22:21:38
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   第一个测试用策略，打印当日收盘价
'''
import backtrader as bt
import datetime
import sys
import pandas as pd
import tushare as ts


class MyStrategy(bt.Strategy):

    def __init__(self):
        #引用data[0]中的收盘价格数据
        self.dataclose = self.datas[0].close    # backtrader.linebuffer.LineBuffer
        print(self.dataclose)
        print("init")
        pass

    def log(self, txt, dt = None):
        dt = dt or self.datas[0].datetime.date(0)
        print("%s, %s" % (dt.isoformat(), txt))

    def next(self):
        # print("next函数")
        # self.log("next函数, Close, %.2f" % self.dataclose[0])
        pass

def get_data():
    """取得数据包
    """
    TOKEN = '341d66d4586929fa56f3f987e6c0d5bd23fb2a88f5a48b83904d134b'
    ts.set_token(TOKEN)
    pro = ts.pro_api()

    # 加载数据
    start = "2020-01-01"
    end = "2020-01-31"
    #df = ts.get_k_data("510300", autype = "qfq", start = start,  end = end)
    df = pro.daily(ts_code='600016.SH', start_date='20200101', end_date='20200131')
    df.sort_values(by=["trade_date"], ascending=True, inplace=True)    # 按日期先后排序
    df.index = pd.to_datetime(df.trade_date)
    df['openinterest']=0
    df=df[['open','high','low','close','vol','openinterest']]
    # print(df.head())
    data = bt.feeds.PandasData(dataname = df, fromdate = datetime.datetime(2020, 1, 1), todate = datetime.datetime(2020, 1, 31))
    return data

# if __name__ == "__main__":
#     df = get_data()
#     print(df)


if __name__ == "__main__":
    #初始化Cebro引擎
    cerebro = bt.Cerebro()

    # 给Cebro引擎添加策略
    cerebro.addstrategy(MyStrategy)

    # # 给Cebro引擎添加数据
    # data = bt.feeds.YahooFinanceCSVData(dataname='TSLA.csv')
    data = get_data()
    print(data)
    cerebro.adddata(data)

    # 设置初始资金
    cerebro.broker.setcash(100000.0)
    print("初始资金:%.2f" % cerebro.broker.getvalue())
    cerebro.run()
    print("期末资金:%.2f" % cerebro.broker.getvalue())