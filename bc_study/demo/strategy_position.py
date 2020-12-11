#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   strategy_position.py
@Time    :   2020/12/11 11:01:42
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   策略Position

学习Position的用法

- postion什么时候产生对象？
- 连做两笔order，postion的值是什么？

OUTPUT:
2015-01-05, 头寸，单价=0.0，规模=0
2015-01-05, 第1天，下市场买单10
2015-01-06, 买单(oid=1)执行, 开盘价=15.85, 成交价=15.85，滑点差价=0.0
2015-01-06, 第2天，下市场卖单5
2015-01-07, 买单(oid=2)执行, 开盘价=15.56, 成交价=15.559999999999999，滑点差价=-1.7763568394002505e-15
2015-01-07, 头寸，单价=15.85，规模=5

'''
import backtrader as bt
import bc_study.tushare_csv_datafeed as ts_df


class PositionStrategy(bt.Strategy):
    """
    查看头寸

    T1，下BUY单10
    T2，下SELL单5
    T3，看position情况
    """

    def log(self, txt, dt=None):
        ''' log信息的功能'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.dataopen = self.datas[0].open
        pass

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        elif order.status in [order.Completed]:
            self.log('买单(oid={oid})执行, 开盘价={open}, 成交价={pexec}，滑点差价={sp}'.format(
                oid=order.ref, pexec=order.executed.price, open=self.dataopen[0], sp=(order.executed.price-self.dataopen[0])))
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            pass

    def next(self):
        if len(self) == 1:
            self.log("头寸，单价={p}，规模={s}".format(p=self.position.price, s=self.position.size))     # 空头寸
            order = self.buy(size=10, exectype=bt.Order.Market)
            if order:
                self.log("第1天，下市场买单10")
        elif len(self) == 2:
            order = self.sell(size=5, exectype=bt.Order.Market)
            if order:
                self.log("第2天，下市场卖单5")
        elif len(self) == 3:
            self.log("头寸，单价={p}，规模={s}".format(p=self.position.price, s=self.position.size))


if __name__ == '__main__':
    # 初始化引擎
    cerebro = bt.Cerebro()

    # 给Cebro引擎添加策略
    cerebro.addstrategy(PositionStrategy)

    # 设置初始资金：
    cerebro.broker.setcash(100000.0)    # 10万元

    # 从csv文件加载数据
    # 仅3天数据
    data = ts_df.get_csv_daily_data(
        stock_id="000001.SZ", start="20150101", end="20150110")
    cerebro.adddata(data)

    # 回测启动运行
    cerebro.run()
