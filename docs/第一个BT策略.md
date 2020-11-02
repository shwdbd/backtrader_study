# 第一个BT策略

通过编写第一个可执行策略，初步探索backstrategy的使用。

## 策略的run框架

BT回测的运行，基本分为几个部分（阶段）进行：

1. 初始化引擎
2. 加载策略（允许加载多个策略）
3. 加载数据
4. 设置参数（起止日期、原始资金等）

```python
# 初始化引擎
cerebro = bt.Cerebro()

# 加载策略
cerebro.addstrategy(MyStrategy)

# 加载数据
# data = bt.feeds.YahooFinanceCSVData(dataname='TSLA.csv')
data = get_tushare_data()
cerebro.adddata(data)

# 设置参数
cerebro.broker.setcash(100000.0)
print("初始资金:%.2f" % cerebro.broker.getvalue())

# 运行
cerebro.run()
print("期末资金:%.2f" % cerebro.broker.getvalue())

```

## 数据的要求

引擎（cerebro）通过adddata方法得到数据集合（backtrader.feeds.pandafeed.PandasData对象），其特征有：

- PandasData是类似pandas.DataFrame的数据集合
- pd的index是日期，顺序排列
- 含有的字段有：open, high, low, close, vol和openinterest
- 可以从csv文件读取数据

## 时间序列的运行


