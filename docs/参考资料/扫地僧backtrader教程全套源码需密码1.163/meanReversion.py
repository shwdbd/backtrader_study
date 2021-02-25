import backtrader as bt
from datetime import datetime
import os.path  # 管理路径
import sys  # 发现脚本名字


class BOLLStrat(bt.Strategy):
    '''
    布林线均值回归策略
 
    进入标准:
        - 长仓:
            - 收盘价低于下轨
            - 创建Stop买单， 当价格向上突破下轨时，买入
        - 短仓（允许做空）: 
            - 收盘价高于上轨
            - 创建Stop卖单， 当价格向下突破上轨时，卖出
    退出标准
        - 长/短: 价格触及中线
    '''

    params = (
        ("period", 20),  # 布林线周期
        ("devfactor", 2),  # 偏离因子
        ("size", 20),  # 订单数量
        ("debug", False)  # 是否调试
    )

    def __init__(self):
        self.boll = bt.indicators.BollingerBands(
            period=self.p.period, devfactor=self.p.devfactor)
        #self.sx = bt.indicators.CrossDown(self.data.close, self.boll.lines.top)
        #self.lx = bt.indicators.CrossUp(self.data.close, self.boll.lines.bot)

    def next(self):
        # 未决订单列表
        orders = self.broker.get_orders_open()

        # 取消所有未决订单
        if orders:
            for order in orders:
                self.broker.cancel(order)

        # 无仓位，准备建仓进入市场
        if not self.position:  # 没有仓位

            if self.data.close > self.boll.lines.top:  # 收盘价高于上轨

                self.sell(  # 卖出
                    exectype=bt.Order.Stop,
                    price=self.boll.lines.top[0],
                    size=self.p.size)

            if self.data.close < self.boll.lines.bot:  # 收盘价低于下轨
                self.buy(  # 买入
                    exectype=bt.Order.Stop,
                    price=self.boll.lines.bot[0],
                    size=self.p.size)

        # 有仓位，准备退出市场
        else:

            if self.position.size > 0:  # 有长仓
                self.sell(  # 限价卖单，以比中线更好的价格卖出平仓
                    exectype=bt.Order.Limit,
                    price=self.boll.lines.mid[0],
                    size=self.p.size)

            else:  # 有短仓，即持仓量为负值
                self.buy(  # 限价买单，以比中线更好的价格买入平仓
                    exectype=bt.Order.Limit,
                    price=self.boll.lines.mid[0],
                    size=self.p.size)

        if self.p.debug:
            print(
                '---------------------------- NEXT ----------------------------------'
            )
            print("1: Data Name:                            {}".format(
                data._name))
            print("2: Bar Num:                              {}".format(
                len(data)))
            print("3: Current date:                         {}".format(
                data.datetime.datetime()))
            print('4: Open:                                 {}'.format(
                data.open[0]))
            print('5: High:                                 {}'.format(
                data.high[0]))
            print('6: Low:                                  {}'.format(
                data.low[0]))
            print('7: Close:                                {}'.format(
                data.close[0]))
            print('8: Volume:                               {}'.format(
                data.volume[0]))
            print('9: Position Size:                       {}'.format(
                self.position.size))
            print(
                '--------------------------------------------------------------------'
            )

    def notify_trade(self, trade):
        if trade.isclosed:
            dt = self.data.datetime.date()

            print(
                '---------------------------- TRADE ---------------------------------'
            )
            print("1: Data Name:                            {}".format(
                trade.data._name))
            print("2: Bar Num:                              {}".format(
                len(trade.data)))
            print("3: Current date:                         {}".format(dt))
            print('4: Status:                               Trade Complete')
            print('5: Ref:                                  {}'.format(
                trade.ref))
            print('6: PnL:                                  {}'.format(
                round(trade.pnl, 2)))
            print(
                '--------------------------------------------------------------------'
            )


#Variable for our starting cash
startcash = 10000

# Create an instance of cerebro
cerebro = bt.Cerebro()

# Add our strategy
cerebro.addstrategy(BOLLStrat)

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
    openinterest=-1,  # 无未平仓量列
    dtformat=('%Y%m%d'),  # 日期格式
    fromdate=datetime(2019, 1, 1),  # 起始日
    todate=datetime(2020, 7, 8))  # 结束日

# Add the data to Cerebro
cerebro.adddata(data)

# Add a sizer
cerebro.addsizer(bt.sizers.FixedReverser, stake=10)

# Run over everything
cerebro.run()

#Get final portfolio Value
portvalue = cerebro.broker.getvalue()
pnl = portvalue - startcash

#Print out the final result
print('Final Portfolio Value: ${}'.format(round(portvalue, 2)))
print('P/L: ${}'.format(round(pnl, 2)))

# Finally plot the end results
cerebro.plot(style='candlestick')