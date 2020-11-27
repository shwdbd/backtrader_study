#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   data_downloader.py
@Time    :   2020/10/29 16:48:20
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   Tushare下载数据文件
'''
import sys
import tushare as ts
import os

# 公共参数：
# 1. tushare的token:
TOKEN = '341d66d4586929fa56f3f987e6c0d5bd23fb2a88f5a48b83904d134b'
# 2. 下载地址：
LOCAL_DIR = os.path.join(os.path.dirname(
    os.path.abspath(sys.argv[0])), '../fd_data/')


# 将A股票日线数据下载到本地
def stock_daily_to_csv(stock_id="600016.SH", start="20190101", end="20191231"):
    """将A股票日线数据下载到本地

    Args:
        stock_id ([type], optional): [description]. Defaults to None.
        start ([type], optional): [description]. Defaults to None.
        end ([type], optional): [description]. Defaults to None.
    """
    ts.set_token(TOKEN)
    pro = ts.pro_api()

    # 如数据文件夹不存在，则新建之
    if not os.path.exists(LOCAL_DIR):
        os.makedirs(LOCAL_DIR)

    file_name = stock_id + ".csv"
    file_path = LOCAL_DIR + "/" + file_name

    try:
        # 加载数据
        df = pro.daily(ts_code=stock_id, start_date=start, end_date='end')
        df.sort_values(by=["trade_date"], ascending=True,
                       inplace=True)    # 按日期先后排序
        df.reset_index(inplace=True, drop=True)
        df.to_csv(path_or_buf=file_path, encoding='UTF-8', header=True, index=False)
        print(
            "下载{0}日线文件完毕 [记录数={1}] [时间范围 {2} - {3}]".format(stock_id, df.shape[0], start, end))
    except Exception as err:
        print("下载{0}完毕失败！")
        print("失败原因 = " + str(err))


def stock_basic_to_csv():
    """下载基本股票信息，下载为本地csv文件
    """
    ts.set_token(TOKEN)
    pro = ts.pro_api()

    # 如数据文件夹不存在，则新建之
    if not os.path.exists(LOCAL_DIR):
        os.makedirs(LOCAL_DIR)

    file_name = "stock_basic.csv"
    file_path = LOCAL_DIR + "/" + file_name

    try:
        # 加载数据
        df = pro.stock_basic(list_status='L')
        df.sort_values(by=["ts_code"], ascending=True, inplace=True)
        df.to_csv(path_or_buf=file_path, encoding='UTF-8', header=True)
        print("下载全部上市股票信息文件完毕 [记录数={0}]]".format(df.shape[0]))
    except Exception as err:
        print("下载{0}完毕失败！")
        print("失败原因 = " + str(err))


if __name__ == "__main__":
    start = "20000101"
    end = "20201110"
    # stock_daily_to_csv(stock_id="000002.SZ", start=start, end=end)
    # stock_daily_to_csv(stock_id="600016.SH", start=start, end=end)
    stock_daily_to_csv(stock_id="000001.SZ", start=start, end=end)
    # stock_basic_to_csv()
