from datetime import datetime
import backtrader as bt
import os.path  # 管理路径
import sys  # 发现脚本名字(in argv[0])


# 创建策略类
class SmaCross(bt.Strategy):

    # 日志函数
    def log(self, txt, dt=None):
        '''日志函数'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # 订单状态 submitted/accepted，无动作
            return

        # 订单完成
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('买单执行, %.2f' % order.executed.price)

            elif order.issell():
                self.log('卖单执行, %.2f' % order.executed.price)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('订单 Canceled/Margin/Rejected')

    

    # 记录交易收益情况（可省略，默认不输出结果）
    def notify_trade(self, trade):
        if trade.isclosed:
            print('毛收益 %0.2f, 扣佣后收益 % 0.2f, 佣金 %.2f' %
                  (trade.pnl, trade.pnlcomm, trade.commission))

    def __init__(self):
        # 5日移动平均线指标
        self.move_average = bt.ind.MovingAverageSimple(self.data, period=5)
        # 2周线移动平均线
        self.move_average2 = bt.ind.MovingAverageSimple(
            self.datas[1].close, period=2)

        # 日线交叉信号指标
        self.crossover = bt.ind.CrossOver(self.data, self.move_average)

        # 日移动均线和周移动均线的差
        self.isover = self.move_average - self.move_average2()

    def next(self):
      
        print(self.datetime.datetime(),'in next, move_average2 %0.2f' % self.isover[0],self.data0.open[0],self.data1.open[0])
        if not self.position:  # 还没有仓位
            # 当日收盘价上穿5日均线，创建买单，买入100股
            if self.crossover > 0 and self.isover:
                self.log('创建买单')
                self.buy(size=100)
        # 有仓位，并且当日收盘价下破5日均线，创建卖单，卖出100股
        elif self.crossover < 0 and not self.isover:
            self.log('创建卖单')
            self.close()


##########################
# 主程序开始
#########################

# 创建大脑引擎对象
cerebro = bt.Cerebro()

# 获取本脚本文件所在路径
modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
# 拼接得到数据文件全路径
datapath = os.path.join(modpath, './600000d.csv')  # 日线数据
datapath2 = os.path.join(modpath, './600000w.csv')  #周线数据

# 日线行情数据对象，加载数据
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
    timeframe = bt.TimeFrame.Days,
    fromdate=datetime(2000, 1, 4),  # 起始日
    todate=datetime(2000, 12, 29))  # 结束日

# 周线行情数据对象，加载数据
data2 = bt.feeds.GenericCSVData(
    dataname=datapath2,
    datetime=2,  # 日期行所在列
    open=4,  # 开盘价所在列
    high=5,  # 最高价所在列
    low=6,  # 最低价所在列
    close=3,  # 收盘价价所在列
    volume=10,  # 成交量所在列
    openinterest=-1,  # 无未平仓量列
    dtformat=('%Y%m%d'),  # 日期格式
    timeframe = bt.TimeFrame.Weeks,
    fromdate=datetime(2000, 1, 4),  # 起始日
    todate=datetime(2000, 12, 29))  # 结束日

cerebro.adddata(data)  # 将行情数据对象注入引擎
cerebro.adddata(data2)  # 将行情数据对象注入引擎
cerebro.addstrategy(SmaCross)  # 将策略注入引擎

cerebro.broker.setcash(10000.0)  # 设置初始资金
cerebro.broker.setcommission(0.001)  # 佣金费率
# 固定滑点，也可用cerebro.broker.set_slippage_perc()设置百分比滑点
cerebro.broker.set_slippage_fixed(0.05)

print('初始市值: %.2f' % cerebro.broker.getvalue())

cerebro.run(stdstats=False, runonce=False)
print('最终市值: %.2f' % cerebro.broker.getvalue())
