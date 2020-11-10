#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   first_strategy.py
@Time    :   2020/10/22 22:21:38
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   第一个测试用策略，打印当日收盘价
'''
import backtrader as bt
import bc_study.tushare_csv_datafeed as ts_df


class MyStrategy(bt.Strategy):

    def __init__(self):
        # 引用data[0]中的收盘价格数据
        # backtrader.linebuffer.LineBuffer
        self.dataclose = self.datas[0].close
        print(self.dataclose)
        print("init")
        pass

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print("%s, %s" % (dt.isoformat(), txt))

    def next(self):
        # print("next函数")
        # self.log("next函数, Close, %.2f" % self.dataclose[0])
        pass


if __name__ == "__main__":
    # 初始化Cebro引擎
    cerebro = bt.Cerebro()

    # 给Cebro引擎添加策略
    cerebro.addstrategy(MyStrategy)

    # # 给Cebro引擎添加数据
    data = ts_df.get_csv_daily_data(stock_id="600016.SH")
    print(data)
    cerebro.adddata(data)

    # 设置初始资金
    cerebro.broker.setcash(100000.0)
    print("初始资金:%.2f" % cerebro.broker.getvalue())
    cerebro.run()
    print("期末资金:%.2f" % cerebro.broker.getvalue())
