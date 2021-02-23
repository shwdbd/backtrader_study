#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   lines_shortcut.py
@Time    :   2021/02/23 19:26:23
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   缩略调用方法

datas的同义写法
lines的同义写法

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
        pass

    def next(self):
        # datas的同义写法：
        self.log("datas[0] = {0} = {1}".format(self.data, self.data0))
        self.log("datas[1] = {0}".format(self.data1))
        # lines的同义写法：


# 启动回测
def engine_run():
    # 初始化引擎
    cerebro = bt.Cerebro()
    # 给Cebro引擎添加策略
    cerebro.addstrategy(DemoStrategy)
    # 从csv文件加载数据
    data = data_tl.get_stock_daily(stock_id="600016.SH", start="20190101", end="20190103")
    cerebro.adddata(data, name="民生")
    data = data_tl.get_stock_daily(stock_id="000001.SZ", start="20190101", end="20190103")
    cerebro.adddata(data, name="平安")
    # 回测启动运行
    cerebro.run()
    # cerebro.plot()


if __name__ == '__main__':
    engine_run()
