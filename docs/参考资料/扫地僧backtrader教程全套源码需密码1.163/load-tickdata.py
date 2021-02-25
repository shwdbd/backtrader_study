import backtrader as bt
import backtrader.feeds as btfeeds

class testStrategy(bt.Strategy):
    def next(self):
        print(self.data0.datetime.datetime(0),self.data0.open[0],self.data0.high[0],self.data0.low[0],self.data0.close[0],)

# Create a cerebro entity
cerebro = bt.Cerebro(stdstats=False)

# Add a strategy
cerebro.addstrategy(testStrategy)

# Load the Data
datapath =  './ticksample.csv'

# 原始数据列都处于默认位置，所以这里省略了不少指定列号的参数
data = btfeeds.GenericCSVData(
    dataname=datapath,
    dtformat='%Y-%m-%dT%H:%M:%S.%f',
    timeframe=bt.TimeFrame.Ticks,
)

cerebro.adddata(data)


# Run over everything
cerebro.run()





