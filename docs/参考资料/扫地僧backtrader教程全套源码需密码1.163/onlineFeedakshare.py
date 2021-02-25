import backtrader as bt
import akshare as ak



# 创建策略类
class SmaCross(bt.Strategy):
    # 定义参数
    params = dict(period=5  # 移动平均期数
                  )

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
        # 移动平均线指标
        self.move_average = bt.ind.MovingAverageSimple(
            self.data, period=self.params.period)

        # 交叉信号指标
        self.crossover = bt.ind.CrossOver(self.data, self.move_average)

    def next(self):

        if not self.position:  # 还没有仓位
            # 当日收盘价上穿5日均线，创建买单，买入100股
            if self.crossover > 0:
                self.log('创建买单')
                self.buy(size=100)
        # 有仓位，并且当日收盘价下破5日均线，创建卖单，卖出100股
        elif self.crossover < 0:
            self.log('创建卖单')
            self.sell(size=100)

##########################
# 主程序开始
#########################

# 创建大脑引擎对象
cerebro = bt.Cerebro()

# start_date = datetime(2018, 1, 1)  # 回测开始时间
# end_date = datetime(2020, 1, 1)  # 回测结束时间

 # 利用 AkShare 获取后复权数据
stock_hfq_df = ak.stock_zh_a_daily(symbol="sh600000", adjust="hfq",start_date='20180101',end_date='20200101') 
# data = bt.feeds.PandasDirectData(dataname=stock_hfq_df, fromdate=start_date, todate=end_date)  # 加载数据

print(stock_hfq_df)
data = bt.feeds.PandasDirectData(dataname=stock_hfq_df)  # 加载数据


cerebro.adddata(data)  # 将数据传入回测系统
cerebro.addstrategy(SmaCross)  # 将交易策略加载到回测系统中
cerebro.broker.setcash(1000000.0)  # 设置初始资金



cerebro.run()  # 运行
print('最终市值: %.2f' % cerebro.broker.getvalue())

cerebro.plot()  # 画图