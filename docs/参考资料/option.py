from __future__ import (absolute_import, division, print_function, unicode_literals)
import pymysql
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
import pymssql
import datetime
import os.path
import sys
import backtrader as bt
import pandas as pd
import akshare as ak

from backtrader.feeds import PandasData
conn = pymssql.connect(host='.', user='sa', password='test', database='50_ak', charset='utf8')
engine = create_engine('mssql+pymssql://sa:test@127.0.0.1/50_ak')
sql_query = 'select * from [50_ak]'
df_read = pd.read_sql(sql_query, engine)
#df_read = df_read.loc[:100]



df_read.columns = ['ts_code', 'datetime', 'open', 'high', 'low', 'close', 'volume']
df_read['datetime'] = df_read['datetime'].astype('datetime64')
df_read['open'] = df_read['open'].astype('float64')
df_read['high'] = df_read['high'].astype('float64')
df_read['low'] = df_read['low'].astype('float64')
df_read['close'] = df_read['close'].astype('float64')
df_read['volume'] = df_read['volume'].astype('int64')
df_read['ttm'] = 0
df_read['impvol'] = 0.5



stk_num = 1000  # 回测股票数据

#date_value_list = []


# 创建策略
class BollStrategy(bt.Strategy):
    # 可配置策略参数
    params = dict(
        poneplot=False,  # 是否打印到同一张图
        pstake=100,      # 单笔交易股票数据
    )

    def log(self, txt, dt=None):
        """策略的日志函数"""
        dt = dt or self.datas[0].datetime.date(0)
        print('%s,%s' % (dt.isoformat(), txt))

    def __init__(self):
        pass

        # for i, d in enumerate(self.datas):
        #     # 跳过第一只股票data，第一只股票data作为主图数据
        #     if i == 0:
        #         if self.p.poneplot:
        #             d.plotinfo.plotmaster = self.datas[0]

    def prenext(self):
        self.next()

    # 策略核心，根据条件执行买卖交易指令（必选）
    def next(self):

        # 获取当天日期
        date = self.datetime.date()
        print(date)

        for i,d in enumerate(self.datas):
            pos = self.getposition(d)
            # if self.datas[i].close[0] < 0.05:
            #     self.close(d,size = self.params.pstake)
            if len(pos):
                print('{}, 持仓:{}, 成本价:{}, 当前价:{}, 盈亏:{:.2f}'.format(
                    d._name, pos.size, pos.price, pos.adjbase, pos.size * (pos.adjbase - pos.price)),
                    file=self.log_file)
        # # 获取当天value
        # value = self.broker.getvalue()

        # # 存入列表
        # date_value_list.append((date, value))

        for i,d in enumerate(self.datas):
            #if self.datas[i].close[0] > 0.01:
            if True:
                print('buy',d.close[0])
                self.order = self.buy(data = d, size=self.params.pstake)
                #print(d._name)
                #order.addinfo(ticker=d._name)
                #print(d._name)
            else:
                #print('sell',d.close[0])
                self.order = self.sell(data = d, size=self.params.pstake)
                #order.addinfo(ticker=d._name)
                #print(d._name)


    # 记录交易收益情况（可省略，默认不输出结果）
    def notify_trade(self, trade):
        date = self.datetime.date()
        print('order',date)
        dt = self.data.datetime.date()
        if trade.isclosed:
            print('{} {} Closed: Pnl Gross{}, Net {}'.format(
                dt, trade.data._name, round(trade.pnl, 2), round(trade.pnlcomm, 2)
            ))

    # 订单状态变化时引擎会调用notify_order
    # 记录交易执行情况（可省略，默认不输出结果）
    def notify_order(self, order):

        print(order.getstatusname(order.status))
        if order.status in [order.Submitted, order.Accepted]:
            return

        # 如果交易已经完成，显示成交信息
        if order.status in [order.Completed]:
            if order.isbuy() or order.issell():
                print('{}  Buy/Sell {}, Price: {:.4f}, Size: {:6.0f}, Cost: {:.4f}, Comm {:.4f}'.format(
                    self.datetime.date(),
                    order.info['ticker'],
                    order.executed.price,
                    order.executed.size,
                    order.executed.value,
                    order.executed.comm)
                )

        # 如果订单未成交则给出提示
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            print('Order Canceled/Margin/Rejected: {}'.format(order.info['ticker']))

# #回测结束后输出结果（可省略，默认输出结果）
#     def stop(self):
#         self.log('(MA均线： %2d日) 期末总资金 %.2f' %
#                  (self.params.maperiod, self.broker.getvalue()), doprint=True)
class ETFOptionPandasData(PandasData):
    lines = ('ttm', 'impvol')
    params = (('ttm', 7), ('impvol', 8))

from backtrader.feeds import PandasData

cerebro = bt.Cerebro()
# 建立期权池
stk_pools = df_read['ts_code'].unique().tolist()
# 获取期权数据
for stk_code in stk_pools:
    df = df_read[df_read['ts_code'] == stk_code].iloc[:, :]
    df.index = pd.to_datetime(df['datetime'])
    data = ETFOptionPandasData(dataname=df)
    cerebro.adddata(data, name=stk_code)
cerebro.broker.setcash(10000000000000.0)
cerebro.broker.setcommission(commission=0.005)
cerebro.addstrategy(BollStrategy)
cerebro.run(maxcpus=10)
# for d in cerebro.datas:
#     d.plotinfo.plot =False
print(cerebro.broker.getvalue())

import matplotlib
import matplotlib.pyplot as plt
plt.figure()
for d in cerebro.datas:
    d.plotinfo.plot = False
cerebro.plot()