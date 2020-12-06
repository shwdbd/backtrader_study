#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   datafeed_create.py
@Time    :   2020/12/06 17:05:36
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   探索建立DataFeed的实验性程序代码

- 读取backtrade csv文件
- 读取tushare默认下载的csv文件
- 读取在线tushare api
- 增加pe列

'''
import backtrader as bt
import datetime
import tushare as ts
import pandas as pd


class MyCsvFileData(bt.feeds.GenericCSVData):
    # 自定义的文件格式

    params = (
        ('fromdate', datetime.datetime(2000, 1, 1)),
        ('todate', datetime.datetime(2000, 12, 31)),
        ('nullvalue', 0.0),
        ('dtformat', ('%Y-%m-%d %H:%M:%S')),
        # ('tmformat', ('%H.%M.%S')),
        ('nullvalue', 0.00),
        ('datetime', 0),
        ('high', 1),
        ('low', 2),
        ('open', 3),
        ('close', 4),
        ('volume', 5),
        ('openinterest', -1)
    )


class TusharePdData(bt.feeds.PandasData):
    '''
    从Tushare读取A股票数据日线
    '''

    params = (
        # Possible values for datetime (must always be present)
        #  None : datetime is the "index" in the Pandas Dataframe
        #  -1 : autodetect position or case-wise equal name
        #  >= 0 : numeric index to the colum in the pandas dataframe
        #  string : column name (as index) in the pandas dataframe
        ('datetime', None),
        # ('dtformat', ('%Y%m%d')),

        # Possible values below:
        #  None : column not present
        #  -1 : autodetect position or case-wise equal name
        #  >= 0 : numeric index to the colum in the pandas dataframe
        #  string : column name (as index) in the pandas dataframe
        ('open', -1),
        ('high', -1),
        ('low', -1),
        ('close', -1),
        ('volume', 9),
        ('openinterest', -1),
    )


def get_bt_csv_data(start="20000104", end="20000110"):
    # 取得csv文件

    dt_start = datetime.datetime.strptime(start, "%Y%m%d")
    dt_end = datetime.datetime.strptime(end, "%Y%m%d")

    data = bt.feeds.GenericCSVData(
        dataname='bc_study/demo/bt_csv_file.csv',
        fromdate=dt_start,
        todate=dt_end,
        nullvalue=0.0,
        dtformat=('%Y-%m-%d'),
        datetime=0,
        high=1,
        low=2,
        open=3,
        close=4,
        volume=5,
        openinterest=-1
    )
    return data


def get_tushare_data(start="20200101", end="20200131"):
    # 从tushare在线读取数据

    stock_id = "000001.SZ"
    start = "20190101"
    end = "20191231"
    dt_start = datetime.datetime.strptime(start, "%Y%m%d")
    dt_end = datetime.datetime.strptime(end, "%Y%m%d")
    TOKEN = '341d66d4586929fa56f3f987e6c0d5bd23fb2a88f5a48b83904d134b'

    ts.set_token(TOKEN)
    pro = ts.pro_api()

    try:
        # 加载数据
        df = pro.daily(ts_code=stock_id, start_date=start, end_date=end)
        # 将日期列，设置成index
        df.index = pd.to_datetime(df.trade_date, format='%Y%m%d')
        print(df.head())

        data = TusharePdData(dataname=df, fromdate=dt_start, todate=dt_end)

        return data
    except Exception as err:
        print("下载{0}完毕失败！")
        print("失败原因 = " + str(err))


# 启动回测
def engine_run():
    # 初始化引擎
    cerebro = bt.Cerebro()

    # # 给Cebro引擎添加策略
    # cerebro.addstrategy(StopLimitOrderStrategy)

    # 设置初始资金：
    cerebro.broker.setcash(200000.0)

    # # 从csv文件加载数据
    # data = get_bt_csv_data(start="20001219", end="20001225")
    # cerebro.adddata(data)

    # # 从自定义类加载数据
    # data = MyCsvFileData(dataname='bc_study/demo/bt_csv_file.csv', start="20001219", end="20001225")
    # cerebro.adddata(data)

    # 从tushare读取
    # data = get_tushare_data(start="20200101", end="20200131")
    # cerebro.adddata(data)
    # cerebro.adddata(ts_df.get_tushare_online_daily_data())
    data = get_tushare_data()
    cerebro.adddata(data)

    # 回测启动运行
    cerebro.run()

    cerebro.plot()


if __name__ == '__main__':
    engine_run()
    # get_tushare_data()
