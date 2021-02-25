import datetime
import backtrader as bt


class St(bt.Strategy):
    params = dict(
        periods=[10, 30],
        matype=bt.ind.SMA,
    )

    def __init__(self):
        # 记录是否作弊，注意它是如何取得cerebro参数的
        self.cheating = self.cerebro.p.cheat_on_open 
        print('self.cheating',self.cheating)
        # 移动均线列表
        mas = [self.p.matype(period=x) for x in self.p.periods]
        self.signal = bt.ind.CrossOver(*mas)
        self.order = None

    def notify_order(self, order):
        if order.status != order.Completed:
            return

        self.order = None
        print('{} {} Executed at price {},             size {}'.format(
            bt.num2date(order.executed.dt).date(),
            'Buy' * order.isbuy() or 'Sell', order.executed.price,  order.executed.size)
        )

    def operate(self, fromopen):
        if self.order is not None:
            return
        if self.position:
            if self.signal < 0:
                self.order = self.close()
        elif self.signal > 0:
            print('{} Send Buy, fromopen {}, close {}'.format(
                self.data.datetime.date(),
                fromopen, self.data.close[0])
            )
            self.order =  self.buy()
          

    def next(self):        
        print('{} next     , open {} close {}'.format(
            self.data.datetime.date(),
            self.data.open[0], self.data.close[0])
        )

        if self.cheating:
            return
        self.operate(fromopen=False)

    def next_open(self):
        
        if not self.cheating:
            return
        print('{} next_open, open {} close {}'.format(
            self.data.datetime.date(),
            self.data.open[0], self.data.close[0])
        )
        self.operate(fromopen=True)

##################
# 主程序开始
#################

# 启用开盘作弊模式
cerebro = bt.Cerebro(cheat_on_open=True) 

# Data feed
data0 = bt.feeds.BacktraderCSVData(dataname='./samples/datas/2005-2006-day-001.txt')
cerebro.adddata(data0)

# Broker
cerebro.broker.add_cash(100000)

# Strategy
cerebro.addstrategy(St)

# Execute
cerebro.run()






