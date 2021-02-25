# example of optimizing SMA crossover strategy parameters using 
# Particle Swarm Optimization in the opptunity python library
# https://github.com/claesenm/optunity

from datetime import datetime
import backtrader as bt

import optunity
import optunity.metrics
import os.path  # 管理路径
import sys  # 发现脚本名字(in argv[0])



class SmaCross(bt.Strategy): # 这是信号策略
    params = (
        ('sma1', 10), # 需要优化的参数1，短期均线窗口
        ('sma2', 30), # 需要优化的参数2，长期均线窗口
    )
    def __init__(self):
        SMA1 = bt.ind.SMA(period=int(self.params.sma1)) # 用int取整
        SMA2 = bt.ind.SMA(period=int(self.params.sma2)) # 用int取整
        self.crossover = bt.ind.CrossOver(SMA1, SMA2)


    
    def next(self):
        if not self.position:           
            if self.crossover > 0:              
                self.buy(size=100)
       
        elif self.crossover < 0:            
            self.sell(size=100)





################
# 主程序入口
##############

# 获取本脚本文件所在路径
modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
# 拼接得到数据文件全路径
datapath = os.path.join(modpath, './600000qfq.csv')

# 创建行情数据对象，加载数据
data0 = bt.feeds.GenericCSVData(
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
    todate=datetime(2019, 12, 31))  # 结束日


# 评估函数，输入参数，返回评估函数值，这里是总市值，要求最大化
def runstrat(sma1,sma2):
    
    print('I am called',datetime.now().strftime('%H:%M:%S'))
    cerebro = bt.Cerebro()
    cerebro.addstrategy(SmaCross, sma1=sma1, sma2=sma2)

    cerebro.adddata(data0)
    cerebro.broker.setcash(10000.0)  # 设置初始资金
    cerebro.run()
    return cerebro.broker.getvalue()


#  执行优化，第一个参数是评估函数
# 执行5次回测（num_evals,实战时回测次数要设大一些，比如100次），设置两个参数sma1,sma2的取值范围
# solver_name可取算法包括 particle swarm,sobol,random search,cma-es,grid search
opt = optunity.maximize(runstrat,  num_evals=10,solver_name='particle swarm', sma1=[2, 55], sma2=[2, 55])



########################################
# 优化完成，得到最优参数结果
optimal_pars, details, _ = opt
print('Optimal Parameters:')
print('sma1 = %.2f' % optimal_pars['sma1'])
print('sma2 = %.2f' % optimal_pars['sma2'])
# 利用最优参数最后回测一次，作图
cerebro = bt.Cerebro()
cerebro.addstrategy(SmaCross, sma1=optimal_pars['sma1'], sma2=optimal_pars['sma2'])
cerebro.adddata(data0)
cerebro.run()
cerebro.plot()