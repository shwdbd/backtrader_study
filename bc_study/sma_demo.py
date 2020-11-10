#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   quickstart_demo0.py
@Time    :   2020/10/29 15:25:16
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   最简单的SMA均线策略 示例

20日均线，如果今天开盘价小于SMA则买入，大于SMA则卖

具备功能：
- 电池函数
- 个性化参数


'''
import backtrader as bt
import bc_study.tushare_csv_datafeed as ts_df


# 最简单的SMA策略
class SMAStrategy(bt.Strategy):

    params = (
        ('sma_window', 25),
    )

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # 建立开盘价的引用
        self.dataopen = self.datas[0].open
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.sma_window)

    def next(self):
        # Simply log the closing price of the series from the reference
        # self.log('Open, %.2f' % self.dataopen[0])
        # self.log('SMA last, %.2f' % self.sma[-1])

        if not self.position:
            if self.dataopen[0] < self.sma[-1]:
                # 买入
                # self.log('买入, 挂单价格 = %.2f' % self.dataopen[0])
                self.buy()
        else:
            if self.dataopen[0] > self.sma[-1]:
                # 卖出
                # self.log('卖出, 挂单价格 = %.2f' % self.dataopen[0])
                self.sell()

    def stop(self):
        self.log('(MA Period %2d) Ending Value %.2f' %
                 (self.params.sma_window, self.broker.getvalue()))


# 启动回测
def engine_run():
    # 初始化引擎
    cerebro = bt.Cerebro()

    # 给Cebro引擎添加策略
    cerebro.addstrategy(SMAStrategy)

    # 设置初始资金：
    cerebro.broker.setcash(200000.0)
    # Set the commission - 0.1% ... divide by 100 to remove the %
    cerebro.broker.setcommission(commission=0.001)

    periods = range(20, 120)
    cerebro.optstrategy(SMAStrategy, sma_window=periods)
    cerebro.addsizer(bt.sizers.FixedSize, stake=1)

    # 从csv文件加载数据
    data = ts_df.get_csv_daily_data(stock_id="600016.SH", start="20190101", end="20191231")
    cerebro.adddata(data)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    # 回测启动运行
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())


if __name__ == '__main__':
    # get_data()
    engine_run()
