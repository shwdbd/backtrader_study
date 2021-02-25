from datetime import datetime
import backtrader as bt
import os.path  # 管理路径
import sys  # 发现脚本名字(in argv[0])


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
        self.count=0


    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # 订单状态 submitted/accepted，处于未决订单状态。
            return
        
        self.log('订单状态 %s' % order.getstatusname())  

        # 订单已决，执行如下语句
        if order.status in [order.Completed, order.Partial]:
            if order.isbuy():
                self.log('买单执行, %.2f, %d, %d' %(order.executed.price, order.executed.size, order.executed.remsize))

            elif order.issell():
                self.log('卖单执行, %.2f, %d, %d' % (order.executed.price, order.executed.size, order.executed.remsize))

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('订单 Canceled/Margin/Rejected')



    # # 记录交易收益情况（可省略，默认不输出结果）
    # def notify_trade(self, trade):      
     
    #     print()
    #     for h in trade.history:
    #         print('status:',h.status)
    #         print('enent:',h.event)
        


  

    
    def next(self):
        
        if self.count <= 0:
            self.buy(size=100)
            print('buy create, vol',self.data.datetime.date(),self.data.volume[0])
        # elif self.count == 2:
        #     self.sell(size=200) # 此句亦可改为self.close()
        # elif self.count == 3:
        #     self.buy(size=100)
        # elif self.count == 4:
        #     self.close()

        self.count+=1
        
    def stop(self):
        pass
        # _trades[data][0]: tradeid=0的trade列表
        # print(len(self._trades[data][0]))
    
        



##########################
# 主程序开始
#########################

# 创建大脑引擎对象
cerebro = bt.Cerebro(tradehistory=True)


# 获取本脚本文件所在路径
modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
# 拼接得到数据文件全路径
datapath = os.path.join(modpath, './600000test.csv')

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
    fromdate=datetime(2000, 1, 1),  # 起始日
    todate=datetime(2000, 2, 28))  # 结束日

cerebro.adddata(data)  # 将行情数据对象注入引擎
cerebro.addstrategy(SmaCross)  # 将策略注入引擎

# filler = bt.broker.fillers.FixedSize(size=30)
# filler = bt.broker.fillers.FixedBarPerc(perc=90)
filler = bt.broker.fillers.BarPointPerc(minmov=0.1, perc=90)
 
cerebro.broker.set_filler(filler)


cerebro.broker.setcash(10000.0)  # 设置初始资金
cerebro.broker.setcommission(0.001) # 佣金费率
 # 固定滑点，也可用cerebro.broker.set_slippage_perc()设置百分比滑点
# cerebro.broker.set_slippage_fixed(0.05)

print('初始市值: %.2f' % cerebro.broker.getvalue())
cerebro.run()  # 运行
print('最终市值: %.2f' % cerebro.broker.getvalue())
