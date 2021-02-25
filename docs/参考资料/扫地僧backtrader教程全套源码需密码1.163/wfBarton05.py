# https://community.backtrader.com/topic/501/walk-forward-analysis-demonstration
from sklearn.model_selection import TimeSeriesSplit
from sklearn.utils import indexable
from sklearn.utils.validation import _num_samples
import numpy as np


def createWFAReport(simParams, simulations):
    # Create simulation report format
    reportColumns = ['grossProfit', 'grossAverageProfit', 'maxProfit',
                     'grossLoss', 'grossAverageLoss', 'maxLoss',
                     'netProfit', 'averageNetProfit', 'NAR',
                     'recoveryFactor', 'MDDLength', 'MDD',
                     'wonTrade', 'lossTrade', 'tradingTime',
                     'averageTradeTime', 'TradeNumber', 'maxValue',
                     'minValue', 'totalCommission']
    simulationReport = pd.DataFrame(columns=reportColumns)

    # Loop Simulations to create summary
    for simulation in simulations:
        '''some Calculation is done here'''
    return simReport


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



# 程序入口
######################
if __name__ == "__main__":
    session = 'WinsWFAProd'
    stockList, indicatorDict, params = jsonConfigMap(session)
    params['timeString'] = '0621_113833'
    params['topResult'] = pd.read_csv(
        '{}{}/consoReport.csv'.format(params['resultLocation'], params['timeString']), index_col=0)
    params['resultLocation'] += params['timeString']+'/WFA'
    simulations = []

    try:
        # Create Folder
        shutil.rmtree(params['resultLocation'])
    except FileNotFoundError:
        pass
    except PermissionError:
        pass
    os.makedirs(params['resultLocation'], exist_ok=True)
    for element in ['order', 'trade', 'mr', 'ohlc', 'simulation', 'bestTrain', 'graph']:
        os.makedirs(params['resultLocation']+'/'+element, exist_ok=True)
    # Create master Log
    handler = logging.FileHandler(
        filename='{}/Master.log'.format(params['resultLocation']))
    handler.setFormatter(logging.Formatter(
        '%(asctime)s:%(name)s - %(levelname)s {}- %(message)s'))
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    # Create OptReport Log
    reportHandler = logging.FileHandler(
        filename='{}/optReport.csv'.format(params['resultLocation']))
    reportHandler.setFormatter(logging.Formatter('%(message)s'))
    reportHandler.setLevel(logging.INFO)
    reportLogger = logging.getLogger('report')
    reportLogger.addHandler(reportHandler)
    simResultColumns = ['stockName', 'market', 'indicator',
                        'grossProfit', 'grossAverageProfit', 'maxProfit',
                        'grossLoss', 'grossAverageLoss', 'maxLoss',
                        'netProfit', 'averageNetProfit', 'NAR', 'profitFactor',
                        'recoveryFactor', 'MDDLength', 'MDD',
                        'selfMDD', 'winRate', 'tradingTimeRatio',
                        'averageTradingBar', 'tradeNumber', 'maxValue',
                        'minValue', 'initialv', 'totalCommission',
                                    'barNumber', 'expectancy100', 'bnhReturn', 'bnhRatio']
    reportLogger.info(str(simResultColumns).strip(
        "[]").replace("'", "").replace(" ", ""))

    # Create Simulation Log
    oneLogger = logging.getLogger('oneLogger')
    oneLogger.propagate = False
    postHandler = logging.StreamHandler()
    postHandler.setLevel(logging.INFO)
    if params['selfLog']:
        oneLogger.setLevel(logging.DEBUG)
    else:
        oneLogger.setLevel(logging.INFO)
    oneLogger.addHandler(postHandler)
    # Record Start Time
    startTime = time.time()
    for row in params['topResult'].itertuples():
        simParams = pd.DataFrame(columns=['startTime', 'endTime', 'Parameter'])
        indicator = indicatorDict[row.indicator]
        stockName = row.stockName
        market = row.market
        try:
            optt = eval(indicator['optParam'])
        except:
            logger.info(
                '{}: Indicator does not have WFA parameters and skipped'.format(row.indicator))
            continue
        datafeed = feeder(stockName, market, params) # 这里应该是dataframe
        bnhReturn = round(
            datafeed.iloc[-1]['close'] - datafeed.iloc[0]['open'], 2)
        # Extract Feeder from Data to save time for multi-simulation
        print('Start WFA for {}-{} from {} to {}'.format(stockName,
                                                         row.indicator, datafeed.iloc[0].name, datafeed.iloc[-1].name))
        
        # 重要，数据划分，datafeed是dataframe，包含k线数据
        trainTestGenerator = WFASplit(
            datafeed, trainBy='8m', testBy='8m', loopBy='m')

        _ind = indicatorDict[row.indicator]
        # Training 样本内训练
        WFATrainResult = runTrain(trainTestGenerator, _ind, stockName)


        WFATrainResult = pd.DataFrame.from_records(WFATrainResult)
        WFATrainResult.to_csv('{}/bestTrain/{}_{}_train.csv'.format(
            params['resultLocation'], stockName, row.indicator), index=False)
        
        # TESTING 样本外测试
        _report = runTest(params, WFATrainResult, _ind, datafeed, stockName) # datafeed是dataframe

        
        # Consolidate T
        if _report[0] is not None:
            reportLogger.info(str(_report).strip("[]").strip(
                " ").replace(" ", "").replace("'", ""))
            simulations.append(_report)

    # After simulations
    simulations = pd.DataFrame(simulations)
    reportColumns = ['stockName', 'market', 'indicator',
                     'grossProfit', 'grossAverageProfit', 'maxProfit',
                     'grossLoss', 'grossAverageLoss', 'maxLoss',
                     'netProfit', 'averageNetProfit', 'NAR',
                     'profitFactor', 'recoveryFactor', 'MDDLength',
                     'selfMDD', 'winRate', 'tradingTimeRatio',
                     'averageTradingBar', 'tradeNumber', 'maxValue',
                     'minValue', 'initialv', 'totalCommission',
                     'barNumber', 'expectancy100', 'bnhReturn',
                     'bnhRatio']
    simulations.columns = reportColumns
    consoResult = cr.scoring(simulations)
    consoResult = consoResult.sort_values(['res'], ascending=False)
    consoResult.sort_values('res').to_csv(
        '{}/optReport.csv'.format(params['resultLocation']), index=False)

    timeRequired = time.time()-startTime
    print('timeRequired={:.2f}s'.format(timeRequired))
