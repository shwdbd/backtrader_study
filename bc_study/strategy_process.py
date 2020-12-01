#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   strategy_process.py
@Time    :   2020/11/30 16:26:29
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   演示Strategy的个接口函数运行顺序


- 在__init__中计算一个5日的SMA
- 如果SMA还未计算出，则调用prenext()，否则调用next()
- 暂不涉及Order和Trade

输出的值：
初始市值: 200000.00
【策略】2019-01-10, init()
【策略】2019-01-10, start()
【策略】2019-01-02, prenext() Open=5.72, Bar数len(self)=1
【策略】2019-01-03, prenext() Open=5.63, Bar数len(self)=2
【策略】2019-01-04, prenext() Open=5.64, Bar数len(self)=3
【策略】2019-01-07, prenext() Open=5.8, Bar数len(self)=4
【策略】2019-01-08, next() Open=5.76, Bar数len(self)=5
【策略】2019-01-09, next() Open=5.78, Bar数len(self)=6
【策略】2019-01-10, next() Open=5.74, Bar数len(self)=7
【策略】2019-01-10, stop()
回测运行返回值 = [<__main__.ProcessDemoStrategy object at 0x00000215111CA408>]
期末市值: 200000.00

'''
import backtrader as bt
import bc_study.tushare_csv_datafeed as ts_df


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


# 启动回测
def engine_run():
    # 初始化引擎
    cerebro = bt.Cerebro()

    # 给Cebro引擎添加策略
    cerebro.addstrategy(ProcessDemoStrategy)

    # 设置初始资金：
    cerebro.broker.setcash(200000.0)

    # 从csv文件加载数据
    data = ts_df.get_csv_daily_data(
        stock_id="600016.SH", start="20190101", end="20190110")
    cerebro.adddata(data)

    print('初始市值: %.2f' % cerebro.broker.getvalue())
    # 回测启动运行
    result = cerebro.run()
    print("回测运行返回值 = {0}".format(result))
    print('期末市值: %.2f' % cerebro.broker.getvalue())


if __name__ == '__main__':
    engine_run()
