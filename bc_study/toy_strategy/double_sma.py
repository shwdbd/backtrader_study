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

TODO:
1. 记录每次Trade的 胜负结果、盈亏数字
2. 计算总的Shape比率   Analyzer
3. 参数优化(长短周期的参数)
4. 图形输出
5. 动态计算sizer
6. 增加 notify_trade

'''
import backtrader as bt
import bc_study.tushare_csv_datafeed as ts_df
import backtrader.analyzers as btanalyzers


class DoulbeSMAStrategy(bt.Strategy):
    """
    双均线金叉死叉策略
    """
    # 参数：长短均线的日期
    params = {"short_window": 20, "long_window": 50}

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
        self.log("完成 长[{0}]短[{1}]SMA 数据的计算".format(self.p.short_window, self.p.long_window))

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

        # 做多
        if size == 0 and self.short_ma[-1] < self.long_ma[-1] and self.short_ma[0] > self.long_ma[0]:
            # 开仓
            # self.order_target_value(self.datas[0]*, target=5)
            order = self.buy(size=100*5)
            self.log("金叉，买{0}, Short SMA yes={1}, Long SMA today={2}".format(order.size, self.short_ma[-1], self.long_ma[0]))
        # 平多
        if size > 0 and self.short_ma[-1] > self.long_ma[-1] and self.short_ma[0] < self.long_ma[0]:
            order = self.close(self.datas[0])
            self.log("死叉，卖{0}, Short SMA yes={1}, Long SMA today={2}".format(order.size, self.short_ma[-1], self.long_ma[0]))


if __name__ == '__main__':
    # 初始化引擎
    cerebro = bt.Cerebro()

    # 给Cebro引擎添加策略
    cerebro.addstrategy(DoulbeSMAStrategy)

    # 添加分析器
    cerebro.addanalyzer(btanalyzers.SharpeRatio, _name='mysharpe')

    # 设置初始资金：
    cerebro.broker.setcash(100000.0)    # 10万元

    # 从csv文件加载数据
    # 仅3天数据
    data = ts_df.get_csv_daily_data(
        stock_id="000001.SZ", start="20150101", end="20161231")
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
