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
import bc_study.tushare_csv_datafeed as ts_df


if __name__ == '__main__':
    # 初始化引擎
    cerebro = bt.Cerebro()
    # 设置初始资金：
    cerebro.broker.setcash(200000.0)

    # 从csv文件中读取数据
    data = ts_df.get_csv_daily_data(stock_id="600016.SH")
    print(data)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # 回测启动运行
    cerebro.run()

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
