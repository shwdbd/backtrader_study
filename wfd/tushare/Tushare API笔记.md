# Tushare API笔记

    # TODO A股股票：
    # stock_basic 全量, 股票列表
    # trade_cal 交易日历
    # stock_company 上市公司基本信息
    
    # daily， 股票日线
    # pro_bar，复权行情 ？
    # daily_basic，每日指标
    # stk_limit，每日涨跌停价格
    # limit_list，每日涨跌停统计
    
    # TODO 指数
    # index_basic 指数基本信息
    # index_daily 指数日线行情
    # index_weekly， 指数周线行情
    # index_weight， 指数成分和权重

## A股数据

### 1. 股票列表(stock_basic)

[官方文档](https://waditu.com/document/2?doc_id=25)

**参数：**

- 上市状态，要多种merage后下载(L上市 D退市 P暂停上市，默认L)
- 交易所，两种都要（SSE上交所 SZSE深交所）
- 是否沪深港通，（N否 H沪股通 S深股通）
- 综上，需要 3*2*2=12个df的合并

**参数：**
- 默认字段很少，需要人为标识

**下载限制：**

- 记录限制：每天大约4000条？
- 

**检查规则：**

- 数量大约在xxxxx条

**下载限制：**



### 2. trade_cal 交易日历





### 3. 上市公司基本信息(stock_company )



### 4. daily， 股票日线



5. 






## 指数

## 公募基金


