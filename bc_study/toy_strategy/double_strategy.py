#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   double_strategy.py
@Time    :   2020/12/03 15:05:41
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   尝试，同时运行两个策略

- 两个策略，分别在第3，5日买入，第4，6日平仓

- 一个Analyzer是否可以针对两个策略？

执行顺序: A、B策略交替执行
返回值：list，N个result对象
共享一个broker
分析器是针对每个策略，都执行一遍

'''
import backtrader as bt
import bc_study.tushare_csv_datafeed as ts_df
from backtrader import Analyzer


# 策略A，3日买，5日卖
class MyStrategy_A(bt.Strategy):

    def log(self, text, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('【策略A】%s, %s' % (dt.isoformat(), text))

    def __init__(self):
        self.log("__init__()")
        self.dataopen = self.datas[0].open

    def next(self):
        # 输出当日价格
        self.log('Open={0}, 昨Open={1}, 前Open={2}'.format(self.dataopen[0], self.dataopen[-1], self.dataopen[-2]))

        day = len(self)
        if day == 3:
            self.buy()
            self.log("A 买入")
        elif day == 5:
            self.close()
            self.log("A 平仓")


# 策略B，2日买，6日卖
class MyStrategy_B(bt.Strategy):

    def log(self, text, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('【策略B】%s, %s' % (dt.isoformat(), text))

    def __init__(self):
        self.log("__init__()")
        self.dataopen = self.datas[0].open

    def next(self):
        # 输出当日价格
        self.log('Open={0}, 昨Open={1}, 前Open={2}'.format(self.dataopen[0], self.dataopen[-1], self.dataopen[-2]))

        day = len(self)
        if day == 2:
            self.buy()
            self.log("B 买入")
        elif day == 6:
            self.close()
            self.log("B 平仓")


# Analyzer A
class MyAnalyzerA(Analyzer):

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('【分析器A】%s, %s' % (dt.isoformat(), txt))

    def next(self):
        # 针对策略的调用
        # self.log("策略对象的引用: {0}".format(self.strategy))

        self.log("今日收盘价: {0}".format(self.datas[0].close[0]))

    def get_analysis(self):
        return "分析A结果"


# 启动回测
def engine_run():
    # 初始化引擎
    cerebro = bt.Cerebro()

    # 给Cebro引擎添加策略
    cerebro.addstrategy(MyStrategy_A)
    cerebro.addstrategy(MyStrategy_B)

    # Analyzer
    cerebro.addanalyzer(MyAnalyzerA, _name='analyzer_a')

    # 设置初始资金：
    cerebro.broker.setcash(10000.0)

    # 从csv文件加载数据
    data = ts_df.get_csv_daily_data(stock_id="600016.SH", start="20190101", end="20190115")
    cerebro.adddata(data)

    print('初始市值: %.2f' % cerebro.broker.getvalue())
    # 回测启动运行
    result = cerebro.run()
    print("回测运行返回值 = {0}".format(result))
    print("LEN(返回值) = {0}".format(len(result)))
    print('期末市值: %.2f' % cerebro.broker.getvalue())

    # 分析器结果
    print("分析器 A = {0}".format(result[0].analyzers.analyzer_a.get_analysis()))


if __name__ == '__main__':
    engine_run()
