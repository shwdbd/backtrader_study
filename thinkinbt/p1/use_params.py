#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   use_params.py
@Time    :   2021/02/25 20:55:33
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   使用策略参数

目的：
1. 策略参数的使用
2. 引擎向策略传入参数


'''
import backtrader as bt
import thinkinbt.p1.data_tl as data_tl


class DemoStrategy(bt.Strategy):

    # 定义参数
    params = dict(
        myname="Jack", myage=10
    )

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.log("__init__() : ")
        self.log("My Name = {0}".format(self.p.myname))
        self.log("My Age = {0}".format(self.p.myage))

    def next(self):
        self.log("My Name = {0}".format(self.p.myname))
        self.log("My Age = {0}".format(self.p.myage))


# 启动回测
def engine_run():
    # 初始化引擎
    cerebro = bt.Cerebro()
    # 给Cebro引擎添加策略
    cerebro.addstrategy(DemoStrategy, myname="Mike")    # 参数覆盖了策略中的值
    # 设置初始资金：
    cerebro.broker.setcash(20000.0)
    # 从csv文件加载数据
    data = data_tl.get_stock_daily(
        stock_id="600016.SH", start="20190101", end="20190105")
    cerebro.adddata(data, name="民生银行")
    # 回测启动运行
    # print('初始账户价值: %.2f' % cerebro.broker.getvalue())
    # 回测启动运行
    cerebro.run()
    # print('最终账户价值: %.2f' % cerebro.broker.getvalue())


if __name__ == '__main__':
    engine_run()
