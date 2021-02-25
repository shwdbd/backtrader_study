import tushare as ts
# 设置token，要用你自己的token号
ts.set_token('这里填你自己的token号')

# 行情结果存放到pandas dataframe，按日期降序排
df = ts.pro_bar(
    ts_code='600000.SH', adj='hfq', start_date='20000101',
    end_date='20200710')  # 日线,前复权qfq，后复权hfq

# 颠倒顺序，使得按日期升序排。backtrader要求日期升序
df.sort_index(inplace=True, ascending=False)

df.to_csv('E:/backtradertutorial/600000.csv')
