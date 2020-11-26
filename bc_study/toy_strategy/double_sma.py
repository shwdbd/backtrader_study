#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   double_sma.py
@Time    :   2020/11/26 16:17:41
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   单标的，双均线策略

使用民生银行2015年数据，做长短双均线交易

'''
import backtrader as bt
import bc_study.tushare_csv_datafeed as ts_df


class DoulbeSMAStrategy(bt.Strategy):
    """
    双均线策略
    """

    params = {"short_window": 10, "long_window": 20}

    def log(self, txt, dt=None):
        ''' log信息的功能'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # 一般用于计算指标或者预先加载数据，定义变量使用
        self.dataopen = self.datas[0].open
        self.dataclose = self.datas[0].close
        self.short_ma = bt.indicators.SMA(
            self.datas[0].close, period=self.p.short_window)
        self.long_ma = bt.indicators.SMA(
            self.datas[0].close, period=self.p.long_window)

    def notify_order(self, order):
        # 订单状态变化：
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY成交, 执行价={0}, {1}'.format(order.executed.price, order.executed.size/100))
            elif order.issell():
                self.log('SELL成交, 执行价={0}, {1}'.format(order.executed.price, order.executed.size/100))

    def next(self):
        # 判断金叉、死叉
        # self.log('Open={0}, Close={1}'.format(
        #     self.dataopen[0], self.dataclose[0]))
        # self.log('Short SMA={0}, Long SMA={1}'.format(
        #     self.short_ma[0], self.long_ma[0]))

        size = self.getposition(self.datas[0]).size

        # 做多
        if size == 0 and self.short_ma[-1] < self.long_ma[-1] and self.short_ma[0] > self.long_ma[0]:
            # 开仓
            # self.order_target_value(self.datas[0]*, target=5)
            self.buy(size=100*50)
            self.log("开仓")
            self.log('Short SMA={0}, Long SMA={1}'.format(self.short_ma[-1], self.long_ma[0]))
        # 平多
        if size > 0 and self.short_ma[-1] > self.long_ma[-1] and self.short_ma[0] < self.long_ma[0]:
            self.close(self.datas[0])
            self.log("平多")
            self.log('Short SMA={0}, Long SMA={1}'.format(self.short_ma[-1], self.long_ma[0]))


if __name__ == '__main__':
    # 初始化引擎
    cerebro = bt.Cerebro()

    # 给Cebro引擎添加策略
    cerebro.addstrategy(DoulbeSMAStrategy)

    # 设置初始资金：
    cerebro.broker.setcash(200000.0)    # 20万元

    # 从csv文件加载数据
    # 仅3天数据
    data = ts_df.get_csv_daily_data(
        stock_id="600016.SH", start="20100101", end="20150630")
    cerebro.adddata(data)

    print('初始市值: %.2f' % cerebro.broker.getvalue())
    # 回测启动运行
    result = cerebro.run()
    print('期末市值: %.2f' % cerebro.broker.getvalue())
