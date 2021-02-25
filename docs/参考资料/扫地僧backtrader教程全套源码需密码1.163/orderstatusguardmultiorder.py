import datetime
import backtrader as bt
import os.path  # 管理路径
import sys  # 发现脚本名字(in argv[0])


class St(bt.Strategy):
    params = dict(
        ma=bt.ind.SMA,
        p1=5, # 快速均线周期
        p2=15, # 慢速均线周期
        limit=0.005, # 用于计算限价单的限价
        limdays=3, # 买单有效期
        limdays2=1000, # 卖单有效期
        hold=10, 
      
    )

    def notify_order(self, order):
        print('{}: Order ref: {} / Type {} / Status {}'.format(
            self.data.datetime.date(0), order.ref, 'Buy' * order.isbuy()
            or 'Sell', order.getstatusname()))

        if order.status == order.Completed:
            self.holdstart = len(self)

        if not order.alive() and order.ref in self.orefs:
            self.orefs.remove(order.ref)

    def __init__(self):
        # 两个移动均线
        ma1, ma2 = self.p.ma(period=self.p.p1), self.p.ma(period=self.p.p2)
        self.cross = bt.ind.CrossOver(ma1, ma2)

        self.orefs = list() # 未决订单标识列表

    def next(self):
        # 如果有未决订单，直接返回
        if self.orefs:
            return

        if not self.position: # 如果没有仓位
            if self.cross > 0.0:  #买入信号

                close = self.data.close[0]
                p1 = close * (1.0 - self.p.limit)
                p2 = p1 - 0.02 * close
                p3 = p1 + 0.02 * close

                valid1 = datetime.timedelta(self.p.limdays)
                valid2 = valid3 = datetime.timedelta(self.p.limdays2)

      
                #　发布一个限价买单
                o1 = self.buy(
                    exectype=bt.Order.Limit,
                    price=p1,
                    valid=valid1,
                    transmit=False)

                print('{}: Oref {} / Buy at {}'.format(self.datetime.date(),
                                                       o1.ref, p1))
                # 再发布一个保护性的停损卖单，用于止损
                o2 = self.sell(
                    exectype=bt.Order.Stop,
                    price=p2,
                    valid=valid2,
                    parent=o1, # 父订单是o1
                    transmit=False)

                print('{}: Oref {} / Sell Stop at {}'.format(
                    self.datetime.date(), o2.ref, p2))

                # 再发布一个限价卖单，用于止盈
                o3 = self.sell(
                    exectype=bt.Order.Limit,
                    price=p3,
                    valid=valid3,
                    parent=o1,  # 父订单是o1
                    transmit=True)

                print('{}: Oref {} / Sell Limit at {}'.format(
                    self.datetime.date(), o3.ref, p3))
                
                # 将三个订单标识放入未决订单列表
                self.orefs = [o1.ref, o2.ref, o3.ref]

        else:  # in the market
            if (len(self) - self.holdstart) >= self.p.hold:
                pass  # do nothing in this case


##########################
# 主程序开始
#########################

# 创建大脑引擎对象
cerebro = bt.Cerebro()

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
    fromdate=datetime.datetime(2019, 1, 1),  # 起始日
    todate=datetime.datetime(2020, 7, 8))  # 结束日

cerebro.adddata(data)  # 将行情数据对象注入引擎
cerebro.addstrategy(St)  # 将策略注入引擎

print('初始市值: %.2f' % cerebro.broker.getvalue())
cerebro.run()  # 运行
print('最终市值: %.2f' % cerebro.broker.getvalue())
