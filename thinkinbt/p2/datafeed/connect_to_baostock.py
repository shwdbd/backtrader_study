#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   connect_to_baostock.py
@Time    :   2021/02/26 20:20:18
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   尝试连接Baostock，并读取600016的日线数据
'''
import baostock as bs
import pandas as pd

#### 登陆系统 ####
lg = bs.login()
# 显示登陆返回信息
print('login respond error_code:'+lg.error_code)
print('login respond  error_msg:'+lg.error_msg)

#### 获取沪深A股历史K线数据 ####
# 详细指标参数，参见“历史行情指标参数”章节；“分钟线”参数与“日线”参数不同。“分钟线”不包含指数。
# 分钟线指标：date,time,code,open,high,low,close,volume,amount,adjustflag
# 周月线指标：date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg

# fields = "date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg"     # 周月线指标
fields = "date,time,code,open,high,low,close,volume,amount,adjustflag"  # 15分钟线


rs = bs.query_history_k_data_plus("sh.600016",
                                  fields=fields,
                                  start_date='2021-02-26', end_date='2021-02-26',
                                  frequency="15", adjustflag="3")
print('query_history_k_data_plus respond error_code:'+rs.error_code)
print('query_history_k_data_plus respond  error_msg:'+rs.error_msg)

#### 打印结果集 ####
data_list = []
while (rs.error_code == '0') & rs.next():
    # 获取一条记录，将记录合并在一起
    data_list.append(rs.get_row_data())
result = pd.DataFrame(data_list, columns=rs.fields)

# #### 结果集输出到csv文件 ####
# result.to_csv("D:\\history_A_stock_k_data.csv", index=False)
print(result)

#### 登出系统 ####
bs.logout()
