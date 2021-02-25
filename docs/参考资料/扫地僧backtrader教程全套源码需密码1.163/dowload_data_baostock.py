import baostock as bs
import pandas as pd
import datetime, os, sys

'''
日线指标参数包括：'date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,peTTM,pbMRQ,psTTM,pcfNcfTTM,isST'
周、月线指标参数包括：'date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg'
分钟指标参数包括：'date,time,code,open,high,low,close,volume,amount,adjustflag'

adjustflag：复权类型，默认不复权：3；1：后复权；2：前复权。已支持分钟线、日线、周线、月线前后复权。
'''

# 是否删除停盘数据
DROP_SUSPENSION = True
# DROP_SUSPENSION = False

# 获取当前目录
proj_path = os.path.dirname(os.path.abspath(sys.argv[0])) + '/../'


def update_stk_list(stk_type, out_file, date=None):
    # 获取指定日期的指数、股票数据
    stock_df = bs.query_all_stock(date).get_data()
    if 0 == len(stock_df):
        if date is not None:
            print('当前选择日期为非交易日或尚无交易数据，请设置date为历史某交易日日期')
            sys.exit(0)
        delta = 1
        while 0 == len(stock_df):
            stock_df = bs.query_all_stock(datetime.date.today() - datetime.timedelta(days=delta)).get_data()
            delta += 1
    stock_df.drop(stock_df[(stock_df.code < 'sh.600000') | (stock_df.code > 'sz.399000')].index, inplace=True)
    # 所有股票
    if '' == stk_type or 'all' == stk_type:
        pass
    # 主板
    elif 'main' == stk_type:
        stock_df.drop(stock_df[stock_df.code > 'sh.688000'].index, inplace=True)
    # 科创板
    elif 'star' == stk_type:
        stock_df.drop(stock_df[(stock_df.code < 'sh.688000') | (stock_df.code > 'sz.000000')].index, inplace=True)
    # 中小板
    elif 'ms' == stk_type:
        stock_df.drop(stock_df[(stock_df.code < 'sz.000000') | (stock_df.code > 'sz.300000')].index, inplace=True)
    # 创业板
    elif 'gem' == stk_type:
        stock_df.drop(stock_df[stock_df.code < 'sz.300000'].index, inplace=True)
    stock_df['code'].to_csv(out_file, encoding='gbk', index=False)


def load_stk_list(stk_type, date=None, update=False):
    data_path = '{}data/'.format(proj_path)
    data_file = '{}{}_stock_list.csv'.format(data_path, stk_type)
    # 判断是否存在data文件夹，若不存在，则创建data文件夹
    if not os.path.exists(data_path):
        os.makedirs(data_path)
    if not os.path.exists(data_file) or update:
        update_stk_list(stk_type, data_file, date)

    df = pd.read_csv(data_file)
    return df['code'].tolist()


def convert_time(t):
    H = t[8:10]
    M = t[10:12]
    S = t[12:14]
    return H + ':' + M + ':' + S


def download_data(stk_list, from_date='1990-12-19', to_date=datetime.date.today(),
                  datas='date,open,high,low,close,volume,amount,turn,pctChg',
                  frequency='d', adjustflag='2'):
    data_dir = proj_path + 'data/download/' + frequency + '/'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    for code in stk_list:
        print("Downloading :" + code)
        k_rs = bs.query_history_k_data_plus(code, datas, start_date=from_date, end_date=to_date.strftime('%Y-%m-%d'),
                                            frequency=frequency, adjustflag=adjustflag)

        data_file = data_dir + code + '.csv'
        out_df = k_rs.get_data()
        if DROP_SUSPENSION and 'volume' in list(out_df):
            out_df.drop(out_df[out_df.volume == '0'].index, inplace=True)
        # 做time转换
        if frequency in ['5', '15', '30', '60'] and 'time' in list(out_df):
            out_df['time'] = out_df['time'].apply(convert_time)
        out_df.to_csv(data_file, encoding='gbk', index=False)


if __name__ == '__main__':
    bs.login()

    # 获取下载股票数据列表, 如设置date参数，需确保date为交易日
    stk_list = load_stk_list('all', date=None, update=False) # 'all' 
    # stk_list = load_stk_list('main', date=None, update=False)
    # stk_list = load_stk_list('star', date=None, update=False)
    # stk_list = load_stk_list('ms', date=None, update=False)
    # stk_list = load_stk_list('gem', date=None, update=False)

    # 下载日线
    download_data(stk_list)
    # 下载周线
    # download_data(stk_list, frequency='w')
    # 下载月线
    # download_data(stk_list, frequency='m')
    # 下载5分钟线
    # download_data(stk_list, from_date='2020-6-1', frequency='5', datas='date,time,open,high,low,close,volume,amount')
    # 下载15分钟线
    # download_data(stk_list, from_date='2020-6-1', frequency='15', datas='date,time,open,high,low,close,volume,amount')
    # 下载30分钟线
    # download_data(stk_list, from_date='2020-6-1', frequency='30', datas='date,time,open,high,low,close,volume,amount')
    # 下载60分钟线
    # download_data(stk_list, from_date='2020-6-1', frequency='60', datas='date,time,open,high,low,close,volume,amount')
    bs.logout()
