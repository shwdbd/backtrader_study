#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   tushare_csv_datafeed.py
@Time    :   2020/11/11 00:04:27
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   基于tushare下载的csv数据源工具代码
'''
import backtrader as bt
import os
import sys
import datetime
import pandas as pd


# 加载本地csv文件数据
def get_csv_daily_data(stock_id="600016.SH", start="20190101", end="20191231"):
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
    file_path = os.path.join(os.path.dirname(os.path.abspath(
        sys.argv[0])), '../fd_data/') + stock_id + ".csv"
    if not os.path.exists(file_path):
        print("数据源文件未找到！")
        raise Exception("数据源文件未找到！")

    # 数据清洗
    df = pd.read_csv(filepath_or_buffer=file_path)
    df.sort_values(by=["trade_date"], ascending=True,
                   inplace=True)    # 按日期先后排序
    df.index = pd.to_datetime(df.trade_date, format='%Y%m%d')
    df['openinterest'] = 0
    df = df[['open', 'high', 'low', 'close', 'vol', 'openinterest']]
    # print(df.shape[0])
    data = bt.feeds.PandasData(dataname=df, fromdate=dt_start, todate=dt_end)
    return data


if __name__ == "__main__":
    data = get_csv_daily_data()
    print(data)
    print(type(data))
