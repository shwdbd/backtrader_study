#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   get_datetime_in_next.py
@Time    :   2021/02/23 17:07:37
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   在next()函数中取当前时间与日期

逻辑：
1. 数据运行5天时间；
2. 在next中输出日期和时间

输出：
1. 控制台输出：
初始账户价值: 200000.00
2019-01-02, --------------------
2019-01-02, 策略时间
2019-01-02, 当前时间 self.datetime.datetime() : 2019-01-02 23:59:59.999989
2019-01-02, 当前日期 self.datetime.date() : 2019-01-02
2019-01-02, 年 : 2019
2019-01-02, 月 : 1
2019-01-02, 日 : 2
2019-01-02, 小时 : 23
2019-01-02,
2019-01-02, 数据时间
2019-01-02, 当前Bar时间 self.datas[0].datetime.datetime() : 2019-01-02 23:59:59.999989
2019-01-02, 当前Bar日期 self.datas[0].datetime.date() : 2019-01-02
2019-01-03, --------------------
2019-01-03, 策略时间
2019-01-03, 当前时间 self.datetime.datetime() : 2019-01-03 23:59:59.999989
2019-01-03, 当前日期 self.datetime.date() : 2019-01-03
2019-01-03, 年 : 2019
2019-01-03, 月 : 1
2019-01-03, 日 : 3
2019-01-03, 小时 : 23
2019-01-03,
2019-01-03, 数据时间
2019-01-03, 当前Bar时间 self.datas[0].datetime.datetime() : 2019-01-03 23:59:59.999989
2019-01-03, 当前Bar日期 self.datas[0].datetime.date() : 2019-01-03
2019-01-04, --------------------
2019-01-04, 策略时间
2019-01-04, 当前时间 self.datetime.datetime() : 2019-01-04 23:59:59.999989
2019-01-04, 当前日期 self.datetime.date() : 2019-01-04
2019-01-04, 年 : 2019
2019-01-04, 月 : 1
2019-01-04, 日 : 4
2019-01-04, 小时 : 23
2019-01-04,
2019-01-04, 数据时间
2019-01-04, 当前Bar时间 self.datas[0].datetime.datetime() : 2019-01-04 23:59:59.999989
2019-01-04, 当前Bar日期 self.datas[0].datetime.date() : 2019-01-04
最终账户价值: 200000.00

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
        pass

    def next(self):
        self.log("-"*20)
        self.log("策略时间")
        self.log("当前时间 self.datetime.datetime() : {0}".format(self.datetime.datetime()))
        self.log("当前日期 self.datetime.date() : {0}".format(self.datetime.date()))
        self.log("年 : {0}".format(self.datetime.datetime().year))
        self.log("月 : {0}".format(self.datetime.datetime().month))
        self.log("日 : {0}".format(self.datetime.datetime().day))
        self.log("小时 : {0}".format(self.datetime.datetime().hour))

        self.log("")
        self.log("数据时间")
        self.log("当前Bar时间 self.datas[0].datetime.datetime() : {0}".format(self.datas[0].datetime.datetime()))
        self.log("当前Bar日期 self.datas[0].datetime.date() : {0}".format(self.datas[0].datetime.date()))


# 启动回测
def engine_run():
    # 初始化引擎
    cerebro = bt.Cerebro()
    # 给Cebro引擎添加策略
    cerebro.addstrategy(DemoStrategy)
    # 设置初始资金：
    cerebro.broker.setcash(200000.0)
    # 从csv文件加载数据
    data = data_tl.get_stock_daily(stock_id="600016.SH", start="20190101", end="20190105")
    cerebro.adddata(data)
    print('初始账户价值: %.2f' % cerebro.broker.getvalue())
    # 回测启动运行
    cerebro.run()
    print('最终账户价值: %.2f' % cerebro.broker.getvalue())
    # cerebro.plot()


if __name__ == '__main__':
    engine_run()
