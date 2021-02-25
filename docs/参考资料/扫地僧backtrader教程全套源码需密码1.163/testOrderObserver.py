from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime
import os.path  # 管理路径
import sys  # 发现脚本名字
import backtrader as bt
import backtrader.feeds as btfeeds
import backtrader.indicators as btind

from backtrader.observers.orderobserver import OrderObserver


class MyStrategy(bt.Strategy):
    params = (
        ('smaperiod', 15),
        ('limitperc', 1.0),
        ('valid', 7),
    )

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.data.datetime[0]
        if isinstance(dt, float):
            dt = bt.num2date(dt)
        print('%s, %s' % (dt.isoformat(), txt))

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            self.log('ORDER ACCEPTED/SUBMITTED', dt=order.created.dt)
            self.order = order
            return

        if order.status in [order.Expired]:
            self.log('BUY EXPIRED')

        elif order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price, order.executed.value,
                          order.executed.comm))

            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price, order.executed.value,
                          order.executed.comm))

        # Set to None: new orders allowed
        self.order = None

    def __init__(self):
        # SimpleMovingAverage on main data
        sma = btind.SMA(period=self.p.smaperiod)

        # CrossOver (1: up, -1: down) close / sma
        self.crossover = btind.CrossOver(self.data.close, sma, plot=True)

        # Set to None: new ordersa allowed
        self.order = None

    def next(self):
        if self.order:
            # 有未决订单，跳过
            return

        # Check if we are in the market
        if self.position:
            if self.crossover < 0:
                self.log('SELL CREATE, %.2f' % self.data.close[0])
                self.order = self.sell()

        elif self.crossover > 0:
            plimit = self.data.close[0] * (1.0 - self.p.limitperc / 100.0)
            valid = self.data.datetime.datetime(0) + \
                datetime.timedelta(days=self.p.valid)
            self.log('BUY CREATE, %.2f' % plimit)
            self.order = self.buy(
                exectype=bt.Order.Limit, price=plimit, valid=valid)


def runstrat():
    cerebro = bt.Cerebro()

    # 获取本脚本文件所在路径
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    # 拼接得到数据文件全路径
    datapath = os.path.join(modpath, './600000qfq.csv')

    # 创建行情数据对象，加载数据
    data = bt.feeds.GenericCSVData(
        dataname=datapath,
        datetime=2,  # 日期行所在列
        open=3,  # 开盘价所在列
        high=4,  # 最高价所在列
        low=5,  # 最低价所在列
        close=6,  # 收盘价价所在列
        volume=10,  # 成交量所在列
        openinterest=-1,  # 无未平仓量列
        dtformat=('%Y%m%d'),  # 日期格式
        fromdate=datetime.datetime(2019, 3, 1),  # 起始日
        todate=datetime.datetime(2020, 5, 1))  # 结束日

    cerebro.adddata(data)  # 将行情数据对象注入引擎

    cerebro.addobserver(OrderObserver)

    cerebro.addstrategy(MyStrategy)
    cerebro.run()

    cerebro.plot()


if __name__ == '__main__':
    runstrat()