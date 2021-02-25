from datetime import datetime
import backtrader as bt
import os.path  # 管理路径
import sys  # 发现脚本名字(in argv[0])



class stampDutyCommissionScheme(bt.CommInfoBase):
    '''
    本佣金模式下，买入股票仅支付佣金，卖出股票支付佣金和印花税.    
    '''
    params = (
        ('stamp_duty', 0.5), # 印花税率
        ('commission', 0.1), # 佣金率
        ('stocklike', True),
        ('commtype', bt.CommInfoBase.COMM_PERC),
        )
 
    def _getcommission(self, size, price, pseudoexec):
        '''
        If size is greater than 0, this indicates a long / buying of shares.
        If size is less than 0, it idicates a short / selling of shares.
        '''
        print('self.p.commission',self.p.commission)
        if size > 0: # 买入，不考虑印花税
            return  size * price * self.p.commission * 100
        elif size < 0: # 卖出，考虑印花税
            return - size * price * (self.p.stamp_duty + self.p.commission*100)
        else:
            return 0 #just in case for some reason the size is 0.


# 创建策略类
class SmaCross(bt.Strategy):
    # 定义参数
    params = dict(period=5  # 移动平均期数
                  )

    # 日志函数
    def log(self, txt, dt=None):
        '''日志函数'''
        dt = dt or self.datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))
      

    def __init__(self):
        # 移动平均线指标
        self.move_average = bt.ind.MovingAverageSimple(
            self.data, period=self.params.period)


    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # 订单状态 submitted/accepted，处于未决订单状态。
            return

        # 订单已决，执行如下语句
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('买单执行, %.2f' % order.executed.price)

            elif order.issell():
                self.log('卖单执行, %.2f' % order.executed.price)

        elif order.status in [order.Canceled, order.Margin, order.Rejected, order.Expired]:
            self.log('订单 Canceled/Margin/Rejected')



    # 记录交易收益情况（可省略，默认不输出结果）
    def notify_trade(self, trade):
        print('trade')
        
        if trade.isclosed:
            print('毛收益 %0.2f, 扣佣后收益 % 0.2f, 佣金 %.2f' %
                     (trade.pnl, trade.pnlcomm, trade.commission))



    def next(self):
        
        if not self.position:  # 还没有仓位
            # 当日收盘价上穿5日均线，创建买单，买入100股
            if self.data.close[
                    -1] < self.move_average[-1] and self.data > self.move_average:
                self.log('创建买单')
                self.buy(size=100)
        # 有仓位，并且当日收盘价下破5日均线，创建卖单，卖出100股
        elif self.data.close[
                -1] > self.move_average[-1] and self.data < self.move_average:
            self.log('创建卖单')
            self.sell(size=100)


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
    openinterest=-1, # 无未平仓量列
    dtformat=('%Y%m%d'),  # 日期格式
    fromdate=datetime(2019, 1, 1),  # 起始日
    todate=datetime(2020, 7, 8))  # 结束日

cerebro.adddata(data)  # 将行情数据对象注入引擎
cerebro.addstrategy(SmaCross)  # 将策略注入引擎

cerebro.broker.setcash(10000.0)  # 设置初始资金
comminfo=stampDutyCommissionScheme(stamp_duty=0.005,commission=0.001)
cerebro.broker.addcommissioninfo(comminfo)


print('初始市值: %.2f' % cerebro.broker.getvalue())
cerebro.run()  # 运行
print('最终市值: %.2f' % cerebro.broker.getvalue())
cerebro.plot()