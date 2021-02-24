#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   do_sell_trade.py
@Time    :   2021/02/24 18:04:36
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   模拟做空交易

看一下postion，如果为none，则卖出
结果是可以做空单。

逻辑：
1. 第一天就卖出100份
2. 查看执行情况

输出：
1. 控制台输出：
初始账户价值: 10000.00
2019-01-02, 无头寸
2019-01-03, 卖单执行, 5.63
2019-01-03, --- Position Begin
- Size: -100
- Price: 5.63
- Price orig: 0.0
- Closed: 0
- Opened: -100
- Adjbase: 5.67
--- Position End
2019-01-04, --- Position Begin
- Size: -100
- Price: 5.63
- Price orig: 0.0
- Closed: 0
- Opened: -100
- Adjbase: 5.78
--- Position End
最终账户价值: 9985.00


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

        if self.position:
            self.log(self.position)
        else:
            self.log('无头寸')
            self.sell(size=100)

        # # 下单
        # self.order = self.buy(size=100)     # 买一手

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
    # 从csv文件加载数据
    data = data_tl.get_stock_daily(stock_id="600016.SH", start="20190101", end="20190105")
    cerebro.adddata(data, name="民生银行")
    # 回测启动运行
    print('初始账户价值: %.2f' % cerebro.broker.getvalue())
    # 回测启动运行
    cerebro.run()
    print('最终账户价值: %.2f' % cerebro.broker.getvalue())
    # cerebro.plot()


if __name__ == '__main__':
    engine_run()
