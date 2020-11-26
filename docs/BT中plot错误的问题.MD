# backtrader中plot错误的问题

在使用Backtrader初期，发生了很多绘图plot出错的问题，经一番折腾，问题都出在数据源(DataFeed)上。

为解决问题，本文专注于说明BT的DataFeed数据源的基本要求，为入门者提供方便。

[TOC]

## DataFeed的分类

BT的QuickStart使用的DataFeed是YahooFinanceCSVData，多适用于美股。针对国内A股，多是从tushare等接口下载csv文件，然后读取成为DataFeed这一模式。所以问题来了：

1. BT要求的csv文件格式是怎么样的？
2. 怎么将csv文件格式解析成为DataFeed类
3. 如何使用自定义的DataFeed?

## csv文件的格式

首先要说明的是BT理论上可以使用任意格式的csv文件。但为了尽快上手，这里介绍一个标准的csv文件格式。按这一格式，可以快速适用于BT框架。

标准的csv文件格式：

- 一个股票一个csv文件，每一行为一个Bar的数据；
- 有标题行；
- 列顺序为：ts_code,trade_date,open,high,low,close,pre_close,change,pct_chg,vol,amount；（这个列名是tushare默认下载的）
- 日期列，格式为20040812，即%Y%m%d。

这样的文件，读取数据的代码可写为：

```python
# 使用pandas读取csv文件的方式，读取DataFeed，其返回的是一个 backtrader.feeds.pandafeed.PandasData 对象

file_path = "600016SH.csv"
if not os.path.exists(file_path):
    print("数据源文件未找到！" + file_path)
    raise Exception("数据源文件未找到！" + file_path)

# 将csv文件转为pandas.dataframe
df = pd.read_csv(filepath_or_buffer=file_path)
# 按日期先后排序
df.sort_values(by=["trade_date"], ascending=True, inplace=True)
# 将日期列，设置成index
df.index = pd.to_datetime(df.trade_date, format='%Y%m%d')
# 增加一列openinterest
df['openinterest'] = 0.00
# 取出特定的列
df = df[['open', 'high', 'low', 'close', 'vol', 'openinterest']]
# 列名修改成指定的
df.rename(columns={"vol": "volume"}, inplace=True)

# 构建PandasData对象
data = bt.feeds.PandasData(dataname=df, fromdate=dt_start, todate=dt_end)
return data
```

## 自定义的DataFeed类

添加 用户定义 的新列

## Plot画出的图形要素初步说明
