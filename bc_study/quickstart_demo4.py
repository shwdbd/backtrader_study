#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   quickstart_demo0.py
@Time    :   2020/10/29 15:25:16
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   官方QuickStart第1个策略示例

尝试买卖的策略：
1. 如果价格连续跌两天则买入
2. 如果持仓大于等于5天则卖出

'''
import backtrader as bt
import bc_study.tushare_csv_datafeed as ts_df


# 演示用策略，每日输出开盘价
class TestStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "open" line in the data[0] dataseries
        self.dataopen = self.datas[0].open
        print("TestStrategy init function called")

    def notify_order(self, order):
        # self.log("func notify_order :")
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def next(self):
        # 输出当日开盘价
        self.log('Open, %.2f' % self.dataopen[0])

        self.log('len(self)={0}'.format(len(self)))
        if not self.position:
            if self.dataopen[0] < self.dataopen[-1]:
                if self.dataopen[-1] < self.dataopen[-2]:
                    # BUY, BUY, BUY!!! (with all possible default parameters)
                    self.log('BUY CREATE, %.2f' % self.dataopen[0])
                    self.buy()
        else:
            # Already in the market ... we might sell
            self.log('len(self)={0}, bar_executed={1}'.format(len(self), self.bar_executed))
            if len(self) >= (self.bar_executed + 5):
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE, %.2f' % self.dataopen[0])
                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()


# 启动回测
def engine_run():
    # 初始化引擎
    cerebro = bt.Cerebro()

    # 给Cebro引擎添加策略
    cerebro.addstrategy(TestStrategy)

    # 设置初始资金：
    cerebro.broker.setcash(200000.0)

    # 从csv文件加载数据
    data = ts_df.get_csv_daily_data(stock_id="600016.SH", start="20190101", end="20190120")
    cerebro.adddata(data)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    # 回测启动运行
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())


if __name__ == '__main__':
    # get_data()
    engine_run()
