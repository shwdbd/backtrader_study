#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   quickstart_demo0.py
@Time    :   2020/10/29 15:25:16
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   官方QuickStart示例

最简单的策略，输出当日的开收盘价格

'''
import backtrader as bt
import bc_study.tushare_csv_datafeed as ts_df


# 演示用策略，每日输出开盘价
class DemoStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        print("【策略】init 函数 开始")
        # 建立对于DataFeed的Open/Close价格的引用参数
        self.dataopen = self.datas[0].open
        self.dataclose = self.datas[0].close
        print("【策略】init 函数 结束")

    def next(self):
        # 输出当日的Open,Close价格
        self.log('Open={0}, Close={1}'.format(self.dataopen[0], self.dataclose[0]))
        self.log('上一日 Open={0}, Close={1}'.format(self.dataopen[-1], self.dataclose[-1]))
        # error，无法访问后续的日期数据
        # self.log('上一日 Open={0}, Close={1}'.format(self.dataopen[1], self.dataclose[1]))


# 启动回测
def engine_run():
    # 初始化引擎
    cerebro = bt.Cerebro()

    # 给Cebro引擎添加策略
    cerebro.addstrategy(DemoStrategy)

    # 设置初始资金：
    cerebro.broker.setcash(200000.0)

    # 从csv文件加载数据
    # 仅3天数据
    data = ts_df.get_csv_daily_data(stock_id="600016.SH", start="20190101", end="20190105")
    cerebro.adddata(data)

    print('初始市值: %.2f' % cerebro.broker.getvalue())
    # 回测启动运行
    result = cerebro.run()
    print("回测运行返回值 = {0}".format(result))
    print('期末市值: %.2f' % cerebro.broker.getvalue())


if __name__ == '__main__':
    engine_run()
