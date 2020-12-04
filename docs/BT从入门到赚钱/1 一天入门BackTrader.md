# BT从入门到赚钱(一) 一天入门BackTrader

本章节的目的是让读者用一天的时间（约4-5小时）对BackTrader有个初步了解，搭建第一个HelloWorld级的回测代码，引导完成官方的QuickStart示例。

这个系列文章，默认读者具备初步的量化投资概念和Python编程的初步知识背景。

[TOC]

## 为什么选择BackTrader

选择BackTrader的理由如下：

- 自2015年以来的开源软件，用户数多
- 本地回测框架，不依赖云资源
- 可使用多种数据源
- 纯Python
- 有内置的常用指标、分析器和绘图组件

综上，我觉得适用于个人量化开发者，减少架构开发工作量，如需要也可通过自定义代码实现个性化需求。

## HelloWorld

一门新语言的开发往往从HelloWorld开始，BT也是。

我们的HelloWorld将实现：

- 读取股票历史数据
- “装死”测试，不做任何事
- 期末输出回测结果（肯定不佳 :) ）

废话少说，先上代码：

```python
import backtrader as bt

if __name__ == '__main__':
    # 初始化引擎
    cerebro = bt.Cerebro()

    # 默认初始资金为20K，设置初始资金：
    cerebro.broker.setcash(100000.0)
    print('初始市值: %.2f' % cerebro.broker.getvalue())

    # 回测启动运行
    result = cerebro.run()
    print('期末市值: %.2f' % cerebro.broker.getvalue())
```

要想运行上述代码，您需要新建立一个Python的项目环境，并完成backtrader包的安装。

backtrader的安装可参考：[Installation - Backtrader](https://www.backtrader.com/docu/installation/)

## 官方QuickStart的实现

HelloWorld只是给了一个最简单的、可运行的示例，在Backtrader官网上有一个完整的[QuikcStart](https://www.backtrader.com/docu/quickstart/quickstart/)的Demo程序。
这个QuickStart逻辑清晰，初学者跟着跑一遍对BackTrader将有一个较为全面的了解，所以强烈推荐完成这个QuickStart。

新入坑者常常被QuickStart的数据源部分卡住，导致无法继续执行。官方代码中使用的是Yahoo的数据源，交易对象是美股。而针对国内小伙伴，更希望（也被迫）有一个友好的、国内数据源。我推荐的是用tushare在线数据api。

用下面的代码，更换QuickData中data对象生成部分：

```python
import backtrader as bt
import datetime
import pandas as pd
import backtrader.feeds as btfeeds

# 取得Data Feed对象
def get_tushare_online_daily_data():
    """将A股票日线数据返回BT Data
    """
    # 参数部分
    stock_id = "000001.SZ"
    start = "20190101"
    end = "20191231"
    dt_start = datetime.datetime.strptime(start, "%Y%m%d")
    dt_end = datetime.datetime.strptime(end, "%Y%m%d")
    TOKEN = 'abcd1234'

    ts.set_token(TOKEN)
    pro = ts.pro_api()

    try:
        # 加载数据
        df = pro.daily(ts_code=stock_id, start_date=start, end_date='end')
        df.sort_values(by=["trade_date"], ascending=True,
                       inplace=True)    # 按日期先后排序
        df.reset_index(inplace=True, drop=True)

        # 开始数据清洗：
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

        print(df.shape[0])
        # print(df.info())
        print(df.head())

        data = bt.feeds.PandasData(dataname=df, fromdate=dt_start, todate=dt_end)

        return data
    except Exception as err:
        print("下载{0}完毕失败！")
        print("失败原因 = " + str(err))
```

读者可自行修改上述代码中参数部分，其中TOKEN是tushare上的用户token，注册用户后即可得到。

## 附录 BackTrader的网络资源

常用的互联网资源：

- [官方网站](https://www.backtrader.com/)
- [Github](https://github.com/mementum/backtrader)
