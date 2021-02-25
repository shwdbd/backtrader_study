#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from backtrader import Analyzer
from backtrader.mathsupport import average
from backtrader.utils import AutoOrderedDict


class Kelly(Analyzer):

    def create_analysis(self):
        '''Replace default implementation to instantiate an AutoOrdereDict
        rather than an OrderedDict'''
        self.rets = AutoOrderedDict()
      
    
    
    def start(self):
        super().start()
        self.pnlWins = list()  # 盈利列表：保留盈利交易利润额的列表
        self.pnlLosses = list()  # 亏损列表：保留亏损交易亏损额的列表

    def notify_trade(self, trade):
        if trade.status == trade.Closed:
            if trade.pnlcomm >= 0:
                # 盈利加入盈利列表，利润0算盈利
                self.pnlWins.append(trade.pnlcomm)
            else:
                # 亏损加入亏损列表
                self.pnlLosses.append(trade.pnlcomm)

    def stop(self):
        # 防止除以0
        if len(self.pnlWins) > 0 and len(self.pnlLosses) > 0:

            avgWins = average(self.pnlWins)  # 计算平均盈利
            avgLosses = abs(average(self.pnlLosses))  # 计算平均亏损（取绝对值）
            winLossRatio = avgWins / avgLosses  # 盈亏比

            if winLossRatio == 0:
                kellyPercent = None
            else:
                numberOfWins = len(self.pnlWins)  # 获胜次数
                numberOfLosses = len(self.pnlLosses)  # 亏损次数
                numberOfTrades = numberOfWins + numberOfLosses  # 总交易次数
                winProb = numberOfWins / numberOfTrades  # 计算胜率
                inverse_winProb = 1 - winProb

                # 计算凯利比率
                # 即每次交易投入资金占总资金的最优比率
                kellyPercent = winProb - (inverse_winProb / winLossRatio)
        else:
            kellyPercent = None  # 信息不足

        self.rets.kellyRatio = kellyPercent  # 例如 0.215
        self.rets.kellyPercent = kellyPercent * 100  # 例如 21.5
