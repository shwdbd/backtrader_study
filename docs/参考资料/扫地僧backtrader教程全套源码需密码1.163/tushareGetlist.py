import tushare as ts
# 设置token
ts.set_token('????')

pro = ts.pro_api()

stocklist = pro.stock_basic(
    exchange='',
    list_status='L',
    fields='ts_code,symbol,name,area,industry,list_date')

for i in range(100,200):
    ticker = stocklist['ts_code'].iloc[i]
    print(i,ticker)
    df = ts.pro_bar(
        ts_code=ticker,
        adj='qfq',
        freq='M',  # 月线
        start_date='20100101',
        end_date='20200710')
    # 颠倒顺序，使得按日期升序排。backtrader要求日期升序
    df.sort_index(inplace=True, ascending=False)
    df.to_csv('E:/backtradertutorial/data/%s.csv' % ticker)

