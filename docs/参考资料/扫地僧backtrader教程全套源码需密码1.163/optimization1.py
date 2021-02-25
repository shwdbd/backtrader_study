from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from datetime import datetime  # 用于datetime对象操作
import os.path  # 用于管理路径
import sys  # 用于在argvTo[0]中找到脚本名称
import backtrader as bt  # 引入backtrader框架


# 创建策略
class SmaCross(bt.Strategy):
    # 可配置策略参数
    params = dict(
        pfast=5,  # 短期均线周期
        pslow=10  # 长期均线周期
    )

    def __init__(self):
        sma1 = bt.ind.SMA(period=self.p.pfast)  # 短期均线
        sma2 = bt.ind.SMA(period=self.p.pslow)  # 长期均线
        self.crossover = bt.ind.CrossOver(sma1, sma2)  # 交叉信号

    def next(self):
        if not self.position:  # 不在场内，则可以买入
            if self.crossover > 0:  # 如果金叉
                self.buy(size=5000)  # 买入
        elif self.crossover < 0:  # 在场内，且死叉
            self.close()  # 卖出

    def stop(self):
        print('(Fast Period %3d, Slow Period %3d) Ending Value %.2f' %
              (self.p.pfast, self.p.pslow, self.broker.getvalue()))


if __name__ == '__main__':
    cerebro = bt.Cerebro()  # 创建cerebro

    # 获取本脚本文件所在路径
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    # 拼接得到数据文件全路径
    datapath = os.path.join(modpath, './600000qfq.csv')

    # 创建行情数据对象，加载数据
    data = bt.feeds.GenericCSVData(
        dataname=datapath,
        datetime=2,  # 日期行所在列
        open=3,  # 开盘价所在列
        high=4,  # 最高价所在列
        low=5,  # 最低价所在列
        close=6,  # 收盘价价所在列
        volume=10,  # 成交量所在列
        dtformat=('%Y%m%d'),  # 日期格式
        fromdate=datetime(2018, 1, 1),  # 起始日
        todate=datetime(2020, 7, 8))  # 结束日

    # 在Cerebro中添加价格数据
    cerebro.adddata(data)
    # 设置启动资金
    cerebro.broker.setcash(100000.0)

    # 设置佣金为千分之一
    cerebro.broker.setcommission(commission=0.001)

    # 添加策略
    strats = cerebro.optstrategy(
        SmaCross, pfast=[5, 10, 15], pslow=[20, 30, 60])
    # strats = cerebro.optstrategy(SmaCross, pfast=range(5,10), pslow=range(20,25))

    cerebro.run()
