#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   get_all_trades.py
@Time    :   2021/02/24 19:59:48
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   读取已经发生过的所有Trade

逻辑：
1. 买100股，卖50股
2. 卖50股，Trade结束
3. 再卖100股，新Trade
4. 买入100股，第二个Trade结束
5. 查看所有的Trade

'''

# here put the import lib
