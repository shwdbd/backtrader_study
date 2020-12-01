#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   analyzer_process.py
@Time    :   2020/11/28 10:43:18
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   分析器Analyzer的执行逻辑探索
'''
import backtrader as bt
import bc_study.tushare_csv_datafeed as ts_df
from backtrader import Analyzer


# 演示用策略，每日输出开盘价
class ProcessDemoStrategy(bt.Strategy):

    def log(self, text, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('【策略】%s, %s' % (dt.isoformat(), text))

    def __init__(self):
        self.log("init()")
        # 建立对于DataFeed的Open价格的引用参数
        self.dataopen = self.datas[0].open
        # 计算一个SMA，窗口指标
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=5)

    def start(self):
        self.log("start()")

    def prenext(self):
        # SMA还未计算成功，会有一个时间窗口
        self.log("prenext() Open={0}, Bar数len(self)={1}".format(self.dataopen[0], len(self)))

    def next(self):
        # 输出当日价格
        self.log('next() Open={0}, Bar数len(self)={1}'.format(self.dataopen[0], len(self)))

    def stop(self):
        self.log("stop()")


# Analyzer每个Bar执行一次计数
class MyAnalyzer(Analyzer):

    # params = (('timeframe', TimeFrame.Years), ('riskfreerate', 0.01),)

    def __init__(self):
        self.log(" __init__() ")
        # self.anret = AnnualReturn()

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('【分析器】%s, %s' % (dt.isoformat(), txt))

    def start(self):
        # Not needed ... but could be used
        self.log(" start() ")

    def prenext(self):
        self.log(" prenext() ")

    def next(self):
        # Not needed ... but could be used
        self.log(" next() ")
        self.log("策略对象的引用: {0}".format(self.strategy))
        self.log("今日收盘价: {0}".format(self.datas[0].close[0]))

    def nextstart(self):
        self.log(" nextstart() ")

    def stop(self):
        self.log(" stop() ")

    def get_analysis(self):
        return 999


# 启动回测
def engine_run():
    # 初始化引擎
    cerebro = bt.Cerebro()

    # 给Cebro引擎添加策略
    cerebro.addstrategy(ProcessDemoStrategy)

    # Analyzer
    cerebro.addanalyzer(MyAnalyzer, _name='myanalyzer')

    # 设置初始资金：
    cerebro.broker.setcash(200000.0)

    # 从csv文件加载数据
    data = ts_df.get_csv_daily_data(stock_id="600016.SH", start="20190101", end="20190110")
    cerebro.adddata(data)

    print('初始市值: %.2f' % cerebro.broker.getvalue())
    # 回测启动运行
    result = cerebro.run()
    print("回测运行返回值 = {0}".format(result))
    print('期末市值: %.2f' % cerebro.broker.getvalue())


if __name__ == '__main__':
    engine_run()
