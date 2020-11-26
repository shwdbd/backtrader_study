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
import datetime
import pandas as pd
import backtrader.feeds as btfeeds


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
    file_path = os.path.join('fd_data/' + stock_id + ".csv")
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

    # print(df.shape[0])
    # print(df.info())
    # print(df.head())

    data = bt.feeds.PandasData(dataname=df, fromdate=dt_start, todate=dt_end)
    return data


# 加载本地csv文件数据
def get_csv_GenericCSVData(stock_id="600016.SH", start="20190101", end="20191231"):
    # 日期格式转换
    dt_start = datetime.datetime.strptime(start, "%Y%m%d")
    dt_end = datetime.datetime.strptime(end, "%Y%m%d")
    # 读取文件
    data = btfeeds.GenericCSVData(
        dataname='fd_data/600016.SH.csv',
        fromdate=dt_start,
        todate=dt_end,
        nullvalue=0.0,
        dtformat=('%Y%m%d'),
        datetime=1,
        high=3,
        low=4,
        open=2,
        close=5,
        volume=9,
        openinterest=-1
    )
    return data


if __name__ == "__main__":
    # 读取从tushare下载的日线数据文件：
    data = get_csv_daily_data()
    print(data)
    print(type(data))

    # # 读取csv文件
    # data = get_csv_GenericCSVData()
    # print(data)
    # print(type(data))
