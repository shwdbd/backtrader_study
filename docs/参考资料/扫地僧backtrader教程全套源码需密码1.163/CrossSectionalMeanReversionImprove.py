import pandas as pd
import backtrader as bt
import numpy as np
from datetime import datetime
import os.path  # 管理路径
import sys  # 发现脚本名字(in argv[0])

# 获取本脚本文件所在路径
modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
# 拼接得到数据文件全路径
datapath = os.path.join(modpath, './survivorship-free/tickers.csv')

tickers = pd.read_csv(datapath, header=None)[1].tolist()  # 股票池全集
maxtickersNum = 20  # 选maxtickersNum支股票进入股票池
tickers = tickers[0:maxtickersNum]  # 最终股票池列表


def max_n(array, n):
    return np.argpartition(array, -n)[-n:]


class CrossSectionalMR(bt.Strategy):
    params = (('num_positions', 10), )  # 选几只按权重分配

    def __init__(self):
        self.inds = {}
        for d in self.datas:
            self.inds[d] = {}
            self.inds[d]["pct"] = bt.indicators.PercentChange(
                d.close, period=1)

    def prenext(self):
        self.next()

    def next(self):
        # 昨天有数据的数据列表
        available = list(filter(lambda d: len(d) > 1, self.datas))

        if not available:  # 如果空则返回
            return

        rets = np.zeros(len(available))  # 初始化个股收益率列表
        for i, d in enumerate(available):
            # 计算第i支股票的日收益率
            rets[i] = self.inds[d]['pct'][0]

        market_ret = np.mean(rets)  # 股票池平均收益率
        # 计算个股权重列表
        weights = -(rets - market_ret)  # 个股超额收益率取反
        # 绝对权重最大的前num_positions个股票的索引列表
        max_weights_index = max_n(np.abs(weights), self.params.num_positions)
        # 取得绝对权重最大的权重列表
        max_weights = weights[max_weights_index]  
        weights = weights / np.sum(np.abs(max_weights))

        for i, d in enumerate(available):
            if i in max_weights_index:
                self.order_target_percent(d, target=weights[i])
            else:
                self.order_target_percent(d, 0)


##########################
# 主程序开始
#########################

cerebro = bt.Cerebro(stdstats=False)
cerebro.broker.set_coc(True)  # 以收盘价成交

for ticker in tickers:
    data = bt.feeds.GenericCSVData(
        dataname=f"survivorship-free/{ticker}.csv",
        dtformat=('%Y-%m-%d'),
        openinterest=-1,
        nullvalue=0.0,
        plot=False)
    cerebro.adddata(data)

cerebro.broker.setcash(1_000_000)
cerebro.addobserver(bt.observers.Value)
cerebro.addanalyzer(bt.analyzers.SharpeRatio, riskfreerate=0.0)
cerebro.addanalyzer(bt.analyzers.Returns)
cerebro.addanalyzer(bt.analyzers.DrawDown)

cerebro.addstrategy(CrossSectionalMR)
results = cerebro.run()

print(
    f"Sharpe: {results[0].analyzers.sharperatio.get_analysis()['sharperatio']:.3f}"
)
print(
    f"Norm. Annual Return: {results[0].analyzers.returns.get_analysis()['rnorm100']:.2f}%"
)
print(
    f"Max Drawdown: {results[0].analyzers.drawdown.get_analysis()['max']['drawdown']:.2f}%"
)
cerebro.plot()[0][0]