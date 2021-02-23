#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   read_lines_name.py
@Time    :   2021/02/23 10:15:17
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   读取lines名称

lines分为策略lines和数据lines两种。
策略lines通过self.lines访问；数据lines通过self.data[x].lines访问。
策略lines只有一个line：datatime

lines的名称可通过 lines.getlinealiases() 访问，返回一个元组，如('close', 'low', 'high', 'open', 'volume', 'openinterest', 'datetime')

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
        self.log("策略lines：{0}".format(self.lines.getlinealiases()))
        self.log("行情数据lines：{0}".format(self.datas[0].lines.getlinealiases()))

    def next(self):
        self.log("next()")
        self.log(self.datetime.date())


# 启动回测
def engine_run():
    # 初始化引擎
    cerebro = bt.Cerebro()
    # 给Cebro引擎添加策略
    cerebro.addstrategy(DemoStrategy)
    # 设置初始资金：
    cerebro.broker.setcash(200000.0)
    # 从csv文件加载数据
    data = data_tl.get_stock_daily(stock_id="600016.SH", start="20190101", end="20190105")
    cerebro.adddata(data)
    print('初始账户价值: %.2f' % cerebro.broker.getvalue())
    # 回测启动运行
    cerebro.run()
    print('最终账户价值: %.2f' % cerebro.broker.getvalue())
    # cerebro.plot()


if __name__ == '__main__':
    engine_run()
