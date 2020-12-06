# 番外1 bt订单的执行类型

backtrader支持多种订单执行方式（execute type），这里用代码来讨论不同执行方式的逻辑。

bt.Order中exectype参数表示执行方式，常用的执行方式有：

| TYPE      | 名称       | 成交逻辑                                                     |
| --------- | ---------- | ------------------------------------------------------------ |
| MARKET    | 市场单     | T0下单，T1按开盘价成交                                       |
| Limit     | 限价单     | T0下单，从T1日开始按 Open/High/Low/Close 四个价格按最优价（保证成交价格不劣于报价）成交 |
| Close     | 收盘价单   | T0下单，T1收盘价价格成交                                     |
| Stop      | 停止单     | T0下单，订单留在Broker中不发交易所，直到价格匹配成功后才发交易所按市场价尽快成交 |
| Stoplimit | 停止限价单 | 根据条件转换为Limit或Stop Order                              |

光看文字很枯燥，下面用代码来说明问题：

## 代码准备

首先我们准备测试用数据，下面是 平安银行（000001.SZ）2000年前5天的日线数据，后续的代码都基于这组数据进行：

| trade_date | open  | high  | low   | close |
| ---------- | ----- | ----- | ----- | ----- |
| 20000104   | 17.5  | 18.55 | 17.2  | 18.29 |
| 20000105   | 18.35 | 18.85 | 18.0  | 18.06 |
| 20000106   | 18.02 | 19.05 | 17.75 | 18.78 |
| 20000107   | 19.0  | 19.77 | 18.9  | 19.54 |
| 20000110   | 19.79 | 20.48 | 19.77 | 20.14 |

### Market Order

Market市场单，规则是T0下单，T1日按T1的开盘价成交。

我们程序中在1月4日下单，按逻辑将在第二天按5日开盘价(open=18.35)价格成交。

实现代码：

```python
def next(self):
    # 第1天，下单
    if len(self) == 1:
        order = self.buy(size=10, price=100, exectype=Order.Market)
        if order:
            self.log("下单BUY单(oid={id}), price={p}".format(id=order.ref, p=order.price))
```

输出结果：

```text
2000-01-04, 下单BUY单(oid=1), price=100
2000-01-05, 买单(oid=1)执行, 执行价=18.35，数量=10
```

### Close Order

Close收盘价单，规则是T0下单，T1日按T1的收盘价成交。

我们程序中在1月4日下单，按逻辑将在第二天按5日开盘价(open=18.35)价格成交。

实现代码：

```python
def next(self):
    # 第1天，下单
    if len(self) == 1:
        order = self.buy(size=10, price=100, exectype=Order.Close)
        if order:
            self.log("下单BUY单(oid={id}), price={p}".format(id=order.ref, p=order.price))
```

输出结果：

```text
2000-01-04, 下单BUY单(oid=1), price=100
2000-01-05, 买单(oid=1)执行, 执行价=18.06，数量=10
```

### Limit 限价单

Limit限价单，规则是T0下单，从T1日开始按 Open/High/Low/Close 四个价格寻找匹配，如匹配则按最优价（保证成交价格不劣于报价）成交，如到限定时刻还未成交，则订单取消。

限价单由于是按最优价成交，则不保证一定能成交。我们日常在A股市场上的挂单操作，都属于Limit Order。

下面是一个例子：

我们在4日下BUY单，限价17.6，由于到5日价格一直上升，则该单到回测结束仍无法成交；

然后在5日下BUY单，限价20.00，到6日价格小于20.00可匹配，则按当时市场价18.02价格成交(开盘即成交)；

最后我们在6日下SELL单，限价20.30，由于7日价格小于20无法成交，等到10日最高价高于20，则按当时最高价20.30价格成交。

实现代码：

```python
def next(self):
    if len(self) == 1:
        order = self.buy(size=10, price=17.60, exectype=Order.Limit)
        if order:
            self.log("下单BUY单(oid={id}), price={p}".format(id=order.ref, p=order.price))
    if len(self) == 2:
        order = self.buy(size=10, price=20.00, exectype=Order.Limit)
        if order:
            self.log("下单BUY单(oid={id}), price={p}".format(id=order.ref, p=order.price))
    if len(self) == 3:
        order = self.sell(size=10, price=20.30, exectype=Order.Limit)
        if order:
            self.log("下单SELL单(oid={id}), price={p}".format(id=order.ref, p=order.price))
```

输出结果：

```text
2000-01-04, 下单BUY单(oid=1), price=17.6
2000-01-05, 下单BUY单(oid=2), price=20.0
2000-01-06, 买单(oid=2)执行, 执行价=18.02，数量=10
2000-01-06, 下单SELL单(oid=3), price=20.3
2000-01-10, 卖单(oid=3)执行, 执行价=20.3，数量=-10
```

### Stop停止单

Stop限价单，规则是T0下单，订单留在Broker中不发交易所，直到价格匹配成功后才发交易所按市场价尽快成交。

与Limit有区别的是：

- Limit Order下单后就提交交易所，而Stop Order当价格匹配后才提交交易所；
- 中国没有Stop Order

关于Limit和Stop的更多不同，可以参考下图：

![img](番外1 bt订单的执行类型.assets/39ed53c03dc0612240616974029a5ed9_1440w.jpg)

下面例子中，

我们在4日下BUY单，限价19.00，6日价格能匹配，则按订单价成交；

我们在4日下BUY单，限价25.00，由于到回测结束还未达到这个价格，则订单不提交也不会成交；

然后在6日下SELL单，限价18.00，由于价格高企，则订单不提交也不会成交。

实现代码：

```python
def next(self):
    # 第1天，4日BUY单，价19
    if len(self) == 1:
        order = self.buy(size=10, price=19, exectype=Order.Stop)
        if order:
            self.log("下单BUY单(oid={id}), price={p}".format(id=order.ref, p=order.price))
        order = self.buy(size=10, price=25, exectype=Order.Stop)
        if order:
            self.log("下单BUY单(oid={id}), price={p}".format(id=order.ref, p=order.price))
    if len(self) == 3:
        order = self.sell(size=10, price=18, exectype=Order.Stop)
        if order:
            self.log("下单SELL单(oid={id}), price={p}".format(id=order.ref, p=order.price))
```

输出结果：

```text
2000-01-04, 下单BUY单(oid=1), price=19
2000-01-04, 下单BUY单(oid=2), price=25
2000-01-06, 买单(oid=1)执行, 执行价=19.0，数量=10
2000-01-06, 下单SELL单(oid=3), price=18
```

### StopLimit 限价停止单

Stop Order和Limit Order是在订单上设定一个价格触发条件，触发了则按市场价格进行成交。

与上述不同，Stop Limit是严格按下单人给出的价格成交（真实情况是非常接近这个价格）。StopLimit订单要设置两个参数：price和limit price（bt中称为plimit）。

当价格突破price时触发订单（类似于Order.Stop订单），之后以给定的价位plimit或者更好的价位执行订单（相当于以参数plimit为price的Order.Limit订单）

例子：

我们在4日下BUY单，price=19, plimit=20.14，则将在6日成交，按19.00成交(转为Limit Order)

实现代码：

```python
def next(self):
    # 第1天，4日BUY单，价19
    if len(self) == 1:
        order = self.buy(size=10, price=19, plimit=20.14, exectype=Order.StopLimit)
        if order:
            self.log("下单BUY单(oid={id}), price={p}, plimit={pl}".format(id=order.ref, p=order.price, pl=order.plimit))
```

输出结果：

```text
2000-01-04, 下单BUY单(oid=1), price=19, plimit=20.14
2000-01-06, 买单(oid=1)执行, 执行价=19.0，数量=10
```

### 完整代码

下面给出前文中的完整可执行代码：

```python
import backtrader as bt
import bc_study.tushare_csv_datafeed as ts_df
from backtrader.order import Order


# 基策略
class BaseOrderExetypeStrategy(bt.Strategy):
    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        pass

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # if order.status == order.Submitted:
            #     self.log('订单(oid={oid}) , Submitted'.format(oid=order.ref))
            # if order.status == order.Accepted:
            #     self.log('订单(oid={oid}) , Accepted'.format(oid=order.ref))
            return
        elif order.status in [order.Completed]:
            if order.isbuy():
                self.log('买单(oid={oid})执行, 执行价={ep}，数量={ea}'.format(oid=order.ref, ep=order.executed.price, ea=order.executed.size))
            elif order.issell():
                self.log('卖单(oid={oid})执行, 执行价={ep}，数量={ea}'.format(oid=order.ref, ep=order.executed.price, ea=order.executed.size))
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order(oid={oid}) Canceled/Margin/Rejected'.format(oid=order.ref))

    def next(self):
        pass


# 演示Market Order策略
class MarketOrderStrategy(BaseOrderExetypeStrategy):

    def next(self):
        # 第1天，下单
        if len(self) == 1:
            order = self.buy(size=10, price=100, exectype=Order.Market)
            if order:
                self.log("下单BUY单(oid={id}), price={p}".format(id=order.ref, p=order.price))


# 演示Close Order策略
class CloseOrderStrategy(BaseOrderExetypeStrategy):

    def next(self):
        # 第1天，下单
        if len(self) == 1:
            order = self.buy(size=10, price=100, exectype=Order.Close)
            if order:
                self.log("下单BUY单(oid={id}), price={p}".format(id=order.ref, p=order.price))


# 演示Limit Order策略
class LimitOrderStrategy(BaseOrderExetypeStrategy):

    def next(self):
        # 第1天，4日BUY单，限价17.6，无法成交
        if len(self) == 1:
            order = self.buy(size=10, price=17.60, exectype=Order.Limit)
            if order:
                self.log("下单BUY单(oid={id}), price={p}".format(id=order.ref, p=order.price))
        if len(self) == 2:
            order = self.buy(size=10, price=20.00, exectype=Order.Limit)
            if order:
                self.log("下单BUY单(oid={id}), price={p}".format(id=order.ref, p=order.price))
        if len(self) == 3:
            order = self.sell(size=10, price=20.30, exectype=Order.Limit)
            if order:
                self.log("下单SELL单(oid={id}), price={p}".format(id=order.ref, p=order.price))


# 演示Stop Order策略
class StopOrderStrategy(BaseOrderExetypeStrategy):

    def next(self):
        # 第1天，4日BUY单，价19
        if len(self) == 1:
            order = self.buy(size=10, price=19, exectype=Order.Stop)
            if order:
                self.log("下单BUY单(oid={id}), price={p}".format(id=order.ref, p=order.price))
            order = self.buy(size=10, price=25, exectype=Order.Stop)
            if order:
                self.log("下单BUY单(oid={id}), price={p}".format(id=order.ref, p=order.price))
        if len(self) == 3:
            order = self.sell(size=10, price=18, exectype=Order.Stop)
            if order:
                self.log("下单SELL单(oid={id}), price={p}".format(id=order.ref, p=order.price))


# 演示StopLimit Order策略
class StopLimitOrderStrategy(BaseOrderExetypeStrategy):

    def next(self):
        # 第1天，4日BUY单，价19
        if len(self) == 1:
            order = self.buy(size=10, price=19, plimit=20.14, exectype=Order.StopLimit)
            if order:
                self.log("下单BUY单(oid={id}), price={p}, plimit={pl}".format(id=order.ref, p=order.price, pl=order.plimit))


# 启动回测
def engine_run():
    # 初始化引擎
    cerebro = bt.Cerebro()

    # 给Cebro引擎添加策略
    cerebro.addstrategy(StopLimitOrderStrategy)

    # 设置初始资金：
    cerebro.broker.setcash(200000.0)

    # 从csv文件加载数据
    # 仅3天数据
    data = ts_df.get_csv_daily_data(
        stock_id="000001.SZ", start="20000104", end="20000110")
    cerebro.adddata(data)

    # 回测启动运行
    cerebro.run()


if __name__ == '__main__':
    engine_run()
```
