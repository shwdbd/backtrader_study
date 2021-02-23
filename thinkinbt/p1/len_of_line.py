#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   len_of_line.py
@Time    :   2021/02/23 19:06:37
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   计算line的长度

line的长度，即截至到当前时刻策略line已执行的单元。
如果有最小时刻，则将最小时刻计算进去

逻辑：
1. 加载5天数据
2. 计算2天的移动平均线sma

输出：
1. 控制台输出：
2019-01-03, LEN(self) = 2
2019-01-03, LEN(self.sma) = 2
2019-01-04, LEN(self) = 3
2019-01-04, LEN(self.sma) = 3
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
        self.sma = bt.ind.MovingAverageSimple(self.datas[0].close, period=2)
        pass

    def next(self):
        self.log("LEN(self) = {0}".format(len(self)))
        # self.log("LEN(self.lines) = {0}".format(len(self.lines)))
        # self.log("LEN(self.datas[0]) = {0}".format(len(self.datas[0])))
        # self.log("SMA = {0}".format(self.sma[0]))
        self.log("LEN(self.sma) = {0}".format(len(self.sma)))


# 启动回测
def engine_run():
    # 初始化引擎
    cerebro = bt.Cerebro()
    # 给Cebro引擎添加策略
    cerebro.addstrategy(DemoStrategy)
    # 从csv文件加载数据
    data = data_tl.get_stock_daily(stock_id="600016.SH", start="20190101", end="20190105")
    cerebro.adddata(data)
    # 回测启动运行
    cerebro.run()
    # cerebro.plot()


if __name__ == '__main__':
    engine_run()
