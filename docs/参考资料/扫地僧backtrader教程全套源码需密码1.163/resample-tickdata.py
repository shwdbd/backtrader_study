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

data = btfeeds.GenericCSVData(
    dataname=datapath,
    dtformat='%Y-%m-%dT%H:%M:%S.%f',
    timeframe=bt.TimeFrame.Ticks,
)

# Handy dictionary for the argument timeframe conversion
tframes = dict(
    ticks=bt.TimeFrame.Ticks,
    microseconds=bt.TimeFrame.MicroSeconds,
    seconds=bt.TimeFrame.Seconds,
    minutes=bt.TimeFrame.Minutes,
    daily=bt.TimeFrame.Days,
    weekly=bt.TimeFrame.Weeks,
    monthly=bt.TimeFrame.Months)

# Resample the data    
cerebro.resampledata(
    data,
    timeframe=tframes['minutes'],
    compression=1,
    # bar2edge=1,
    # adjbartime=1,
    # rightedge=1
    )



# Run over everything
cerebro.run()

# Plot the result
# cerebro.plot(style='bar')



