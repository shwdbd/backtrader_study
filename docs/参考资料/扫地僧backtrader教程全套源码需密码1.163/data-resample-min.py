from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


import backtrader as bt
import backtrader.feeds as btfeeds
from datetime import datetime


class testStrategy(bt.Strategy):
    def next(self):
        print(self.data0.datetime.datetime(0), len(self.data0),
              self.data0.open[0], self.data0.high[0], self.data0.low[0], self.data0.close[0],)


# Create a cerebro entity
cerebro = bt.Cerebro(stdstats=False)

# Add a strategy
cerebro.addstrategy(testStrategy)

# Load the Data
datapath = './2006-min-005.csv'
data = btfeeds.BacktraderCSVData(
    dataname=datapath, timeframe=bt.TimeFrame.Minutes,
    todate=datetime(2006, 1, 3),
)


cerebro.resampledata(
    data,
    timeframe=bt.TimeFrame.Minutes,
    compression=2)


cerebro.run()
