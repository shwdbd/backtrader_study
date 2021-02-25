from datetime import datetime
import backtrader as bt
import numpy as np
import os.path  # 管理路径
import sys  # 发现脚本名字

class KalmanPair(bt.Strategy):
    params = (("printlog", True), ("quantity", 1000))

    def log(self, txt, dt=None, doprint=False):
        """Logging function for strategy"""
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print(f"{dt.isoformat()}, {txt}")

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # 订单状态 submitted/accepted，无动作
            return
        # 订单完成
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('买单执行, %.2f' % order.executed.price)
            elif order.issell():
                self.log('卖单执行, %.2f' % order.executed.price)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('订单 Canceled/Margin/Rejected')

    # 记录交易收益情况（可省略，默认不输出结果）
    def notify_trade(self, trade):
        if trade.isclosed:
            print('毛收益 %0.2f, 扣佣后收益 % 0.2f, 佣金 %.2f' %
                  (trade.pnl, trade.pnlcomm, trade.commission))

    
    
    
    def __init__(self):
        self.delta = 0.0001
        self.Vw = self.delta / (1 - self.delta) * np.eye(2)
        self.Ve = 0.001

        self.beta = np.zeros(2)
        self.P = np.zeros((2, 2))
        self.R = np.zeros((2, 2))

        self.position_type = None  # long or short
        self.quantity = self.params.quantity

    def next(self):
       
        x = np.asarray([self.data0[0], 1.0]).reshape((1, 2))
        y = self.data1[0]

        self.R = self.P + self.Vw  # state covariance prediction
        yhat = x.dot(self.beta)  # measurement prediction

        Q = x.dot(self.R).dot(x.T) + self.Ve  # measurement variance

        e = y - yhat  # measurement prediction error

        K = self.R.dot(x.T) / Q  # Kalman gain

        self.beta += K.flatten() * e  # State update
        self.P = self.R - K * x.dot(self.R)

        sqrt_Q = np.sqrt(Q)

        if self.position:
            if self.position_type == "long" and e > -sqrt_Q:
                self.close(self.data0)
                self.close(self.data1)
                self.position_type = None
            if self.position_type == "short" and e < sqrt_Q:
                self.close(self.data0)
                self.close(self.data1)
                self.position_type = None

        else:
            if e < -sqrt_Q:
                self.sell(data=self.data0, size=(self.quantity * self.beta[0]))
                self.buy(data=self.data1, size=self.quantity)

                self.position_type = "long"
            if e > sqrt_Q:
                self.buy(data=self.data0, size=(self.quantity * self.beta[0]))
                self.sell(data=self.data1, size=self.quantity)
                self.position_type = "short"

        self.log(f"beta: {self.beta[0]}, alpha: {self.beta[1]}")


##########################
# 主程序开始
#########################
if __name__ == '__main__':
    # 创建主控制器
    cerebro = bt.Cerebro()
    # 加入策略
    cerebro.addstrategy(KalmanPair)

    # 获取本脚本文件所在路径
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    # 拼接得到数据文件全路径
    datapath = os.path.join(modpath, './600000d.csv')

    # 创建行情数据对象，加载数据
    data = bt.feeds.GenericCSVData(
        dataname=datapath,
        datetime=2,  # 日期行所在列
        open=3,  # 开盘价所在列
        high=4,  # 最高价所在列
        low=5,  # 最低价所在列
        close=6,  # 收盘价价所在列
        volume=10,  # 成交量所在列
        openinterest=-1,  # 无未平仓量列.(openinterest是期货交易使用的)
        dtformat=('%Y%m%d'),  # 日期格式
        fromdate=datetime(2018, 1, 1),  # 起始日
        todate=datetime(2020, 12, 8))  # 结束日

    cerebro.adddata(data)

    # 拼接得到数据文件全路径
    datapath2 = os.path.join(modpath, './601398d.csv')

    # 创建行情数据对象，加载数据
    data2 = bt.feeds.GenericCSVData(
        dataname=datapath,
        datetime=2,  # 日期行所在列
        open=3,  # 开盘价所在列
        high=4,  # 最高价所在列
        low=5,  # 最低价所在列
        close=6,  # 收盘价价所在列
        volume=10,  # 成交量所在列
        openinterest=-1,  # 无未平仓量列.(openinterest是期货交易使用的)
        dtformat=('%Y%m%d'),  # 日期格式
        fromdate=datetime(2018, 1, 1),  # 起始日
        todate=datetime(2020, 12, 8))  # 结束日

    cerebro.adddata(data2)



    # broker设置资金、手续费
    cerebro.broker.setcash(1000000.0)
    cerebro.broker.setcommission(commission=0.001)

    print('初始资金: %.2f' % cerebro.broker.getvalue())
    # 启动回测
    cerebro.run()

    # 曲线绘图输出
    cerebro.plot()