import tushare as ts
# 设置token
ts.set_token('????')

# 行情结果存放到pandas dataframe，按日期降序排
df = ts.pro_bar(
    ts_code='600000.SH', adj='qfq', start_date='20000101', end_date='20200710') # 日线

# 颠倒顺序，使得按日期升序排。backtrader要求日期升序
df.sort_index(inplace=True, ascending=False)

df.to_csv('E:/backtradertutorial/600000d.csv')


#######################################################
# 行情结果存放到pandas dataframe，按日期降序排
df = ts.pro_bar(
    ts_code='600000.SH', adj='qfq', start_date='20000101', end_date='20200710', freq='W') # 周线

# 颠倒顺序，使得按日期升序排。backtrader要求日期升序
df.sort_index(inplace=True, ascending=False)

df.to_csv('E:/backtradertutorial/600000w.csv')