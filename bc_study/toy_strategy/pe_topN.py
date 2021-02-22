#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   pe_topN.py
@Time    :   2020/12/21 15:45:38
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   定期找出PE最小的10支股票

- 加载2019年所有的股票
- 每10天，找出pe最小的10个股票清单
- 输出这个股票清单
* 用name来检索datas

'''
import backtrader as bt
import os
import datetime
import pandas as pd


DATA_ROOT = "c:/fd_data/tushare/"


# 加载股票日线数据文件
def get_stock_daily_data(stock_id="600016.SH", start="20190101", end="20191231"):
    """从本地股票日线csv文件中取得DataFeed对象

    Args:
        stock_id (str, optional): tushare格式的股票代码. Defaults to "600016.SH".

    Raises:
        Exception: 本地文件无法找到

    Returns:
        [type]: backtrader.feeds.pandafeed.PandasData对象
    """
    # 日期格式转换
    dt_start = datetime.datetime.strptime(start, "%Y%m%d")
    dt_end = datetime.datetime.strptime(end, "%Y%m%d")

    # 文件存放地址
    file_path = DATA_ROOT + 'daily_bar/' + stock_id + ".csv"
    if not os.path.exists(file_path):
        print("数据源文件未找到！" + file_path)
        raise Exception("数据源文件未找到！" + file_path)

    # 将csv文件转为pandas.dataframe
    df = pd.read_csv(filepath_or_buffer=file_path)
    # 按日期先后排序
    df.sort_values(by=["trade_date"], ascending=True, inplace=True)
    # 将日期列，设置成index
    df.index = pd.to_datetime(df.trade_date, format='%Y%m%d')
    # 增加一列openinterest
    df['openinterest'] = 0.00
    # 取出特定的列
    df = df[['open', 'high', 'low', 'close', 'vol', 'openinterest']]
    # 列名修改成指定的
    df.rename(columns={"vol": "volume"}, inplace=True)

    data = bt.feeds.PandasData(dataname=df, fromdate=dt_start, todate=dt_end)
    return data


class BestPeStrategy(bt.Strategy):
    """
    最小PE策略

    """

    def log(self, txt, dt=None):
        """ log信息的功能 """
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # self.dataopen = self.datas[0].open
        self.dataopen = self.data.get("000001.SZ").open

    def next(self):
        # 按name取数据datafeed
        self.log(self.dataopen[0])


if __name__ == '__main__':
    # 初始化引擎
    cerebro = bt.Cerebro()

    # 给Cebro引擎添加策略
    cerebro.addstrategy(BestPeStrategy)

    # 设置初始资金：
    cerebro.broker.setcash(100000.0)    # 10万元

    # 从csv文件加载数据
    start = "20190101"
    end = "20190331"
    data = get_stock_daily_data(stock_id="000001.SZ", start=start, end=end)
    cerebro.adddata(data, name="000001.SZ")
    data = get_stock_daily_data(stock_id="000002.SZ", start=start, end=end)
    cerebro.adddata(data, name="000002.SZ")

    # 回测启动运行
    cerebro.run()
