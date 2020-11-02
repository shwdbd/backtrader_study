#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   quickstart_demo0.py
@Time    :   2020/10/29 15:25:16
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   官方QuickStart第一个示例
'''

import backtrader as bt

if __name__ == '__main__':
    # 初始化引擎
    cerebro = bt.Cerebro()
    # 引擎启动后，broker会自动创建
    # 默认初始资金为10K，设置初始资金：
    cerebro.broker.setcash(200000.0)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # 回测启动运行
    cerebro.run()

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
