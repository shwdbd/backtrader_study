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
# 拼接得到tickers文件全路径
datapath = os.path.join(modpath, './survivorship-free/tickers.csv')
# 股票代码列表
tickers = pd.read_csv(datapath, header=None)[1].tolist()

# 取前maxtickersNum支股票进入策略股票池
maxtickersNum = 20
tickers = tickers[0:maxtickersNum]  # 取前maxtickersNum支股票代码

####################################


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
        rebal_weekday=5,  # 每周5执行再平衡
        momentum_period=90,  #动量计算周期
        idx_period=200,  # 标普指数200日均线
        stock_period=100,  # 股票100日均线
        vol_period=20,  # 平均真实波幅ATR计算周期
    )

    def log(self, arg):
        print('{} {}'.format(self.datetime.date(), arg))

    def __init__(self): 
        self.inds = collections.defaultdict(dict)

        # datas[0]存放数据spy（标普指数），其他股票数据放在stocks列表里
        self.stocks = self.datas[1:]

        # spy的移动平均线
        self.idx_mav = bt.ind.SMA(self.data0, period=self.p.idx_period)
        # 其他股票的3个指标计算
        for d in self.stocks:
            self.inds[d]['mom'] = Momentum(
                d, period=self.p.momentum_period)  # 动量
            self.inds[d]['mav'] = bt.ind.SMA(
                d, period=self.p.stock_period)  # 移动平均
            self.inds[d]['vol'] = bt.ind.ATR(
                d, period=self.p.vol_period)  # 平均真实波幅

        self.add_timer(  # 定时器
            when=bt.Timer.SESSION_START,
            weekdays=[self.p.rebal_weekday],
            weekcarry=True,  # 若再平衡日不是交易日，则延后执行
        )

        self.timercount = 1  # timer触发次数

    def notify_timer(self, timer, when, *args, **kwargs):        
        self.rebalance_portfolio()
        self.timercount = self.timercount + 1
        if self.timercount % 2 == 0:
            self.rebalance_positions()

    def prenext(self):
        # 即使有些股票尚无当前数据，也跳转next执行
        self.next()

    def next(self):
        # print('session', self.data0.p.sessionstart, self.data0.p.sessionend )
        pass

    def rebalance_portfolio(self):
        # 只查看有足够数据计算指标的股票
        self.rankings = list(
            filter(
                lambda d: len(d) > max(self.p.stock_period, self.p.vol_period),
                self.stocks))
        self.rankings.sort(key=lambda d: self.inds[d]["mom"][0])  # 按动量大小排序行情数据
        num_stocks = len(self.rankings)  # 股票数量

        # 按卖出标准卖出
        for i, d in enumerate(self.rankings):
            if self.getposition(d).size:

                # 排在后20%的或收盘价低于移动均值的，卖出
                if i > num_stocks * 0.2 or d < self.inds[d]["mav"]:
                    self.close(d)

        # 如果spy指数低于均线，则不买
        if self.data0 < self.idx_mav:
            return

        # 买入排序前20%的的股票
        for i, d in enumerate(self.rankings[:int(num_stocks * 0.2)]):
            cash = self.broker.get_cash()
            value = self.broker.get_value()
            if cash <= 0:
                break
            if not self.getposition(d).size:
                size = value * 0.001 / self.inds[d]["vol"]  # 买入数量
                self.buy(d, size=size)

    def rebalance_positions(self):
        # 只查看有足够数据计算指标的股票
        self.rankings = list(
            filter(
                lambda d: len(d) > max(self.p.stock_period, self.p.vol_period),
                self.stocks))
        self.rankings.sort(key=lambda d: self.inds[d]["mom"][0])
        num_stocks = len(self.rankings)

        if self.data0 < self.idx_mav:
            return

        # 对排序前20%的股票，再平衡持仓数量
        for i, d in enumerate(self.rankings[:int(num_stocks * 0.2)]):
            cash = self.broker.get_cash()
            value = self.broker.get_value()
            if cash <= 0:
                break
            size = value * 0.001 / self.inds[d]["vol"]  # 新持仓数量
            self.order_target_size(d, size)


##########################
# 主程序开始
#########################

cerebro = bt.Cerebro(stdstats=False)
cerebro.broker.set_coc(True)  # 以收盘价成交

spy = bt.feeds.YahooFinanceCSVData(
    dataname=os.path.join(modpath, './survivorship-free/SPY.csv'),
    fromdate=datetime(2012, 2, 28),
    todate=datetime(2018, 2, 28),
    plot=False)
cerebro.adddata(spy)  # 加入S&P 500指数

for ticker in tickers:
    df = pd.read_csv(
        f"survivorship-free/{ticker}.csv", parse_dates=True, index_col=0)
    
    data = bt.feeds.PandasData(
        dataname=df,
        datetime=None,  # 使用索引列作日期列
        open=0,  # 开盘价所在列
        high=1,  # 最高价所在列
        low=2,  # 最低价所在列
        close=3,  # 收盘价价所在列
        volume=4,  # 成交量所在列
        openinterest=-1,  # 无未平仓量列.(openinterest是期货交易使用的)
        plot=False

    )
    
    if len(df) > 100:  # 数据要足够长以支持计算100日移动均线
        cerebro.adddata(data)

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
