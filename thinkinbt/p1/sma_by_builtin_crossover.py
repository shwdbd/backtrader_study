#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   sma_by_builtin_crossover.py
@Time    :   2021/02/25 21:02:16
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   演示内建crossover指标
'''
import backtrader as bt
import thinkinbt.p1.data_tl as data_tl
import matplotlib as plt

plt.rcParams['font.sans-serif'] = ['SimHei']  # 显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 这两行需要手动设置


class DemoStrategy(bt.Strategy):

    # 定义参数
    params = dict(
        period=10
    )

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.order = None   # 未决订单
        # 移动平均线
        self.ma = bt.ind.MovingAverageSimple(self.data, period=self.p.period)
        # Crossover
        self.crossover = bt.ind.CrossOver(self.data, self.ma)

    def next(self):
        # 如果有未决订单则什么都不做
        if self.order:
            return

        if not self.position:
            if self.crossover > 0:
                self.buy(size=1000)
        elif self.crossover < 0:
            self.sell(size=1000)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log("买单执行, {p}".format(p=order.executed.price))
            elif order.issell():
                self.log("卖单执行, {p}".format(p=order.executed.price))

        self.order = None   # 重置未决订单


# 启动回测
def engine_run():
    # 初始化引擎
    cerebro = bt.Cerebro()
    # 给Cebro引擎添加策略
    cerebro.addstrategy(DemoStrategy)
    # 设置初始资金：
    cerebro.broker.setcash(6000.0)
    # 从csv文件加载数据
    data = data_tl.get_stock_daily(
        stock_id="600016.SH", start="20190101", end="20191231")
    cerebro.adddata(data, name="民生银行")
    # 回测启动运行
    print('初始账户价值: %.2f' % cerebro.broker.getvalue())
    # 回测启动运行
    cerebro.run()
    print('最终账户价值: %.2f' % cerebro.broker.getvalue())
    cerebro.plot()


if __name__ == '__main__':
    engine_run()
