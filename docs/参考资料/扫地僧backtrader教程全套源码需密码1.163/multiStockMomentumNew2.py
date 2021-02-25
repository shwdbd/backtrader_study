from datetime import datetime
import pandas as pd
import numpy as np

import backtrader as bt
import os.path  # 管理路径
import sys  # 发现脚本名字(in argv[0])
from scipy.stats import linregress
import collections

# 获取本脚本文件所在路径
modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
# 拼接得到数据文件全路径
datapath = os.path.join(modpath, './survivorship-free/tickers.csv')

tickers = pd.read_csv(datapath, header=None)[1].tolist()
maxtickersNum = 10
tickers = tickers[0:maxtickersNum]
stocks = ((pd.concat([
    pd.read_csv(
        f"survivorship-free/{ticker}.csv", index_col='date',
        parse_dates=True)['close'].rename(ticker) for ticker in tickers
],
                     axis=1,
                     sort=True)))
stocks = stocks.loc[:, ~stocks.columns.duplicated()]
print(stocks.head())

####################################

import backtrader as bt


class Momentum(bt.Indicator):
    lines = ('trend', )
    params = (('period', 90), )

    def __init__(self):
        self.addminperiod(self.params.period)

    def next(self):
        returns = np.log(self.data.get(size=self.p.period))
        x = np.arange(len(returns))
        slope, _, rvalue, _, _ = linregress(x, returns)
        annualized = (1 + slope)**252
        self.lines.trend[0] = annualized * (rvalue**2)


class Strategy(bt.Strategy):
    params = dict(
        momentum=Momentum,  # parametrize the momentum and its period
        momentum_period=90,
        movav=bt.ind.SMA,  # parametrize the moving average and its periods
        idx_period=200,
        stock_period=100,
        volatr=bt.ind.ATR,  # parametrize the volatility and its period
        vol_period=20,
    )

    def __init__(self):
        # self.i = 0  # See below as to why the counter is commented out
        self.inds = collections.defaultdict(dict)  # avoid per data dct in for

        # Use "self.data0" (or self.data) in the script to make the naming not
        # fixed on this being a "spy" strategy. Keep things generic
        # self.spy = self.datas[0]
        self.stocks = self.datas[1:]

        # Again ... remove the name "spy"
        self.idx_mav = self.p.movav(self.data0, period=self.p.idx_period)
        for d in self.stocks:
            self.inds[d]['mom'] = self.p.momentum(
                d, period=self.p.momentum_period)
            self.inds[d]['mav'] = self.p.movav(d, period=self.p.stock_period)
            self.inds[d]['vol'] = self.p.volatr(d, period=self.p.vol_period)

        self.d_with_len = []

    def prenext(self):
        # Populate d_with_len
        self.d_with_len = [d for d in self.datas if len(d)]
        # call next() even when data is not available for all tickers
        self.next()

    def nextstart(self):
        # This is called exactly ONCE, when next is 1st called and defaults to
        # call `next`
        self.d_with_len = self.datas  # all data sets fulfill the guarantees now

        self.next()  # delegate the work to next

    def next(self):
        l = len(self)
        if l % 5 == 0:
            self.rebalance_portfolio()
        if l % 10 == 0:
            self.rebalance_positions()

    def rebalance_portfolio(self):
        # only look at data that we can have indicators for
        self.rankings = list(filter(lambda d: len(d) > 100, self.stocks))
        self.rankings.sort(key=lambda d: self.inds[d]["mom"][0])
        num_stocks = len(self.rankings)

        # sell stocks based on criteria
        for i, d in enumerate(self.rankings):
            if self.getposition(self.data).size:
                if i > num_stocks * 0.2 or d < self.inds[d]["mav"]:
                    self.close(d)

        if self.data0 < self.idx_mav:
            return

        # buy stocks with remaining cash
        for i, d in enumerate(self.rankings[:int(num_stocks * 0.2)]):
            cash = self.broker.get_cash()
            value = self.broker.get_value()
            if cash <= 0:
                break
            if not self.getposition(self.data).size:
                size = value * 0.001 / self.inds[d]["vol"]
                self.buy(d, size=size)

    def rebalance_positions(self):
        num_stocks = len(self.rankings)

        if self.data0 < self.idx_mav:
            return

        # rebalance all stocks
        for i, d in enumerate(self.rankings[:int(num_stocks * 0.2)]):
            cash = self.broker.get_cash()
            value = self.broker.get_value()
            if cash <= 0:
                break
            size = value * 0.001 / self.inds[d]["vol"]
            self.order_target_size(d, size)


cerebro = bt.Cerebro(stdstats=False)
cerebro.broker.set_coc(True)

spy = bt.feeds.YahooFinanceCSVData(
    dataname=os.path.join(modpath, './survivorship-free/SPY.csv'),
    fromdate=datetime(2012, 2, 28),
    todate=datetime(2018, 2, 28),
    plot=False)
cerebro.adddata(spy)  # add S&P 500 Index

for ticker in tickers:
    df = pd.read_csv(
        f"survivorship-free/{ticker}.csv", parse_dates=True, index_col=0)
    if len(df) > 100:  # data must be long enough to compute 100 day SMA
        cerebro.adddata(bt.feeds.PandasData(dataname=df, plot=False))

cerebro.addobserver(bt.observers.Value)
cerebro.addanalyzer(bt.analyzers.SharpeRatio, riskfreerate=0.0)
cerebro.addanalyzer(bt.analyzers.Returns)
cerebro.addanalyzer(bt.analyzers.DrawDown)
cerebro.addstrategy(Strategy)
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
