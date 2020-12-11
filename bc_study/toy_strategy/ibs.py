#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   ibs.py
@Time    :   2020/12/11 14:06:28
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   均值回归IBS策略

IBS（Internal Bar Strength）内部条形强度

ibs = (Pc - Pl) / (Ph - Pl)

如果ibs>0.9，则sell
如果isb<0.1, 则buy

'''
import backtrader as bt
import bc_study.tushare_csv_datafeed as ts_df
import backtrader.analyzers as btanalyzers


class IBSStrategy(bt.Strategy):
    """
    IBS（Internal Bar Strength）内部条形强度 策略
    """
    # # 参数：长短均线的日期
    # params = {"short_window": 20, "long_window": 50}

    def log(self, txt, dt=None):
        ''' log信息的功能'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # 一般用于计算指标或者预先加载数据，定义变量使用
        self.price_low = self.datas[0].low
        self.price_close = self.datas[0].close
        self.price_high = self.datas[0].high
        # ibs
        self.ibs = (self.price_close - self.price_low) / (self.price_high - self.price_low)

    def notify_order(self, order):
        # 订单状态变化：
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY成交, 执行价={0}, {1}'.format(order.executed.price, order.executed.size))
            elif order.issell():
                self.log('SELL成交, 执行价={0}, {1}'.format(order.executed.price, order.executed.size))

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('交易结束, 毛利润 %.2f, 净利润 %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        # 当前持有头寸
        size = self.getposition(self.datas[0]).size

        if self.ibs[0] < 0.1:
            # 买入
            self.buy(exectype=bt.Order.Market, size=100*100)
        elif size > 0 and self.ibs[0] > 0.9:
            # 卖出
            self.close(self.datas[0])


if __name__ == '__main__':
    # 初始化引擎
    cerebro = bt.Cerebro()

    # 给Cebro引擎添加策略
    cerebro.addstrategy(IBSStrategy)

    # 添加分析器
    cerebro.addanalyzer(btanalyzers.SharpeRatio, _name='mysharpe')

    # 设置初始资金：
    cerebro.broker.setcash(100*10000.0)    # 10万元

    # 从csv文件加载数据
    # 仅3天数据
    data = ts_df.get_csv_daily_data(
        stock_id="000001.SZ", start="20190101", end="20191231")
    cerebro.adddata(data)

    print('初始市值: %.2f' % cerebro.broker.getvalue())
    # 回测启动运行
    result = cerebro.run()
    thestrat = result[0]
    print('期末市值: %.2f' % cerebro.broker.getvalue())

    # 性能输出：
    print('夏普率:', thestrat.analyzers.mysharpe.get_analysis())

    # 绘图：
    cerebro.plot()
