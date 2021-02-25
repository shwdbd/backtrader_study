from datetime import datetime,time
from datetime import timedelta
import pandas as pd
import numpy as np
import backtrader as bt
import os.path  # 管理路径
import sys  # 发现脚本名字(in argv[0])
import glob
from backtrader.feeds import GenericCSVData  # 用于扩展DataFeed

# 创建新的data feed类


class CSVDataExtend(GenericCSVData):
    # 增加线
    lines = ('pe', 'roe', 'marketdays')
    params = (('pe', 15),
              ('roe', 16),
              ('marketdays', 17), )  # 上市天数


class Strategy(bt.Strategy):
    params = dict(
        rebal_monthday=[1],  # 每月1日执行再平衡
        num_volume=100,  # 成交量取前100名
    )

    # 日志函数
    def log(self, txt, dt=None):
        # 以第一个数据data0，即指数作为时间基准
        dt = dt or self.data0.datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.lastRanks = []  # 上次交易股票的列表
        # 0号是指数，不进入选股池，从1号往后进入股票池
        self.stocks = self.datas[1:]

        # 定时器
        self.add_timer(
            when=bt.Timer.SESSION_START,
            monthdays=self.p.rebal_monthday,  # 每月1号触发再平衡
            monthcarry=True,  # 若再平衡日不是交易日，则顺延触发notify_timer
        )

    def notify_timer(self, timer, when, *args, **kwargs):

        print('timer', self.data0.datetime.datetime(0), 'when', when)
        # 只在5，9，11月的1号执行再平衡
        if(self.data0.datetime.date(0).month == 5
                or self.data0.datetime.date(0).month == 9
                or self.data0.datetime.date(0).month == 11):
            self.rebalance_portfolio()  # 执行再平衡

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # 订单状态 submitted/accepted，无动作
            return

        # 订单完成
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('买单执行,%s, %.2f, %i' % (order.data._name,
                                                order.executed.price, order.executed.size))

            elif order.issell():
                self.log('卖单执行, %s, %.2f, %i' % (order.data._name,
                                                 order.executed.price, order.executed.size))

        else:
            self.log('订单作废 %s, %s, isbuy=%i' %
                     (order.data._name, order.getstatusname(), order.isbuy()))

    # 记录交易收益情况
    def notify_trade(self, trade):
        if trade.isclosed:
            print('毛收益 %0.2f, 扣佣后收益 % 0.2f, 佣金 %.2f, 市值 %.2f' %
                  (trade.pnl, trade.pnlcomm, trade.commission, self.broker.getvalue()))

    def rebalance_portfolio(self):

        # 从指数取得当前日期
        self.currDate = self.data0.datetime.date(0)
        print('rebalance_portfolio currDate', self.currDate, len(self.stocks))

        # 最终标的选取过程
        # 1 先做排除筛选过程
        self.ranks = [d for d in self.stocks if
                      len(d) > 0  # 重要，到今日至少要有一根实际bar
                      and d.marketdays > 3*365  # 到今天至少上市
                      # 今日未停牌 (若去掉此句，则今日停牌的也可能进入，并下订单，次日若复牌，则次日可能成交）（假设原始数据中已删除无交易的记录)
                      and d.datetime.date(0) == self.currDate
                      and d.roe >= 0.1
                      and d.pe < 100
                      and d.pe > 0
                      ]

        # 2 再做排序挑选过程
        self.ranks.sort(key=lambda d: d.volume, reverse=True)  # 按成交量从大到小排序
        self.ranks = self.ranks[0:self.p.num_volume]  # 取前num_volume名

        if len(self.ranks) == 0:  # 无股票选中，则返回
            return

        # 3 以往买入的标的，本次不在标的中，则先平仓
        data_toclose = set(self.lastRanks) - set(self.ranks)
        for d in data_toclose:
            self.close(data=d)

        # 4 本次标的下单
        print('len(self.ranks)', len(self.ranks))
        # 每只股票买入资金百分比
        buypercentage = 1/len(self.ranks)
        print('buypercentage', buypercentage)
        # 为保证先卖后买，要按市值从大到小排序
        # self.ranks.sort(key=lambda d: self.broker.getvalue([d]), reverse=True)
        for d in self.ranks:
            o = self.order_target_percent(data=d, target=buypercentage)
            # o = self.order_target_percent(data=d, target=buypercentage, exectype=bt.Order.Limit, price=d.open[1])

        self.lastRanks = self.ranks  # 跟踪上次买入的标的


##########################
# 主程序开始
#########################
cerebro = bt.Cerebro(stdstats=False)
cerebro.addobserver(bt.observers.Broker)
cerebro.addobserver(bt.observers.Trades)
# cerebro.broker.set_coc(True)  # 以订单创建日的收盘价成交
# cerebro.broker.set_coo(True) # 以次日开盘价成交


datadir = './dataswind'  # 数据文件位于本脚本所在目录的data子目录中
datafilelist = glob.glob(os.path.join(datadir, '*'))  # 数据文件路径列表

maxstocknum = 3  # 股票池最大股票数目
# 注意，排序第一个文件必须是指数数据，作为时间基准
datafilelist = datafilelist[0:maxstocknum]  # 截取指定数量的股票池
print(datafilelist)
# 将目录datadir中的数据文件加载进系统


for fname in datafilelist:

    # df = pd.read_csv(
    #     fname,   
    #     skiprows=0,  # 不忽略行
    #     header=0,  # 列头在0行
    # )
    # # df = df[~df['交易状态'].isin(['停牌一天'])]  # 去掉停牌日记录
    # df['date'] = pd.to_datetime(df['date'])  # 转成日期类型   
    # df = df.dropna()

    # # print(df.info())
    # # print(df.head())
    # # 删除缺指标的记录
    
    data = CSVDataExtend(
        dataname=fname,
        datetime=0,  # 日期列
        open=2,  # 开盘价所在列
        high=3,  # 最高价所在列
        low=4,  # 最低价所在列
        close=5,  # 收盘价价所在列
        volume=6,  # 成交量所在列
        pe=7,
        roe=8,
        marketdays=9,
        openinterest=-1,  # 无未平仓量列
        fromdate=datetime(2002, 4, 1),  # 起始日
        todate=datetime(2015, 12, 31),  # 结束日
        plot=False,
        dtformat=('%Y-%m-%d'),
        sessionstart=time(9,30),
        sessionend=time(15,0)

    )
    ticker = fname[-13:-4]  # 从文件路径名取得股票代码
   
    cerebro.adddata(data, name=ticker)


cerebro.addstrategy(Strategy)
startcash = 10000000
cerebro.broker.setcash(startcash)
# 防止下单时现金不够被拒绝。只在执行时检查现金够不够。
cerebro.broker.set_checksubmit(False)
results = cerebro.run()
print('最终市值: %.2f' % cerebro.broker.getvalue())
cerebro.plot()
