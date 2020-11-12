#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   quickstart_demo0.py
@Time    :   2020/10/29 15:25:16
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   官方QuickStart示例代码

尝试买入的策略：
1. 买入的尝试，如果价格连续跌两天则买入

'''
import backtrader as bt
import bc_study.tushare_csv_datafeed as ts_df


# 演示用策略，每日输出开盘价
class TestStrategy(bt.Strategy):

    def log(self, text, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), text))

    def __init__(self):
        print("【策略】init 函数 开始")
        # 建立对于DataFeed的Open/Close价格的引用参数
        self.dataopen = self.datas[0].open
        self.dataclose = self.datas[0].close
        print("【策略】init 函数 结束")

    def notify_order(self, order):
        # 订单状态变化：

        self.log("【Order通知】")
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
        # 输出当日价格
        self.log('Open={0}, 昨Open={1}, 前Open={2}'.format(self.dataopen[0], self.dataopen[-1], self.dataopen[-2]))

        if self.dataopen[0] < self.dataopen[-1]:
            # if self.dataopen[-1] < self.dataopen[-2]:
            # 条件触发，BUY, BUY, BUY!!! (with all possible default parameters)
            self.log('BUY 订单创建, 订单价=%.2f' % self.dataopen[0])
            order = self.buy()
            if order:
                print("生成的订单对象：\n{0}".format(order))

        # if self.position:
        #     print("{0}".format(self.position))

        # 打印交易后的资金市值
        # next中只是下单，还未成交
        # print('Portfolio Value: %.2f' % self.cerebro.broker.getvalue())


# 启动回测
def engine_run():
    # 初始化引擎
    cerebro = bt.Cerebro()

    # 给Cebro引擎添加策略
    cerebro.addstrategy(TestStrategy)

    # 设置初始资金：
    cerebro.broker.setcash(200000.0)

    # 从csv文件加载数据
    data = ts_df.get_csv_daily_data(stock_id="600016.SH", start="20190101", end="20190106")
    cerebro.adddata(data)

    print('初始市值: %.2f' % cerebro.broker.getvalue())
    # 回测启动运行
    result = cerebro.run()
    print("回测运行返回值 = {0}".format(result))
    print('期末市值: %.2f' % cerebro.broker.getvalue())


if __name__ == '__main__':
    engine_run()
