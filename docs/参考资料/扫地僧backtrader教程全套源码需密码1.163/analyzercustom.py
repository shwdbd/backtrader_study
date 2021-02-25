from datetime import datetime
import backtrader as bt
import os.path  # 管理路径
import sys  # 发现脚本名字(in argv[0])



# 创建策略类
class SmaCross(bt.Strategy):
    # 定义参数
    params = dict(period=2  # 移动平均期数
                  )

    # 日志函数
    def log(self, txt, dt=None):
        '''日志函数'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # 移动平均线指标
        self.move_average = bt.ind.MovingAverageSimple(
            self.datas[0].close, period=self.params.period)

    def next(self):
        # self.log('value %.2f' % self.broker.getvalue())
        if not self.position.size:  # 还没有仓位
            # 当日收盘价上穿5日均线，创建买单，买入100股
            if self.datas[0].close[-1] < self.move_average.sma[
                    -1] and self.datas[0].close[0] > self.move_average.sma[0]:
                self.buy(size=100)
        # 有仓位，并且当日收盘价下破5日均线，创建卖单，卖出100股
        elif self.datas[0].close[-1] > self.move_average.sma[-1] and self.datas[
                0].close[0] < self.move_average.sma[0]:
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
    openinterest=-1,  # 无未平仓量列.(openinterest是期货交易使用的)
    dtformat=('%Y%m%d'),  # 日期格式
    fromdate=datetime(2019, 3, 1),  # 起始日
    todate=datetime(2020, 5, 1))  # 结束日

cerebro.adddata(data)  # 将行情数据对象注入引擎
cerebro.addstrategy(SmaCross)  # 将策略注入引擎
cerebro.broker.setcash(10000.0)  # 设置初始资金

# Analyzer
# 这个是含kelly和其他更多指标的定制分析者
# cerebro.addanalyzer(bt.analyzers.BasicTradeStats, _name='basicstats')
cerebro.addanalyzer(bt.analyzers.Kelly, _name='kelly')


# cerebro.addwriter(bt.WriterFile, csv=True, out='mywriter.csv', rounding=2)
thestrats = cerebro.run()
thestrat = thestrats[0]

print('kelly:', thestrat.analyzers.kelly.get_analysis())

# 打印各个分析器内容
for a in thestrat.analyzers:
    a.print()
