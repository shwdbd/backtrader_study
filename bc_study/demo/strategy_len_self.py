#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   strategy_len_self.py
@Time    :   2020/12/08 10:27:20
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   试验len(self)的计算

len(self)返回目前是第几个周期？

？是否包括prenext()函数

'''
import backtrader as bt
import bc_study.tushare_csv_datafeed as ts_df


class DoulbeSMAStrategy(bt.Strategy):
    """
    双均线金叉死叉策略
    """

    def log(self, txt, dt=None):
        ''' log信息的功能'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # 一般用于计算指标或者预先加载数据，定义变量使用
        self.sma = bt.indicators.SMA(
            self.datas[0].close, period=3)

    def prenext(self):
        self.log("prenext(), len(self)={0}".format(len(self)))

    def next(self):
        self.log("next(), len(self)={0}".format(len(self)))


if __name__ == '__main__':
    # 初始化引擎
    cerebro = bt.Cerebro()

    # 给Cebro引擎添加策略
    cerebro.addstrategy(DoulbeSMAStrategy)

    # 设置初始资金：
    cerebro.broker.setcash(100000.0)    # 10万元

    # 从csv文件加载数据
    # 仅3天数据
    data = ts_df.get_csv_daily_data(
        stock_id="000001.SZ", start="20150101", end="20150110")
    cerebro.adddata(data)

    # 回测启动运行
    cerebro.run()
