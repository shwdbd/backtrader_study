from datetime import datetime
import backtrader as bt
import os.path  # 管理路径
import sys  # 发现脚本名字(in argv[0])


class TurtleStrategy(bt.Strategy):
    #默认参数
    params = (
        ('H_period', 20),  # 唐奇安通道上轨周期
        ('L_period', 10),  # 唐奇安通道下轨周期
        ('ATRPeriod', 20),  # 平均真实波幅ATR周期
    )

    #交易记录日志（默认打印结果）
    def log(self, txt, dt=None, doprint=True):
        if doprint:
            dt = dt or self.datetime.date(0)
            print(f'{dt.isoformat()},{txt}')

    def __init__(self):
        # 初始化
        self.order = None  # 未决订单
        self.buyprice = 0  # 买单执行价格
        self.buycomm = 0  # 订单执行佣金
        self.buy_size = 0  # 买单数量
        self.buy_count = 0  # 买入次数计数

        # 海龟交易法则中的唐奇安通道和平均真实波幅ATR
        self.H_line = bt.indicators.Highest(
            self.data.high(-1), period=self.p.H_period)
        self.L_line = bt.indicators.Lowest(
            self.data.low(-1), period=self.p.L_period)
        self.ATR = bt.indicators.AverageTrueRange(
            self.data, period=self.p.ATRPeriod)

        # 价格与上下轨线的交叉
        self.buy_signal = bt.ind.CrossOver(self.data.close(0), self.H_line)
        self.sell_signal = bt.ind.CrossDown(self.data.close(0), self.L_line)

    def next(self):
        if self.order:
            return

        #入场：价格突破上轨线且空仓时
        if self.buy_signal and self.buy_count == 0:
             # 计算买入数量
            self.buy_size = self.broker.getvalue() * 0.01 / self.ATR 
            self.buy_size = int(self.buy_size / 100) * 100 

            self.buy_count += 1  # 买入次数计数
            self.log('创建买单')
            self.order = self.buy(size=self.buy_size)

        #加仓：价格上涨了买入价的0.5的ATR且加仓次数少于3次（含）
        elif self.data.close > self.buyprice + 0.5 * self.ATR[0] \
                and self.buy_count > 0 and self.buy_count <= 4:
             # 计算买入数量
            self.buy_size = self.broker.getvalue() * 0.01 / self.ATR 
            self.buy_size = int(self.buy_size / 100) * 100  

            self.log('创建买单')
            self.order = self.buy(size=self.buy_size)
            self.buy_count += 1  # 买入次数计数

        #离场：价格跌破下轨线且持仓时
        elif self.position:
            if self.sell_signal or self.data.close < (
                    self.buyprice - 2 * self.ATR[0]):
                self.log('创建卖单')
                self.order = self.close()  # 清仓
                self.buy_count = 0

    #记录交易执行情况（默认不输出结果）
    def notify_order(self, order):
        # 如果order为submitted/accepted,返回
        if order.status in [order.Submitted, order.Accepted]:
            return

        # 如果order为buy/sell executed,报告价格结果
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'买入:价格:{order.executed.price},\
                成本:{order.executed.value},\
                手续费:{order.executed.comm}')

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log(f'卖出:价格：{order.executed.price},\
                成本: {order.executed.value},\
                手续费{order.executed.comm}')

        # 如果指令取消/交易失败, 报告结果
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('交易失败%s' % order.getstatusname())
        self.order = None

    #记录交易收益情况（可省略，默认不输出结果）
    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log(f'策略收益：\n毛收益 {trade.pnl:.2f}, 净收益 {trade.pnlcomm:.2f}')

    def stop(self):
        self.log(
            f'(组合线：{self.p.H_period},{self.p.L_period})； \
        期末总资金: {self.broker.getvalue():.2f}',
            doprint=True)


##########################
# 主程序开始
#########################
if __name__ == '__main__':
    # 创建主控制器
    cerebro = bt.Cerebro()
    # 加入策略
    cerebro.addstrategy(TurtleStrategy)

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
        openinterest=-1,  # 无未平仓量列.(openinterest是期货交易使用的)
        dtformat=('%Y%m%d'),  # 日期格式
        fromdate=datetime(2019, 1, 1),  # 起始日
        todate=datetime(2020, 7, 8))  # 结束日

    cerebro.adddata(data)

    # broker设置资金、手续费
    cerebro.broker.setcash(1000000.0)
    cerebro.broker.setcommission(commission=0.001)

    print('初始资金: %.2f' % cerebro.broker.getvalue())
    # 启动回测
    cerebro.run()

    # 曲线绘图输出
    cerebro.plot()