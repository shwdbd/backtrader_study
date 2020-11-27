#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   two_stock_datafeed.py
@Time    :   2020/11/27 13:33:27
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   同时读取两个股票DataFeed的示例

读取两个股票的日线数据，每日输出close价格

'''

import backtrader as bt
import bc_study.tushare_csv_datafeed as ts_df


# 演示用策略，每日输出开盘价
class DemoStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # 建立对于DataFeed的Open/Close价格的引用参数
        self.dataclose_A = self.datas[0].close
        self.dataclose_B = self.datas[1].close

    def next(self):
        self.log('A Close={0}'.format(self.dataclose_A[0]))
        self.log('B Close={0}'.format(self.dataclose_B[0]))


# 启动回测
def engine_run():
    # 初始化引擎
    cerebro = bt.Cerebro()

    # 给Cebro引擎添加策略
    cerebro.addstrategy(DemoStrategy)

    # 设置初始资金：
    cerebro.broker.setcash(200000.0)

    # 加载两个股票的数据
    data1 = ts_df.get_csv_daily_data(stock_id="600016.SH", start="20190101", end="20190105")
    cerebro.adddata(data1)
    data2 = ts_df.get_csv_daily_data(stock_id="000001.SZ", start="20190101", end="20190105")
    cerebro.adddata(data2)

    print('初始市值: %.2f' % cerebro.broker.getvalue())
    # 回测启动运行
    result = cerebro.run()
    print("回测运行返回值 = {0}".format(result))
    print('期末市值: %.2f' % cerebro.broker.getvalue())


if __name__ == '__main__':
    engine_run()
