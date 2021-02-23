#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   data_tl.py
@Time    :   2021/02/22 23:48:56
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   DataFeed工具集
'''
from datetime import datetime
import backtrader as bt
import os


def get_stock_daily(stock_id="600016.SH", start="20190101", end="20190115"):
    """读取股票日线数据

    Args:
        stock_id (str, optional): 股票代码. Defaults to "600016.SH".
        start (str, optional): 开始日期. Defaults to "20190101".
        end (str, optional): 结束日期. Defaults to "20190115".

    Raises:
        Exception: [description]

    Returns:
        [type]: [description]
    """
    try:
        # 日期格式转换
        dt_start = datetime.strptime(start, "%Y%m%d")
        dt_end = datetime.strptime(end, "%Y%m%d")

        # 数据文件
        data_file = os.path.join('fd_data/' + stock_id + ".csv")
        if not os.path.exists(data_file):
            print("数据源文件未找到！" + data_file)
            raise Exception("数据源文件未找到！" + data_file)

        datafeed = bt.feeds.GenericCSVData(
            dataname=data_file,     # 数据文件
            datetime=1,
            open=2,
            high=3,
            low=4,
            close=5,
            volume=9,
            openinterest=-1,
            dtformat=('%Y%m%d'),
            fromdate=dt_start,
            todate=dt_end)

        return datafeed
    except Exception:
        print("读取股票数据失败！")
        return None


if __name__ == '__main__':
    # get_data()
    # df = ts_df.get_csv_daily_data(stock_id="600016.SH")
    df = get_stock_daily(stock_id="600016.SH")
    print(df)
