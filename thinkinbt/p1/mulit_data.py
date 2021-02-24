#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   mulit_data.py
@Time    :   2021/02/24 15:33:23
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   读取多个数据源

逻辑：
1. 从2个csv文件中读取两个数据源，并分别命名

2. 控制台输出
2019-01-02, ['民生银行', '平安银行']
2019-01-02, 5.65
2019-01-02, 9.19

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
        self.log(self.getdatanames())
        self.log(self.getdatabyname('民生银行').close[0])
        self.log(self.getdatabyname('平安银行').close[0])


# 启动回测
def engine_run():
    # 初始化引擎
    cerebro = bt.Cerebro()
    # 给Cebro引擎添加策略
    cerebro.addstrategy(DemoStrategy)
    # 从csv文件加载数据
    data = data_tl.get_stock_daily(stock_id="600016.SH", start="20190101", end="20190103")
    cerebro.adddata(data, name="民生银行")
    data = data_tl.get_stock_daily(stock_id="000001.SZ", start="20190101", end="20190103")
    cerebro.adddata(data, name="平安银行")
    # 回测启动运行
    cerebro.run()
    # cerebro.plot()


if __name__ == '__main__':
    engine_run()
