import baostock as bs
import pandas as pd

#### 登陆系统 ####
lg = bs.login()
# 显示登陆返回信息
print('login respond error_code:' + lg.error_code)
print('login respond  error_msg:' + lg.error_msg)

#### 获取沪深A股历史K线数据 ####
# 详细指标参数，参见“历史行情指标参数”章节；“分钟线”参数与“日线”参数不同。
# 分钟线指标：date,time,code,open,high,low,close,volume,amount,adjustflag
rs = bs.query_history_k_data_plus(
    "sh.600000",
    "date,code,open,high,low,close,preclose,volume,\
    amount,adjustflag,turn,tradestatus,pctChg,isST",  # 输出字段列表
    start_date='2000-01-01',
    end_date='2020-07-13',
    frequency="d",  # 日线
    adjustflag="1")  # 复权类型，默认不复权：3；1：后复权；2：前复权
print('query_history_k_data_plus respond error_code:' + rs.error_code)
print('query_history_k_data_plus respond  error_msg:' + rs.error_msg)

#### 获得结果集dataframe ####

result = rs.get_data()

# 删除股票停牌的行记录
result = result[result.tradestatus == '1']  # tradestatus 1 正常交易， 0 停牌


#### 结果集输出到csv文件 ####
result.to_csv("E:/backtradertutorial/600000Baohfq.csv", index=False)


#### 登出系统 ####
bs.logout()