#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   visit_future_data.py
@Time    :   2021/02/24 16:05:07
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   在next中尝试访问未来数据

默认情况，next()中可以访问未来数据。

逻辑：
1. 加载2019-01-01到2019-01-05的数据

输出：
1. 控制台输出：
2019-01-02, 今日收盘：5.65
2019-01-02, 前两日收盘：5.67
2019-01-02, 下一日收盘：5.67
2019-01-03, 今日收盘：5.67
2019-01-03, 前两日收盘：5.78
2019-01-03, 下一日收盘：5.78
2019-01-04, 今日收盘：5.78
2019-01-04, 前两日收盘：5.65
2019-01-04, 最后一日，未来数据未加载！


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
        self.log("今日收盘：{0}".format(self.data.close[0]))
        self.log("前两日收盘：{0}".format(self.data.close[-2]))
        try:
            self.log("下一日收盘：{0}".format(self.data.close[1]))
        except IndexError:
            self.log("最后一日，未来数据未加载！")


# 启动回测
def engine_run():
    # 初始化引擎
    cerebro = bt.Cerebro()
    # 给Cebro引擎添加策略
    cerebro.addstrategy(DemoStrategy)
    # 从csv文件加载数据
    data = data_tl.get_stock_daily(stock_id="600016.SH", start="20190101", end="20190105")
    cerebro.adddata(data, name="民生银行")
    # 回测启动运行
    cerebro.run()
    # cerebro.plot()


if __name__ == '__main__':
    engine_run()
