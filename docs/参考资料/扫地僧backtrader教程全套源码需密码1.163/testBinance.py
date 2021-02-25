# 从Binance币安在线api下载1分钟k线，进行回测
import requests 
import backtrader as bt
import backtrader.analyzers as btanalyzers
import json 
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt

def get_binance_bars(symbol, interval, startTime, endTime):
 
    url = "https://api.binance.com/api/v3/klines"
 
    startTime = str(int(startTime.timestamp() * 1000))
    endTime = str(int(endTime.timestamp() * 1000))
    limit = '1000'
 
    req_params = {"symbol" : symbol, 'interval' : interval, 'startTime' : startTime, 'endTime' : endTime, 'limit' : limit}
 
    df = pd.DataFrame(json.loads(requests.get(url, params = req_params).text))
 
    if (len(df.index) == 0):
        return None
     
    df = df.iloc[:, 0:6]
    df.columns = ['datetime', 'open', 'high', 'low', 'close', 'volume']
 
    df.open      = df.open.astype("float")
    df.high      = df.high.astype("float")
    df.low       = df.low.astype("float")
    df.close     = df.close.astype("float")
    df.volume    = df.volume.astype("float")
    
    df['adj_close'] = df['close']
     
    df.index = [dt.datetime.fromtimestamp(x / 1000.0) for x in df.datetime]
 
    return df

df_list = []
# 数据起点时间
last_datetime = dt.datetime(2020, 11, 23)
while True:
    new_df = get_binance_bars('ETHUSDT', '1m', last_datetime, dt.datetime.now()) # 获取1分钟k线数据
    
    if new_df is None:
        break
    df_list.append(new_df)
    last_datetime = max(new_df.index) + dt.timedelta(0, 1)
 
df = pd.concat(df_list)
df.shape

class MaCrossStrategy(bt.Strategy):
 
    def __init__(self):
        ma_fast = bt.ind.SMA(period = 10)
        ma_slow = bt.ind.SMA(period = 50)
         
        self.crossover = bt.ind.CrossOver(ma_fast, ma_slow)
 
    def next(self):
        if not self.position:
            if self.crossover > 0: 
                self.buy()
        elif self.crossover < 0: 
            self.close()

cerebro = bt.Cerebro()
print('k线数量', len(df)) 
data = bt.feeds.PandasData(dataname = df)
cerebro.adddata(data)
 
cerebro.addstrategy(MaCrossStrategy)
cerebro.broker.setcash(1000000.0)
 
cerebro.addsizer(bt.sizers.PercentSizer, percents = 50)
cerebro.addanalyzer(btanalyzers.SharpeRatio, timeframe=bt.TimeFrame.Minutes, _name = "sharpe")
cerebro.addanalyzer(btanalyzers.Transactions, _name = "trans")

back = cerebro.run()

print('最终市值', cerebro.broker.getvalue()) # Ending balance
print(back[0].analyzers.sharpe.get_analysis()) # Sharpe
print(len(back[0].analyzers.trans.get_analysis())) # Number of Trades

