from datetime import datetime
import pandas as pd
import numpy as np
import backtrader as bt
import os.path  # 管理路径
import sys  # 发现脚本名字(in argv[0])
from scipy.stats import linregress
import collections
import glob
import chardet


class Strategy(bt.Strategy):
    params = dict(
        rebal_monthday=[1],  # 每月1日执行再平衡
        num_cap = 1000, # 按市值取前多少支股票
        num_amount=800,  # 按成交额排序取前多少支股票
        pct_assetliability= 0.2, # 扣除资产负债率最高的20%个股
        num_roe=100, # 按roe取前100名
        num_pb=50, # 按pb取前50



    )

    def __init__(self):

        self.inds = collections.defaultdict(dict)

        # datas[0]存放数据spy（标普指数），其他股票数据放在stocks列表里
        self.stocks = self.datas[0:]
        self.lastRanks = [] # 初始化上次标的列表 
       

        self.add_timer(  # 定时器
            when=bt.Timer.SESSION_START,
            monthdays=self.p.rebal_monthday,  # 每月1号触发再平衡
            monthcarry=True,  # 若再平衡日不是交易日，则顺延触发notify_timer

        )

    def notify_timer(self, timer, when, *args, **kwargs):
        # print('notify', self.data0.datetime.date(0),len(self.data0.datetime),  self.data1.datetime.date(0),len(self.data1.datetime))
        # print('notify self', len(self))
        # if len(self)==0:  # 策略self自己是时间基准，要有长度才能执行后续操作。（注意，这里len(seld)比策略迭代表当前长度小1，所以实际上浪费了第一条记录，不过影响不大）
        #     return

        if(self.data0.datetime.date(0).month == 5 or self.data0.datetime.date(0).month == 9 or self.data0.datetime.date(0).month == 11):  # 只在5，9，11月的1号执行再平衡
            # print('notify', self.datetime.date(0), self.data0.datetime.date(0),len(self.data0.datetime),  self.data1.datetime.date(0),len(self.data1.datetime))
            self.rebalance_portfolio()

    def prenext(self):
        # 即使有些股票尚无当前数据，也跳转next执行
        # print('prenext',self.datetime.datetime().month)
        self.next()

    def next(self):
        # print('next', self.datetime.date(0), self.data0.datetime.date(0),  self.data1.datetime.date(0))
        # if(len(self)<20):
        #     print('next', self.data0.datetime.date(0),len(self.data0.datetime),  self.data1.datetime.date(0),len(self.data1.datetime))
        #     print('next self', len(self))
        pass

    def rebalance_portfolio(self):
        # print('in balance',self.data0.datetime.date(0))


        # 从stocks列表取出最大的日期，就是当前日期currDate
        currDate = max(list(d.datetime.date(0) for d in self.stocks if len(d)>0))
        # # 最终标的选取过程
        # # 1 先做排除筛选过程
        # self.ranks = [d for d in self.stocks if
        #               d.datetime.date(0) == currDate # 今日未停牌 (假设原始数据中已删除无交易的记录)
        #               and len(d) >= 3*252 # 到今天至少上市3年
        #               and 不是st,*st
        #               and 三年扣非roe>=10%
        #               and 三年平均扣非roe>=12%
        #               and 3年经营现金流净额合计>=利润合计
        #               and pe < 160
        #               ]  
        # # 2 再做排序挑选过程
        # self.ranks.sort(key=lambda d: d.cap, reverse = True) # 按市值从大到小排序
        # self.ranks = self.ranks[0:num_cap] # 取前1000名
        # assert len(self.ranks) == num_cap # 确保取到足够的数量

        # self.ranks.sort(key=lambda d: d.avg_amount, reverse = True) # 按日均成交额从大到小排序
        # self.ranks = self.ranks[0:num_amount] # 取前800名

        # ....其它排序规则




        
        # if len(self.ranks) != 50: # 不等于50只股票，则不操作
        #     return

        # # 3 以往买入的标的，本次不在标的中，则先平仓
        # data_toclose = set(self.lastRanks) - set(self.ranks)
        # for d in data_toclose:
        #     self.close(data=d)

        # # 4 本次标的下单
        # for d in self.ranks:
        #     o = self.order_target_percent(data=d, target=0.019) # 下单，每只股票分配账户价值的2%。未防止次日开票价格过高导致超过总账户价值，采用0.019的分配比例 
            

        # self.lastRanks = self.ranks # 跟踪上次买入的标的


    


##########################
# 主程序开始
#########################
cerebro = bt.Cerebro(stdstats=False)
# cerebro.broker.set_coc(True)  # 以收盘价成交


datadir = './dataswind'  # 数据文件位于本脚本所在目录的data子目录中
datafilelist = glob.glob(os.path.join(datadir, '*'))  # 数据文件路径列表
maxstocknum = 2  # 股票池最大股票数目
datafilelist = datafilelist[0:maxstocknum]  # 截取指定数量的股票池
print(datafilelist)
# 将目录datadir中的数据文件加载进系统
for fname in datafilelist:
    # with open(fname, 'rb') as f:
    #     # or readline if the file is large.确定文件编码
    #     result = chardet.detect(f.read())
    # df = pd.read_csv(
    #     fname, parse_dates=True, index_col=0, encoding='result['encoding']')
    
    df = pd.read_csv(
        fname, parse_dates=True, index_col=0, encoding='gbk')
    print(df.head())
    data = bt.feeds.PandasData(
        dataname=df,
        datetime=None,  # 使用索引列作日期列
        open=1,  # 开盘价所在列
        high=2,  # 最高价所在列
        low=3,  # 最低价所在列
        close=4,  # 收盘价价所在列
        volume=5,  # 成交量所在列
        openinterest=-1,  # 无未平仓量列.(openinterest是期货交易使用的)
        plot=False

    )
    cerebro.adddata(data)


cerebro.addstrategy(Strategy)
startcash = 1000000
cerebro.broker.setcash(startcash)
cerebro.broker.set_checksubmit(False)  # 防止先买后卖导致资金暂时不足时，订单被拒绝
results = cerebro.run()
