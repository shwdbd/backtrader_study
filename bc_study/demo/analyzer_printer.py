#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   analyzer_printer.py
@Time    :   2020/12/14 12:07:31
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   打印常见策略绩效的示例

用一个简单SMA均线策略做演示

'''
import backtrader as bt
import bc_study.tushare_csv_datafeed as ts_df


class DoulbeSMAStrategy(bt.Strategy):
    """
    双均线金叉死叉策略
    """
    # 参数：长短均线的日期
    params = {"short_window": 20, "long_window": 50}

    def log(self, txt, dt=None):
        ''' log信息的功能'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # 一般用于计算指标或者预先加载数据，定义变量使用
        self.dataopen = self.datas[0].open
        self.dataclose = self.datas[0].close
        self.short_ma = bt.indicators.SMA(
            self.datas[0].close, period=self.p.short_window)
        self.long_ma = bt.indicators.SMA(
            self.datas[0].close, period=self.p.long_window)
        self.log("完成 长[{0}]短[{1}]SMA 数据的计算".format(
            self.p.short_window, self.p.long_window))

    def notify_order(self, order):
        # 订单状态变化：
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY成交, 执行价={0}, {1}'.format(
                    order.executed.price, order.executed.size))
            elif order.issell():
                self.log('SELL成交, 执行价={0}, {1}'.format(
                    order.executed.price, order.executed.size))

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('交易结束, 毛利润 %.2f, 净利润 %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        # 当前持有头寸
        size = self.getposition(self.datas[0]).size

        # 做多
        if size == 0 and self.short_ma[-1] < self.long_ma[-1] and self.short_ma[0] > self.long_ma[0]:
            # 开仓
            # self.order_target_value(self.datas[0]*, target=5)
            order = self.buy(size=100*5)
            self.log("金叉，买{0}, Short SMA yes={1}, Long SMA today={2}".format(
                order.size, self.short_ma[-1], self.long_ma[0]))
        # 平多
        if size > 0 and self.short_ma[-1] > self.long_ma[-1] and self.short_ma[0] < self.long_ma[0]:
            order = self.close(self.datas[0])
            self.log("死叉，卖{0}, Short SMA yes={1}, Long SMA today={2}".format(
                order.size, self.short_ma[-1], self.long_ma[0]))


# ======================================================================================================================
# HELPERS：帮助函数，输出各种analyzer结果
# ======================================================================================================================
def pretty_print(format, *args):
    print(format.format(*args))


def exists(object, *properties):
    for property in properties:
        if not (property in object):
            return False
        object = object.get(property)
    return True


def printTradeAnalysis(cerebro, analyzers):
    format = "  {:<24} : {:<24}"
    NA = '-'

    print('Backtesting Results')
    if hasattr(analyzers, 'ta'):
        ta = analyzers.ta.get_analysis()

        openTotal = ta.total.open if exists(ta, 'total', 'open') else None
        closedTotal = ta.total.closed if exists(
            ta, 'total', 'closed') else None
        wonTotal = ta.won.total if exists(ta, 'won',   'total') else None
        lostTotal = ta.lost.total if exists(ta, 'lost',  'total') else None

        streakWonLongest = ta.streak.won.longest if exists(
            ta, 'streak', 'won',  'longest') else None
        streakLostLongest = ta.streak.lost.longest if exists(
            ta, 'streak', 'lost', 'longest') else None

        pnlNetTotal = ta.pnl.net.total if exists(
            ta, 'pnl', 'net', 'total') else None
        pnlNetAverage = ta.pnl.net.average if exists(
            ta, 'pnl', 'net', 'average') else None

        pretty_print(format, 'Open Positions', openTotal or NA)
        pretty_print(format, 'Closed Trades',  closedTotal or NA)
        pretty_print(format, 'Winning Trades', wonTotal or NA)
        pretty_print(format, 'Loosing Trades', lostTotal or NA)
        print('\n')

        pretty_print(format, 'Longest Winning Streak',
                     streakWonLongest or NA)
        pretty_print(format, 'Longest Loosing Streak',
                     streakLostLongest or NA)
        pretty_print(format, 'Strike Rate (Win/closed)', (wonTotal /
                                                          closedTotal) * 100 if wonTotal and closedTotal else NA)
        print('\n')

        pretty_print(format, 'Net P/L',
                     '${}'.format(round(pnlNetTotal,   2)) if pnlNetTotal else NA)
        pretty_print(format, 'P/L Average per trade',
                     '${}'.format(round(pnlNetAverage, 2)) if pnlNetAverage else NA)
        print('\n')

    if hasattr(analyzers, 'drawdown'):
        pretty_print(format, 'Drawdown', '${}'.format(
            analyzers.drawdown.get_analysis()['drawdown']))
    # 夏普率：
    if hasattr(analyzers, 'sharpe'):
        pretty_print(format, 'Sharpe Ratio:',
                     analyzers.sharpe.get_analysis()['sharperatio'])
    if hasattr(analyzers, 'vwr'):
        pretty_print(format, 'VRW', analyzers.vwr.get_analysis()['vwr'])
    if hasattr(analyzers, 'sqn'):
        pretty_print(format, 'SQN', analyzers.sqn.get_analysis()['sqn'])
    print('\n')

    # 输出交易明细
    print('交易明细：')
    format = "  {:<24} {:<24} {:<16} {:<8} {:<8} {:<16}"
    pretty_print(format, '日期', '数量', '价格', 'SID', 'Symbol', '交易金额')
    for key, value in analyzers.txn.get_analysis().items():
        pretty_print(format, key.strftime("%Y/%m/%d %H:%M:%S"),
                     value[0][0], value[0][1], value[0][2], value[0][3], value[0][4])


if __name__ == '__main__':
    # 初始化引擎
    cerebro = bt.Cerebro()

    # 给Cebro引擎添加策略
    cerebro.addstrategy(DoulbeSMAStrategy)

    # 添加分析器
    # cerebro.addanalyzer(btanalyzers.SharpeRatio, _name='mysharpe')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='ta')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', riskfreerate=0.0, annualize=True, timeframe=bt.TimeFrame.Days)
    cerebro.addanalyzer(bt.analyzers.VWR, _name='vwr')
    cerebro.addanalyzer(bt.analyzers.SQN, _name='sqn')
    cerebro.addanalyzer(bt.analyzers.Transactions, _name='txn')

    # 设置初始资金：
    cerebro.broker.setcash(100000.0)    # 10万元

    # 从csv文件加载数据
    # 仅3天数据
    data = ts_df.get_csv_daily_data(
        stock_id="000001.SZ", start="20150101", end="20161231")
    cerebro.adddata(data)

    print('初始市值: %.2f' % cerebro.broker.getvalue())
    # 回测启动运行
    result = cerebro.run()
    backtest_results = result[0]
    print('期末市值: %.2f' % cerebro.broker.getvalue())

    # 性能输出：
    printTradeAnalysis(cerebro, backtest_results.analyzers)

    # 绘图：
    cerebro.plot()
