# Backtrader API 参考手册

bt版本：1.9.76.123

## bt.Strategy

属性：

| 字段    | 类型          | 说明                                                         |
| ------- | ------------- | ------------------------------------------------------------ |
|         |               |                                                              |
| _trades | list of Trade | 返回所有Trade；是一个两层的list，第一层是DataFeed对象，第二层是tradeid（默认为0） |
|         |               |                                                              |

## Trade

属性：

| 字段    | 类型                                  | 说明                                                         |
| ------- | ------------------------------------- | ------------------------------------------------------------ |
|         |                                       |                                                              |
| tradeid | int                                   | 订单分类，默认为1，在下单时候可以指定，用于区分不同的交易类型。比如：self.buy(tradeid=1) |
| history | list of backtrader.trade.TradeHistory | 查看交易明细。TradeHistory有两个属性，分别是status和event，类型都是AutoOrderedDict，前者存放Trade状态，后者存放订单的信息 |
