import tushare as ts
# 120分基础积分每分钟内最多调取500次，每次5000条数据，相当于23年历史
ts.set_token('???') 

df = ts.forecast_data(2020,2)
print(df.head())

df.to_csv('E:/backtradertutorial/tushareforecast.csv')
