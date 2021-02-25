import backtrader as bt
import backtrader.analyzers as btanalyzers
import pandas as pd
import matplotlib
from datetime import datetime

# 定义双均线策略
class MaCrossStrategy(bt.Strategy):
 
    params = (
        ('fast_length', 10),
        ('slow_length', 50)
    )
     
    def __init__(self):
        ma_fast = bt.ind.SMA(period = self.params.fast_length)
        ma_slow = bt.ind.SMA(period = self.params.slow_length)
         
        self.crossover = bt.ind.CrossOver(ma_fast, ma_slow)
 
    def next(self):
        if not self.position:
            if self.crossover > 0: 
                self.buy()
        elif self.crossover < 0: 
            self.close()

if __name__ == "__main__":
    
    cerebro = bt.Cerebro()

  
    # 从yahoo在线api取得股票AAPL的日线数据
    data = bt.feeds.YahooFinanceData(dataname = 'AAPL', fromdate = datetime(2018, 1, 1), todate = datetime(2020, 1, 1))
    cerebro.adddata(data)

    #策略优化
    cerebro.optstrategy(
            MaCrossStrategy,
            fast_length = range(1, 11, 5), 
            slow_length = range(25, 35, 5))
    


    cerebro.broker.setcash(1000000.0)
    
    cerebro.addsizer(bt.sizers.PercentSizer, percents = 10)
    cerebro.addanalyzer(btanalyzers.SharpeRatio, _name = "sharpe")
    cerebro.addanalyzer(btanalyzers.DrawDown, _name = "drawdown")
    cerebro.addanalyzer(btanalyzers.Returns, _name = "returns")
    
    # 运行优化，由于每个参数组合运行一次策略，所以back是返回的策略实例列表（每个实例对应一组参数值）
    back = cerebro.run()


    # 每个策略实例的结果以列表的形式保存在列表中。
    # 优化运行模式下，返回值是列表的列表,内列表只含一个元素，即策略实例
    par_list = [[x[0].params.fast_length, 
                x[0].params.slow_length,
                x[0].analyzers.returns.get_analysis()['rnorm100'], 
                x[0].analyzers.drawdown.get_analysis()['max']['drawdown'],
                x[0].analyzers.sharpe.get_analysis()['sharperatio']
                ] for x in back]

    # 结果转成dataframe
    par_df = pd.DataFrame(par_list, columns = ['length_fast', 'length_slow', 'return', 'dd', 'sharpe'])

    print(par_df.head())

    par_df.to_csv('result.csv')
