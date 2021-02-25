#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   get_trades_history.py
@Time    :   2021/02/25 19:50:13
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   查看交易的详细历史明细

查看构成Trade的每个详细执行Order步骤


逻辑：
1. 第一天，下单买100股，卖50股
2. 第二天，昨日单执行，Trade1建立，然后再下50股卖单
3. 第三天，昨日卖单执行，Trade1结束
Trade关闭后输出所有历史步骤

输出：
初始账户价值: 200000.00
2019-01-03, 买单执行, 5.63
2019-01-03, 卖单执行, 5.63
2019-01-03, Trade id = 1 (size=100)
2019-01-04, 卖单执行, 5.64
2019-01-04, Trade id = 1 (size=0)
2019-01-04, 毛收益 0.50
操作1
Trade状态:AutoOrderedDict([('status', 1), ('dt', 737062.9999999999), ('barlen', 0), ('size', 100), ('price', 5.63), ('value', 563.0), ('pnl', 0.0), ('pnlcomm', 0.0), ('tz', None)]) 
Trade事件:AutoOrderedDict([('order', <backtrader.order.BuyOrder object at 0x000001E368AA4888>), ('size', 100), ('price', 5.63), ('commission', 0.0)])
操作2
Trade状态:AutoOrderedDict([('status', 1), ('dt', 737062.9999999999), ('barlen', 0), ('size', 50), ('price', 5.63), ('value', 281.5), ('pnl', 0.0), ('pnlcomm', 0.0), ('tz', None)])     
Trade事件:AutoOrderedDict([('order', <backtrader.order.SellOrder object at 0x000001E368AA4948>), ('size', -50), ('price', 5.63), ('commission', 0.0)])
操作3
Trade状态:AutoOrderedDict([('status', 2), ('dt', 737063.9999999999), ('barlen', 1), ('size', 0), ('price', 5.63), ('value', 0.0), ('pnl', 0.49999999999998934)
, ('pnlcomm', 0.49999999999998934), ('tz', None)])
Trade事件:AutoOrderedDict([('order', <backtrader.order.SellOrder object at 0x000001E368AA4EC8>), ('size', -50), ('price', 5.64), ('commission', 0.0)])
最终账户价值: 200000.50

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
        self.order = None   # 未决订单

    def next(self):
        # 如果有未决订单则什么都不做
        if self.order:
            self.log("存在未决订单")
            return

        days = len(self.data)
        if days == 1:
            # 第1天 20190102
            self.order = self.buy(size=100)
            self.order = self.sell(size=50)
        elif days == 2:
            # 第2天 20190103
            self.order = self.sell(size=50)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log("买单执行, {p}".format(p=order.executed.price))
            elif order.issell():
                self.log("卖单执行, {p}".format(p=order.executed.price))

        self.order = None   # 重置未决订单

    def notify_trade(self, trade):
        self.log("Trade id = {0} (size={1})".format(trade.ref, trade.size))

        print(trade.status)
        print(trade.getstatusname())

        if trade.isclosed:
            self.log("毛收益 %0.2f" % trade.pnl)
            # 历史明细：
            for idx, h in enumerate(trade.history):
                print("操作{0}".format(idx+1))
                print("Trade状态:{0}".format(h.status))
                print("Trade事件:{0}".format(h.event))


# 启动回测
def engine_run():
    # 初始化引擎
    cerebro = bt.Cerebro(tradehistory=True)
    # 给Cebro引擎添加策略
    cerebro.addstrategy(DemoStrategy)
    # 设置初始资金：
    cerebro.broker.setcash(200000.0)
    # 从csv文件加载数据
    data = data_tl.get_stock_daily(stock_id="600016.SH", start="20190101", end="20190115")
    cerebro.adddata(data, name="民生银行")
    # 回测启动运行
    print('初始账户价值: %.2f' % cerebro.broker.getvalue())
    # 回测启动运行
    cerebro.run()
    print('最终账户价值: %.2f' % cerebro.broker.getvalue())
    # cerebro.plot()


if __name__ == '__main__':
    engine_run()
