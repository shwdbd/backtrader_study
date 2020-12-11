#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   strategy_params.py
@Time    :   2020/12/08 10:50:54
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   策略Strategy类中参数使用

- 参数的定义
- 参数的访问
- 从外部传入数据

'''
import backtrader as bt
import bc_study.tushare_csv_datafeed as ts_df


class DoulbeSMAStrategy(bt.Strategy):
    """
    双均线金叉死叉策略
    """

    # 参数
    params = {"window": 10, "p2": 5}

    def log(self, txt, dt=None):
        ''' log信息的功能'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.log("init() 参数window={0}".format(self.params.window))
        pass

    def next(self):
        self.log("next() 参数window={0}".format(self.params.window))
        self.log("next() 参数p2={0}".format(self.p.p2))


if __name__ == '__main__':
    # 初始化引擎
    cerebro = bt.Cerebro()

    # 给Cebro引擎添加策略
    cerebro.addstrategy(DoulbeSMAStrategy, window=99, p2=10)

    # 设置初始资金：
    cerebro.broker.setcash(100000.0)    # 10万元

    # 从csv文件加载数据
    # 仅3天数据
    data = ts_df.get_csv_daily_data(
        stock_id="000001.SZ", start="20150101", end="20150110")
    cerebro.adddata(data)

    # 回测启动运行
    cerebro.run()
