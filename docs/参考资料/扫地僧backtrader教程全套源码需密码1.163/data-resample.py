#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
#
# Copyright (C) 2015, 2016 Daniel Rodriguez
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import argparse

import backtrader as bt
import backtrader.feeds as btfeeds
from datetime import datetime

class testStrategy(bt.Strategy):
    def next(self):
        print(self.data0.datetime.datetime(0),len(self.data0), self.data0.open[0],self.data0.high[0],self.data0.low[0],self.data0.close[0],)


def runstrat():
    args = parse_args()

    # Create a cerebro entity
    cerebro = bt.Cerebro(stdstats=False)

    # Add a strategy
    cerebro.addstrategy(testStrategy)

    # Load the Data
    datapath = args.dataname or 'D:/backtradertutorial/datas/2006-min-005.txt'  
    data = btfeeds.BacktraderCSVData(
        dataname=datapath, timeframe=bt.TimeFrame.Minutes,todate=datetime(2006, 1, 3))

    # Handy dictionary for the argument timeframe conversion
    tframes = dict(
        daily=bt.TimeFrame.Days,
        weekly=bt.TimeFrame.Weeks,
        monthly=bt.TimeFrame.Months)

    # Resample the data
    if args.oldrs:
        # Old resampler, fully deprecated
        data = bt.DataResampler(
            dataname=data,
            timeframe=bt.TimeFrame.Minutes,
            compression=1)

        # Add the resample data instead of the original
        cerebro.adddata(data)
    else:
        # New resampler
        print('new resample',tframes[args.timeframe],args.compression,)
        cerebro.resampledata(
            data,
            timeframe=bt.TimeFrame.Minutes,
            compression=2)

    # Run over everything
    cerebro.run()

    # Plot the result
    # cerebro.plot(style='bar')


def parse_args():
    parser = argparse.ArgumentParser(
        description='Resample down to minutes')

    parser.add_argument('--dataname', default='', required=False,
                        help='File Data to Load')

    parser.add_argument('--oldrs', required=False, action='store_true',
                        help='Use deprecated DataResampler')

    parser.add_argument('--timeframe', default='weekly', required=False,
                        choices=['daily', 'weekly', 'monthly'],
                        help='Timeframe to resample to')

    parser.add_argument('--compression', default=1, required=False, type=int,
                        help='Compress n bars into 1')

    return parser.parse_args()


if __name__ == '__main__':
    runstrat()
