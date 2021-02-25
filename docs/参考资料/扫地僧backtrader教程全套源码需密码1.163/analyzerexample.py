from datetime import datetime
import backtrader as bt
#import backtrader.analyzers.basictradestats as bts
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
        dt = dt or self.datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # 移动平均线指标
        self.move_average = bt.ind.MovingAverageSimple(
            self.datas[0].close, period=self.params.period)

        # 交叉信号指标
        self.crossover = bt.ind.CrossOver(self.data, self.move_average)

    def next(self):
        if not self.position:  # 还没有仓位
            # 当日收盘价上穿5日均线，创建买单，买入100股
            if self.crossover > 0:
                self.buy(size=100)
        # 有仓位，并且当日收盘价下破5日均线，创建卖单，卖出100股
        elif self.crossover < 0:
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
    openinterest=-1,  # 无未平仓量列
    dtformat=('%Y%m%d'),  # 日期格式
    fromdate=datetime(2019, 3, 1),  # 起始日
    todate=datetime(2020, 5, 1))  # 结束日

cerebro.adddata(data)  # 将行情数据对象注入引擎
cerebro.addstrategy(SmaCross)  # 将策略注入引擎
cerebro.broker.setcash(10000.0)  # 设置初始资金

# Analyzer
cerebro.addanalyzer(
    bt.analyzers.SharpeRatio,
    riskfreerate=0.01,
    annualize=True,
    _name='sharp_ratio')
cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name='annula_return')
cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')


thestrats = cerebro.run()
thestrat = thestrats[0]
# 输出分析器结果字典
print('Sharpe Ratio:', thestrat.analyzers.sharp_ratio.get_analysis())
print('AnnualReturn:', thestrat.analyzers.annula_return.get_analysis())
print('DrawDown:', thestrat.analyzers.drawdown.get_analysis())

# 进一步从字典中取出需要的值
print('Sharpe Ratio:',
      thestrat.analyzers.sharp_ratio.get_analysis()['sharperatio'])
print('Max DrawDown:',
      thestrat.analyzers.drawdown.get_analysis()['max']['drawdown'])

# 打印各个分析器内容
for a in thestrat.analyzers:
    a.print()

