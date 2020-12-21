#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   target_order.py
@Time    :   2020/12/21 14:58:13
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   Target订单

逻辑：
T1, 目标7
T2，目标2
T3，目标3

执行结果：
2015-01-05, 头寸：size=0
2015-01-06, Order(oid=1)执行, 方向=0, 数量=7
2015-01-06, 头寸：size=7
2015-01-07, Order(oid=2)执行, 方向=1, 数量=-5
2015-01-07, 头寸：size=2
2015-01-08, Order(oid=3)执行, 方向=0, 数量=1
2015-01-08, 头寸：size=3

'''
import backtrader as bt
import bc_study.tushare_csv_datafeed as ts_df


class DemoForTargetOrderStrategy(bt.Strategy):
    """
    目标订单试验

    """

    def log(self, txt, dt=None):
        """ log信息的功能 """
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.dataopen = self.datas[0].open

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        elif order.status in [order.Completed]:
            self.log('Order(oid={oid})执行, 方向={dir}, 数量={size}'.format(
                oid=order.ref, dir=order.ordtype, size=order.size))
            self.log("头寸：size={0}".format(self.position.size))
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            pass

    def next(self):
        if len(self) == 1:
            # 初始状态
            self.log("头寸：size={0}".format(self.position.size))
            # 下单：
            self.order_target_size(target=7)
        elif len(self) == 2:
            self.order_target_size(target=2)
        elif len(self) == 3:
            self.order_target_size(target=3)


if __name__ == '__main__':
    # 初始化引擎
    cerebro = bt.Cerebro()

    # 给Cebro引擎添加策略
    cerebro.addstrategy(DemoForTargetOrderStrategy)

    # 设置初始资金：
    cerebro.broker.setcash(100000.0)    # 10万元

    # 从csv文件加载数据
    # 仅3天数据
    data = ts_df.get_csv_daily_data(
        stock_id="000001.SZ", start="20150101", end="20150110")
    cerebro.adddata(data)

    # 回测启动运行
    cerebro.run()
