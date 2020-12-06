#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   order_exetype.py
@Time    :   2020/12/05 14:52:24
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   Order.exectype 不同成交类型的试验


试验用数据：
trade_date,open,  high,  low,   close
20000104,  17.5,  18.55, 17.2,  18.29
20000105,  18.35, 18.85, 18.0,  18.06
20000106,  18.02, 19.05, 17.75, 18.78
20000107,  19.0,  19.77, 18.9,  19.54
20000110,  19.79, 20.48, 19.77, 20.14

Market，市场单
- 4日下单，5日open(18.35)价格成交
  OUTPUT: 2000-01-05, 买单执行, 执行价=18.35，数量=10

Close，市场单
- 4日下单，5日close(18.06)价格成交
  OUTPUT: 2000-01-05, 买单执行, 执行价=18.06，数量=10

LIMIT, 限价单：
- 4日BUY单，限价17.6，无法成交
  OUTPUT: 无法成交
- 5日BUY单，限价20.00，6日18.02价格成交(开盘即成交)
  OUTPUT: 2000-01-06, 买单(oid=2)执行, 执行价=18.02，数量=10
- 6日SELL单，限价20.30，10日20.30价格成交
  OUTPUT: 2000-01-10, 卖单(oid=3)执行, 执行价=20.3，数量=-10

Stop，停止单
- 4日BUY单，价19.0，6日提交, 6日成交
- 4日BUY单，价25.0，不会提交不会成交
- 6日SELL单，价18.0，不会提交不会成交

LIMITSTOP,

trade_date,open,  high,  low,   close
20000104,  17.5,  18.55, 17.2,  18.29
20000105,  18.35, 18.85, 18.0,  18.06
20000106,  18.02, 19.05, 17.75, 18.78
20000107,  19.0,  19.77, 18.9,  19.54
20000110,  19.79, 20.48, 19.77, 20.14

StopLimit，停止限价单
- 4日BUY单，price=19, plimit=20.14，6日成交，按19成交(转为Limit Order)

'''
import backtrader as bt
import bc_study.tushare_csv_datafeed as ts_df
from backtrader.order import Order


# 基策略
class BaseOrderExetypeStrategy(bt.Strategy):
    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        pass

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # if order.status == order.Submitted:
            #     self.log('订单(oid={oid}) , Submitted'.format(oid=order.ref))
            # if order.status == order.Accepted:
            #     self.log('订单(oid={oid}) , Accepted'.format(oid=order.ref))
            return
        elif order.status in [order.Completed]:
            if order.isbuy():
                self.log('买单(oid={oid})执行, 执行价={ep}，数量={ea}'.format(oid=order.ref, ep=order.executed.price, ea=order.executed.size))
            elif order.issell():
                self.log('卖单(oid={oid})执行, 执行价={ep}，数量={ea}'.format(oid=order.ref, ep=order.executed.price, ea=order.executed.size))
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order(oid={oid}) Canceled/Margin/Rejected'.format(oid=order.ref))

    def next(self):
        pass


# 演示Market Order策略
class MarketOrderStrategy(BaseOrderExetypeStrategy):

    def next(self):
        # 第1天，下单
        if len(self) == 1:
            order = self.buy(size=10, price=100, exectype=Order.Market)
            if order:
                self.log("下单BUY单(oid={id}), price={p}".format(id=order.ref, p=order.price))


# 演示Close Order策略
class CloseOrderStrategy(BaseOrderExetypeStrategy):

    def next(self):
        # 第1天，下单
        if len(self) == 1:
            order = self.buy(size=10, price=100, exectype=Order.Close)
            if order:
                self.log("下单BUY单(oid={id}), price={p}".format(id=order.ref, p=order.price))


# 演示Limit Order策略
class LimitOrderStrategy(BaseOrderExetypeStrategy):
    # TODO 添加valid参数，
    # valid = self.data.datetime.date(0) + datetime.timedelta(days=self.p.valid)

    def next(self):
        # 第1天，4日BUY单，限价17.6，无法成交
        if len(self) == 1:
            order = self.buy(size=10, price=17.60, exectype=Order.Limit)
            if order:
                self.log("下单BUY单(oid={id}), price={p}".format(id=order.ref, p=order.price))
        if len(self) == 2:
            order = self.buy(size=10, price=20.00, exectype=Order.Limit)
            if order:
                self.log("下单BUY单(oid={id}), price={p}".format(id=order.ref, p=order.price))
        if len(self) == 3:
            order = self.sell(size=10, price=20.30, exectype=Order.Limit)
            if order:
                self.log("下单SELL单(oid={id}), price={p}".format(id=order.ref, p=order.price))


# 演示Stop Order策略
class StopOrderStrategy(BaseOrderExetypeStrategy):

    def next(self):
        # 第1天，4日BUY单，价19
        if len(self) == 1:
            order = self.buy(size=10, price=19, exectype=Order.Stop)
            if order:
                self.log("下单BUY单(oid={id}), price={p}".format(id=order.ref, p=order.price))
            order = self.buy(size=10, price=25, exectype=Order.Stop)
            if order:
                self.log("下单BUY单(oid={id}), price={p}".format(id=order.ref, p=order.price))
        if len(self) == 3:
            order = self.sell(size=10, price=18, exectype=Order.Stop)
            if order:
                self.log("下单SELL单(oid={id}), price={p}".format(id=order.ref, p=order.price))


# 演示StopLimit Order策略
class StopLimitOrderStrategy(BaseOrderExetypeStrategy):

    def next(self):
        # 第1天，4日BUY单，价19
        if len(self) == 1:
            order = self.buy(size=10, price=19, plimit=20.14, exectype=Order.StopLimit)
            if order:
                self.log("下单BUY单(oid={id}), price={p}, plimit={pl}".format(id=order.ref, p=order.price, pl=order.plimit))


# 启动回测
def engine_run():
    # 初始化引擎
    cerebro = bt.Cerebro()

    # 给Cebro引擎添加策略
    cerebro.addstrategy(StopLimitOrderStrategy)

    # 设置初始资金：
    cerebro.broker.setcash(200000.0)

    # 从csv文件加载数据
    # 仅3天数据
    data = ts_df.get_csv_daily_data(
        stock_id="000001.SZ", start="20000104", end="20000110")
    cerebro.adddata(data)

    # 回测启动运行
    cerebro.run()


if __name__ == '__main__':
    engine_run()
