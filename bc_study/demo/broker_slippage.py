#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   broker_slippage.py
@Time    :   2020/12/08 18:18:49
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   Broker的滑点示例

- 展示买入/卖出的时间点，增加滑点后
不同Order类型，滑点的实现不同

- 滑点分为 fixed和perc两种，分别是按金额固定滑点和按比例滑点。
- 不同的


MarketOrder的滑点：
- 设置滑点 1%
- T日下单，T+1日成交
- T+1日的开盘价，成交价分别是多少，差距是多少？差距是否等于1%

'''
import backtrader as bt
import bc_study.tushare_csv_datafeed as ts_df


class MarketOrderWithSlippageStrategy(bt.Strategy):
    """
    市场单，加入滑点的情况
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
        # self.log("Open={0}".format(self.dataopen[0]))
        if len(self) == 1:
            # 固定金额滑点
            order = self.buy(size=10, exectype=bt.Order.Market)
            if order:
                self.log("第一天，下市场买单")
        elif len(self) == 2:
            # 固定金额滑点
            order = self.sell(size=10, exectype=bt.Order.Market)
            if order:
                self.log("第2天，下市场卖单")


if __name__ == '__main__':
    # 初始化引擎
    cerebro = bt.Cerebro()

    # 给Cebro引擎添加策略
    cerebro.addstrategy(MarketOrderWithSlippageStrategy)

    # 设置初始资金：
    cerebro.broker.setcash(100000.0)    # 10万元
    # cerebro.broker.set_slippage_fixed(fixed=0.01)
    cerebro.broker.set_slippage_perc(perc=0.01)

    # 从csv文件加载数据
    # 仅3天数据
    data = ts_df.get_csv_daily_data(
        stock_id="000001.SZ", start="20150101", end="20150110")
    cerebro.adddata(data)

    # 回测启动运行
    cerebro.run()
