# BackTrading的主要特征

## DataFeed

- 内置多种数据源（csv、在线api等）
- 使用Index作为访问机制
  - 0为当前时刻的数据，-1-2为之前的数据
  - 索引不能为正，从机制上禁止访问未来数据

## Broker

- 支持多订单类型：
  - Market
  - Limit
  - Stop
  - StopLimit
  - StopTrail
  - StopTrailLimit
  - OCO
  - Bracket
  - MarketOnClose
- 支持，多头卖空
- 佣金（客户自定义佣金方案）
- 基金模式
- 批量填充策略
- 滑点（自定义滑点）

## 指标

- 支持122个常用指标，包括：
  - 移动平均线类（SMA、EMA、...）
  - 经典（MACD、Stochastic、RSI）
  - 集成 ta-lib

## 性能分析

内置多种性能分析器

- TimeReturns
- TradeAnalyzer
- SharpeRatio
- VWR
- SQN

## 绘图

集合绘图语句
