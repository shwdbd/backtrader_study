#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   quickstart_demo0.py
@Time    :   2020/10/29 15:25:16
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   官方QuickStart第2个示例

在Demo1基础上，增加DataFeed数据源的使用

'''
import backtrader as bt
import os, sys, datetime


if __name__ == '__main__':
    # 初始化引擎
    cerebro = bt.Cerebro()
    # 设置初始资金：
    cerebro.broker.setcash(200000.0)

    # 从csv文件中读取数据
    # 计算当前执行文件的目录
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    # print(modpath)
    datapath = os.path.join(modpath, '../fd_data/600016.SH.csv')
    # 从csv文件中读取
    data = bt.feeds.GenericCSVData(
        dataname='mydata.csv',
        fromdate=datetime.datetime(2000, 1, 1),
        todate=datetime.datetime(2000, 12, 31),
        nullvalue=0.0,
        dtformat=('%Y-%m-%d'),
        datetime=0,
        high=3,
        low=4,
        open=2,
        close=5,
        volume=9,
        openinterest=-1
    )
    print(data)


    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # 回测启动运行
    cerebro.run()

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
