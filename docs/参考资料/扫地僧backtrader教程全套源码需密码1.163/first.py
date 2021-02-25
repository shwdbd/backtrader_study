'''
本代码仓库是教程《扫地僧Backtrader给力教程系列一：股票量化回测核心篇》的配套代码。

* 请加微信qtbhappy联系购买本教程纸质版及源码

* 若购买腾讯课堂视频教程“扫地僧Backtrader给力教程：量化回测核心篇（全集）”
则免费赠送纸质版教程。https://ke.qq.com/course/package/29579

* 未来内容勘误及修订扩展请关注我们的知乎专栏：
https://www.zhihu.com/people/optmaster/
可搜索我的知乎名字“optMaster”，到达专栏
需要购买该教程纸质版的用户请加微信 qtbhappy 联系购买。加微信时请输验证信息：backtrader。

'''


from datetime import datetime
import backtrader as bt
import os.path  # 管理路径
import sys  # 发现脚本名字(in argv[0])


# 创建策略类
class SmaCross(bt.Strategy):
    # 定义参数
    params = dict(period=5  # 移动平均期数
                  )

    def __init__(self):
        # 移动平均线指标
        self.move_average = bt.ind.MovingAverageSimple(
            self.datas[0].close, period=self.params.period)

    def next(self):
        
        if not self.position.size:  # 还没有仓位
            # 当日收盘价上穿5日均线，创建买单，买入100股
            if self.datas[0].close[-1] < self.move_average.sma[
                    -1] and self.datas[0].close[0] > self.move_average.sma[0]:
                self.buy(size=100)
        # 有仓位，并且当日收盘价下破5日均线，创建卖单，卖出100股
        elif self.datas[0].close[-1] > self.move_average.sma[-1] and self.datas[
                0].close[0] < self.move_average.sma[0]:
            self.sell(size=100)


##########################
# 主程序开始
#########################

# 创建大脑引擎对象
cerebro = bt.Cerebro()

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

cerebro.adddata(data)  # 将行情数据对象注入引擎
cerebro.addstrategy(SmaCross)  # 将策略注入引擎
cerebro.broker.setcash(10000.0)  # 设置初始资金
cerebro.run()  # 运行

print('最终市值: %.2f' % cerebro.broker.getvalue())

cerebro.plot(style='bar')