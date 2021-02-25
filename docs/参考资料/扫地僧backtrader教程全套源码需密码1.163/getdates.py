import datetime
from datetime import timedelta


def gen_dates(b_date, days):
    day = timedelta(days=1)
    # print(day)
    for i in range(days):
        # print(b_date + day*i)
        yield b_date + day*i


def get_date_list(start_date, end_date):   #end_date=None
    """
    获取日期列表
    :param start: 开始日期
    :param end: 结束日期
    :return:
    """
    if start_date is not None:
        start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    if end_date is None:
        end = datetime.datetime.now()
    else:
        end = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    data = []
    for d in gen_dates(start, ((end-start).days + 1)):    # 29 + 1
        # print(d)   # datetime.datetime  类型
        data.append(d.strftime("%Y-%m-%d"))
    return data

def get_month_list(start_date, end_date):
    dates = get_date_list(start_date, end_date)
    months = []
    for i in dates:
        if i[:7] not in months:
            months.append(i[:7])
    return months


if __name__ == '__main__':
    start_date = '2002-04-01'
    end_date = '2015-12-31'
    datas=get_date_list(start_date, end_date)    # 两个日期之间的所有日期，包括开始日期， 包括 结束日期
    # for d in datas:
    #     print(d)
    
    with open('dates.txt','a') as file0:
        for d in datas:
            print(d,file=file0)
        
   