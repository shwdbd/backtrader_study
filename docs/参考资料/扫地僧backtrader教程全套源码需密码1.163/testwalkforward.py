from datetime import datetime
from datetime import timedelta
import backtrader as bt
import os.path  # 管理路径
import sys  # 发现脚本名字(in argv[0])

#######################333
# walk forword相关
#########################
def WFASplit(self, trainBy='12m', testBy='3m', loopBy='m', overlap=True):
    startDate = self.index[0]
    endDate = self.index[-1]
    if trainBy[-1] is 'm':
        trainTime = relativedelta(months=int(trainBy[:-1])) # 取得训练时长，几个月
    else:
        raise ValueError
    if testBy[-1] is 'm':
        testTime = relativedelta(months=int(testBy[:-1]))  # 取得测试时长，几个月
    else:
        raise ValueError
    assert ((relativedelta(endDate, startDate)-trainTime).days) > 0

    if loopBy is 'm':
        # 似乎是训练开始时间列表而不是测试开始时间。从startDate开始，以测试时长为步长，依次增加，直到endDate-trainTime
        test_starts = zip(rrule(MONTHLY, dtstart=startDate,
                                until=endDate-trainTime, interval=int(testBy[:-1])))
    else:
        raise ValueError

    for i in test_starts:
        startD = i[0] #转成日期，i是tuple他的第0个元素是日期
        endD = i[0]+trainTime
        yield (self[(self.index >= startD) & (self.index < endD)],
               self[(self.index >= endD) & (self.index < endD+testTime)])
    return None



def runTrain(trainTestGenerator, _ind, stockName):
    WFATrainResult = []
    for train, test in trainTestGenerator:
        logger.debug('{} Training Data:{} to {}'.format(stockName, pd.DatetimeIndex.strftime(
            train.head(1).index, '%Y-%m-%d'), pd.DatetimeIndex.strftime(train.tail(1).index, '%Y-%m-%d')))
        # Generate Indicator ResultSet
        trainer = bt.Cerebro(cheat_on_open=True,
                             stdstats=False, optreturn=False)
        trainer.broker.set_cash(10000)
        # Add Commission
        IB = params['commission'](commission=0.0)
        trainer.broker.addcommissioninfo(IB)
        # Below Analyzer are used to calculate the Recovery Ratio
        trainer.addanalyzer(btanalyzers.TradeAnalyzer, _name='TradeAn')
        trainer.addanalyzer(
            recoveryAnalyzer, timeframe=params['analysisTimeframe'], _name='recoveryFac')
        trainer.addanalyzer(WFAAn, _name='WFAAna')
        trainer.addanalyzer(btanalyzers.TimeReturn,
                            timeframe=bt.TimeFrame.Months, _name='TR')
        # SetBroker
        trainer.broker.set_checksubmit(False)
        # Copy for tester
        tester = deepcopy(trainer)
        # Optimize Strategy
        trainingFile = '{}/WFA'
        trainer.optstrategy(trainingIdea,
                            inOrOut=(params['inOrOut'],),
                            selfLog=(params['selfLog'],),
                            indName=(row.indicator,),
                            indFormula=(_ind['formula'],),
                            entryExitPara=(_ind['entryExitParameters'],),
                            indOutName=(_ind['indValue'],),
                            nonOptParams=(None,),
                            resultLocation=(params['resultLocation'],),
                            timeString=(params['timeString'],),
                            market=(row.market,),
                            **optt)
        trainData = bt.feeds.PandasData(dataname=train)
        # Add a subset of data.
        trainer.adddata(trainData)
        optTable = trainer.run()
        final_results_list = []
        for run in optTable:
            for x in run:
                x.params['res'] = x.analyzers.WFAAna.get_analysis()
                final_results_list.append(x.params)

        _bestWFA = pd.DataFrame.from_dict(final_results_list, orient='columns').sort_values(
            'res', ascending=False).iloc[0].to_dict()
        bestTrainParams = {key: _bestWFA[key] for key in _bestWFA if key not in [
            'market', 'inOrOut', 'resultLocation', 'selfLog', 'timeString', 'res']}
        bestTrainParams = pd.DataFrame(bestTrainParams, index=[0])
        bestTrainParams['trainStart'] = train.iloc[0].name
        bestTrainParams['trainEnd'] = train.iloc[-1].name
        bestTrainParams['testStart'] = test.iloc[0].name
        bestTrainParams['testEnd'] = test.iloc[-1].name
        WFATrainResult.append(bestTrainParams)
    WFATrainResult = pd.concat(WFATrainResult)
    return WFATrainResult

def runTest(params, WFATrainResult, _ind, datafeed, stockName):
    # Generate Indicator ResultSet
    tester = bt.Cerebro(cheat_on_open=True)
    tester.broker.set_cash(10000)
    # Add Commission
    IB = params['commission'](commission=0.0)
    tester.broker.addcommissioninfo(IB)
    # SetBroker
    tester.broker.set_checksubmit(False)
    logger.debug('{} Start Testing'.format(stockName))
    OneSimHandler = logging.FileHandler(filename='{}/simulation/{}_{}_test.log'.format(
        params['resultLocation'], str(stockName), str(row.indicator)))
    OneSimHandler.setLevel(logging.DEBUG)
    OneSimHandler.setFormatter(logging.Formatter(
        "%(asctime)s:%(relativeCreated)d - %(message)s"))
    oneLogger.addHandler(OneSimHandler)
    tester.addstrategy(trainingIdea,
                       inOrOut=params['inOrOut'],
                       selfLog=params['selfLog'],
                       indName=row.indicator,
                       indFormula=_ind['formula'],
                       entryExitPara=_ind['entryExitParameters'],
                       indOutName=_ind['indValue'],
                       nonOptParams=None,
                       resultLocation=params['resultLocation'],
                       timeString=params['timeString'],
                       market=market,
                       WFATestParams=WFATrainResult)
    data = bt.feeds.PandasData(dataname=datafeed)
    tester.adddata(data, name=stockName)
    # Add analyzers for Tester
    tester.addanalyzer(btanalyzers.DrawDown, _name='MDD')
    tester.addanalyzer(btanalyzers.TradeAnalyzer, _name='TradeAn')
    tester.addanalyzer(btanalyzers.SQN, _name='SQN')
    tester.addanalyzer(
        recoveryAnalyzer, timeframe=params['analysisTimeframe'], _name='recoveryFac')
    tester.addanalyzer(ITDDAnalyzer, _name='ITDD')
    tester.addanalyzer(simpleAn, _name='simpleAna')
    tester.addanalyzer(btanalyzers.TimeReturn,
                       timeframe=bt.TimeFrame.Months, _name='TR')
    # Run and Return Cerebro
    cere = tester.run()[0]

    _report = cere.analyzers.simpleAna.writeAnalysis(bnhReturn)
    oneLogger.removeHandler(OneSimHandler)
    if params['plotGraph']:
        plotSimGraph(tester, params, stockName, row.indicator)
    return _report

########################################################
# 创建策略类
class SmaCross(bt.Strategy):
    # 定义参数
    params = dict(period=5  # 移动平均期数
                  )

    # 日志函数
    def log(self, txt, dt=None):
        '''日志函数'''
        dt = dt or self.datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # 移动平均线指标
        self.move_average = bt.ind.MovingAverageSimple(
            self.data, period=self.params.period)

        # 用来引用未决订单（即尚未执行的订单）
        self.order = None

    def notify_order(self, order):
        
        if order.status in [order.Submitted, order.Accepted]:
            # 订单状态 submitted/accepted，处于未决订单状态。不重置
            return

        # 订单已决，执行如下语句
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('买单执行, %.2f' % order.executed.price)

            elif order.issell():
                self.log('卖单执行, %.2f' % order.executed.price)

        elif order.status in [order.Canceled, order.Margin, order.Rejected,order.Expired]:
            self.log('订单 Canceled/Margin/Rejected/order.Expired: %s'%order.getstatusname())
            


        # 重置未决订单为空，表示无未决订单了
        self.order = None

    # 记录交易收益情况（可省略，默认不输出结果）
    def notify_trade(self, trade):
        print('trade')
        if trade.isclosed:
            print('毛收益 %0.2f, 扣佣后收益 % 0.2f, 佣金 %.2f' %
                  (trade.pnl, trade.pnlcomm, trade.commission))

    def next(self):
        # 如果有未决订单，则无动作，不再生成新订单
        if self.order:
            return

        if not self.position:  # 还没有仓位
            # 当日收盘价上穿5日均线，创建买单，买入100股
            if self.data.close[
                    -1] < self.move_average[-1] and self.data > self.move_average:
                self.log('创建买单')
                # 记录订单引用
                validday = self.data.datetime.datetime(0) + timedelta(days=7)
                self.order = self.buy(
                    size=100,
                    exectype=bt.Order.Limit,
                    price=0.99 * self.data, # 限价
                    valid=validday)
        # 有仓位，并且当日收盘价下破5日均线，创建卖单，卖出100股
        elif self.data.close[
                -1] > self.move_average[-1] and self.data < self.move_average:
            self.log('创建卖单')
            # 记录订单引用
            self.order = self.sell(size=100)


##########################
# 主程序开始
#########################

# 重要，数据划分，datafeed是dataframe，包含k线数据
trainTestGenerator = WFASplit(
    datafeed, trainBy='8m', testBy='8m', loopBy='m')

# Training 样本内训练
WFATrainResult = runTrain(trainTestGenerator, _ind, stockName)

# TESTING 样本外测试
    _report = runTest(params, WFATrainResult, _ind, datafeed, stockName) # datafeed是dataframe


# # 创建大脑引擎对象
# cerebro = bt.Cerebro()

# # 获取本脚本文件所在路径
# modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
# # 拼接得到数据文件全路径
# datapath = os.path.join(modpath, './600000qfq.csv')

# # 创建行情数据对象，加载数据
# data = bt.feeds.GenericCSVData(
#     dataname=datapath,
#     datetime=2,  # 日期行所在列
#     open=3,  # 开盘价所在列
#     high=4,  # 最高价所在列
#     low=5,  # 最低价所在列
#     close=6,  # 收盘价价所在列
#     volume=10,  # 成交量所在列
#     openinterest=-1,  # 无未平仓量列
#     dtformat=('%Y%m%d'),  # 日期格式
#     fromdate=datetime(2018, 1, 1),  # 起始日
#     todate=datetime(2020, 7, 8))  # 结束日

# cerebro.adddata(data)  # 将行情数据对象注入引擎
# cerebro.addstrategy(SmaCross)  # 将策略注入引擎

# cerebro.broker.setcash(10000.0)  # 设置初始资金
# cerebro.broker.setcommission(0.001)  # 佣金费率
# # 固定滑点，也可用cerebro.broker.set_slippage_perc()设置百分比滑点
# cerebro.broker.set_slippage_fixed(0.05)

# print('初始市值: %.2f' % cerebro.broker.getvalue())
# cerebro.run()  # 运行
# print('最终市值: %.2f' % cerebro.broker.getvalue())
# cerebro.plot()