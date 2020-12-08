#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   main.py
@Time    :   2020/12/07 10:46:28
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   tushare数据下载的总入口
'''


def dl_on_stocks(start_date="20200101"):
    """下载存量数据
    """
    # TODO A股股票：
    # stock_basic 全量, 股票列表
    # trade_cal 交易日历
    # stock_company 上市公司基本信息

    # daily， 股票日线
    # pro_bar，复权行情 ？
    # daily_basic，每日指标
    # stk_limit，每日涨跌停价格
    # limit_list，每日涨跌停统计

    # TODO 指数
    # index_basic 指数基本信息
    # index_daily 指数日线行情
    # index_weekly， 指数周线行情
    # index_weight， 指数成分和权重

    pass


def dl_daily(date_date=None):
    """每日数据下载
    """

    pass


if __name__ == "__main__":
    # 下载存量数据
    dl_on_stocks()

    # 下载增量数据
    # dl_daily()
