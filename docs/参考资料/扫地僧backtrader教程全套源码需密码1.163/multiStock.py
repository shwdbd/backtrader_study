import datetime
import glob
import os.path

import backtrader as bt


# 创建策略
class SmaCross(bt.Strategy):
    # 可配置策略参数
    params = dict(
        pfast=2,  # 短期均线周期
        pslow=5,  # 长期均线周期    
        pstake=1000  # 单笔交易股票数目
    )

    def __init__(self):
        sma1 = [bt.ind.SMA(d, period=self.p.pfast) for d in self.datas]
        sma2 = [bt.ind.SMA(d, period=self.p.pslow) for d in self.datas]
        self.crossover = {
            d: bt.ind.CrossOver(s1, s2)
            for d, s1, s2 in zip(self.datas, sma1, sma2)
        }

    def next(self):
        for d in self.datas:            
            if not self.getposition(d).size:
                if self.crossover[d] > 0:
                    self.buy(data=d, size=self.p.pstake)  # 买买买
            elif self.crossover[d] < 0:
                self.close(data=d)  # 卖卖卖


##########################
# 主程序开始
#########################

cerebro = bt.Cerebro()

datadir = './data'  # 数据文件位于本脚本所在目录的data子目录中
datafilelist = glob.glob(os.path.join(datadir, '*'))  # 数据文件路径列表
maxstocknum = 10  # 股票池最大股票数目
datafilelist = datafilelist[0:maxstocknum]  # 截取指定数量的股票池

# 将目录datadir中的所有数据文件加载进系统
for fname in datafilelist:
    data = bt.feeds.GenericCSVData(
        dataname=fname,
        datetime=2,  # 日期行所在列
        open=4,  # 开盘价所在列
        high=5,  # 最高价所在列
        low=6,  # 最低价所在列
        close=3,  # 收盘价价所在列
        volume=10,  # 成交量所在列
        openinterest=-1,  # 无未平仓量列
        dtformat=('%Y%m%d'),  # 日期格式
        fromdate=datetime.datetime(2010, 1, 1),  # 起始日
        todate=datetime.datetime(2020, 7, 10),  # 结束日
        timeframe=bt.TimeFrame.Months  # 月线数据
    )
    cerebro.adddata(data)

# 注入策略
cerebro.addstrategy(SmaCross)

# 设置现金
startcash = 1000000
cerebro.broker.setcash(startcash)
cerebro.broker.setcommission(commission=0.001)

cerebro.run()

# 最终收益或亏损
pnl = cerebro.broker.get_value() - startcash
print('Profit ... or Loss: {:.2f}'.format(pnl))
