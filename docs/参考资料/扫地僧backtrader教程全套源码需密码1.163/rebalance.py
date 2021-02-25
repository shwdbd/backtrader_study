import datetime
import glob
import os.path

import backtrader as bt


class St(bt.Strategy):
    params = dict(
        selcperc=0.10,  # 股票池中挑选标的股票的比例
        rperiod=1,  # 收益率计算期数, 默认1期，即月度收益率
        vperiod=36,  # 波动率计算回看期数
        mperiod=12,  # 动量指标计算回看期数
        reserve=0.05  # 5% 预留资本
    )

    def log(self, arg):
        print('{} {}'.format(self.datetime.date(), arg))

    def __init__(self):
        # 计算要挑出的标的股票数量
        self.selnum = int(len(self.datas) * self.p.selcperc)

        # 为每支选中股票分配资金比率，预留部分资金以防止买股资金不足。
        # 计算购买数量都是以本期收盘价计算，而订单实际是以下期开盘价执行。
        # 因为开盘价可能上升，由此可能产生资金缺口
        self.perctarget = (1.0 - self.p.reserve) / self.selnum

        # 收益率指标计算
        rs = [bt.ind.PctChange(d, period=self.p.rperiod) for d in self.datas]
        # 波动率指标计算
        vs = [bt.ind.StdDev(ret, period=self.p.vperiod) for ret in rs]
        # 动量指标计算
        ms = [bt.ind.ROC(d, period=self.p.mperiod) for d in self.datas]

        # 数据:指标线字典，在next方法中，将按指标进行排序。
        # 对每个数据（股票），对应的评价指标为 ms/vs,它是线对象
        self.ranks = {d: m / v for d, v, m in zip(self.datas, vs, ms)}

    def next(self):       
        # 对数据：指标字典按指标当前值排序,结果ranks是list
        ranks = sorted(
            self.ranks.items(),  # 获得(d, 指标线)对
            key=lambda x: x[1][0],  # 按指标线(元素1) 的当前值（索引0） 排序
            reverse=True,  # 从大到小排序
        )

        # 把排序前selnum位的股票挑出来放进字典rtop，即选中排序表
        rtop = dict(ranks[:self.selnum])

        # 剩余的股票放进字典rbot
        rbot = dict(ranks[self.selnum:])

        # 当前持有仓位的股票列表
        posdata = [d for d, pos in self.getpositions().items() if pos]

        # 对未选中的（不在选中排序表中），但目前有仓位的股票，清仓
        # 先清仓以释放现金
        for d in (d for d in posdata if d not in rtop):
            self.log('Leave {} - Rank {:.2f}'.format(d._name, rbot[d][0]))
            self.order_target_percent(d, target=0.0)  # 清仓

        # 对当前有仓位，并且在选中排序表中的股票，进行仓位数量调整
        for d in (d for d in posdata if d in rtop):
            self.log('Rebal {} - Rank {:.2f}'.format(d._name, rtop[d][0]))
            self.order_target_percent(d, target=self.perctarget)  # 调整仓位数量
            del rtop[d]  # 排序表中，删除该股, 以简化下次迭代

        # 对剩余的新进排序表的股票（当前无仓位），买入
        # 本操作要最后做
        for d in rtop:
            self.log('Enter {} - Rank {:.2f}'.format(d._name, rtop[d][0]))
            self.order_target_percent(d, target=self.perctarget)


##########################
# 主程序开始
#########################

cerebro = bt.Cerebro()

datadir = './data'  # 数据文件位于本脚本所在目录的data子目录中
datafilelist = glob.glob(os.path.join(datadir, '*'))  # 数据文件路径列表
maxstocknum = 200  # 股票池最大股票数目
datafilelist = datafilelist[0:maxstocknum]  # 截取指定数量的股票池

# 将目录datadir中的所有数据文件加载进系统
for fname in datafilelist:
    data = bt.feeds.GenericCSVData(
        dataname=fname,
        datetime=2,  # 日期行所在列
        open=4,  # 开盘价所在列
        high=5,  # 最高价所在列
        low=6,  # 最低价所在列
        close=3,  # 收盘价价所在列
        volume=10,  # 成交量所在列
        openinterest=-1,  # 无未平仓量列
        dtformat=('%Y%m%d'),  # 日期格式
        fromdate=datetime.datetime(2010, 1, 1),  # 起始日
        todate=datetime.datetime(2020, 7, 10),  # 结束日
        timeframe=bt.TimeFrame.Months  # 月线数据
    )
    cerebro.adddata(data)

# 注入策略
cerebro.addstrategy(St)

# 设置现金
startcash = 1000000
cerebro.broker.setcash(startcash)

cerebro.run()

# 最终收益或亏损
pnl = cerebro.broker.get_value() - startcash
print('Profit ... or Loss: {:.2f}'.format(pnl))
