#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   bt_process.py
@Time    :   2021/02/23 10:03:05
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   Bt回测执行流程

包括的函数：
- init
- next
- prenext
- startnext

输出：
1. 控制台输出：
初始账户价值: 200000.00
2019-01-09, __init__()
2019-01-02, prenext()
2019-01-03, next()
2019-01-04, next()
2019-01-07, next()
2019-01-08, next()
2019-01-09, next()
最终账户价值: 200000.00

2. 图形输出 

'''

import backtrader as bt
import thinkinbt.p1.data_tl as data_tl


# 策略
class DemoStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.log("__init__()")

    def prenext(self):
        self.log("prenext()")

    def nextstart(self):
        self.log("prenext()")

    def next(self):
        self.log("next()")


# 启动回测
def engine_run():
    # 初始化引擎
    cerebro = bt.Cerebro()
    # 给Cebro引擎添加策略
    cerebro.addstrategy(DemoStrategy)
    # 设置初始资金：
    cerebro.broker.setcash(200000.0)
    # 从csv文件加载数据
    data = data_tl.get_stock_daily(stock_id="600016.SH", start="20190101", end="20190110")
    cerebro.adddata(data)
    print('初始账户价值: %.2f' % cerebro.broker.getvalue())
    # 回测启动运行
    cerebro.run()
    print('最终账户价值: %.2f' % cerebro.broker.getvalue())
    cerebro.plot()


if __name__ == '__main__':
    engine_run()
