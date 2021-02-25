
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


from datetime import datetime
import backtrader as bt
import os.path  # 用于管理路径
import sys  # 用于在argvTo[0]中找到脚本名称


class TheStrategy(bt.Strategy):
    '''
    This strategy is loosely based on some of the examples from the Van
    K. Tharp book: *Trade Your Way To Financial Freedom*. The logic:

      - Enter the market if:
        - The MACD.macd line crosses the MACD.signal line to the upside
        - The Simple Moving Average has a negative direction in the last x
          periods (actual value below value x periods ago)

     - Set a stop price x times the ATR value away from the close

     - If in the market:

       - Check if the current close has gone below the stop price. If yes,
         exit.
       - If not, update the stop price if the new stop price would be higher
         than the current
    '''

    params = (
        ('use_target_size', False),
        ('use_target_value', False),
        ('use_target_percent', False),
    )

    # 日志函数
    def log(self, txt, dt=None):
        '''日志函数'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def notify_order(self, order):       
        print('订单状态 ',order.getstatusname(order.status))
        if order.status in [order.Submitted, order.Accepted]:
            # 订单状态 submitted/accepted，无动作
            return

        # 订单完成
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('买单执行, price %.2f, size %d' % (order.executed.price, order.executed.size))

            elif order.issell():
                self.log('卖单执行, price %.2f, size %d' % (order.executed.price, order.executed.size))

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('订单 Canceled/Margin/Rejected, %d'%order.status)

        # 重置订单,表明已没有任何订单了
        self.order = None

        # if not order.alive():
        #     self.order = None  # indicate no order is pending

    def start(self):
        self.order = None  # sentinel to avoid operrations on pending order

    def next(self):
        self.log('open %.2f, close %.2f'%(self.data.open[0],self.data.close[0])) 
        dt = self.data.datetime.date()

        portfolio_value = self.broker.get_value()
        print('%04d - %s - Position Size:     %02d - Value %.2f' %
              (len(self), dt.isoformat(), self.position.size, portfolio_value))

        data_value = self.broker.get_value([self.data])
     
        if self.p.use_target_value:
            print('%04d - %s - data value %.2f' %
                  (len(self), dt.isoformat(), data_value))

        elif self.p.use_target_percent:
            port_perc = data_value / portfolio_value
            print('%04d - %s - data percent %.2f' %
                  (len(self), dt.isoformat(), port_perc))

        if self.order:
            return  # pending order execution

        size = dt.day
        if (dt.month % 2) == 0:
            size = 31 - size

        if self.p.use_target_size:
            target = size            
            print('%04d - %s - Order Target Size: %02d' %
                  (len(self), dt.isoformat(), size))

            self.order = self.order_target_size(target=size)

        elif self.p.use_target_value:
            value = self.p.use_target_value

            print('create order, %04d - %s - Order Target Value: %.2f' %
                  (len(self), dt.isoformat(), value))

            self.order = self.order_target_value(target=value)

        elif self.p.use_target_percent:
            percent = size / 100.0

            print('%04d - %s - Order Target Percent: %.2f' %
                  (len(self), dt.isoformat(), percent))

            self.order = self.order_target_percent(target=percent)


def runstrat(args=None):


    cerebro = bt.Cerebro()
    cerebro.broker.setcash(10000)



    # data
    # 获取本脚本文件所在路径
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    # 拼接得到数据文件全路径
    datapath = os.path.join(modpath, './600000qfq.csv')

    # 创建行情数据对象，加载数据
    data = bt.feeds.GenericCSVData(
        dataname=datapath,
        datetime=2,  # 日期行所在列
        open=3,  # 开盘价所在列
        high=4,  # 最高价所在列
        low=5,  # 最低价所在列
        close=6,  # 收盘价价所在列
        volume=10,  # 成交量所在列
        openinterest=-1,  # 无未平仓量列
        dtformat=('%Y%m%d'),  # 日期格式
        fromdate=datetime(2020, 1, 1),  # 起始日
        todate=datetime(2020, 5, 1))  # 结束日
          

    cerebro.adddata(data)

    # strategy
    cerebro.addstrategy(TheStrategy,
                        # use_target_size=200, # args.target_size,
                         use_target_value=50000, # args.target_value,
                        #use_target_percent=0.5) # args.target_percent
                        )

    cerebro.run()


runstrat()