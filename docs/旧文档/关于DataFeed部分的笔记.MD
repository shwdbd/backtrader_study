# 关于DataFeed部分的笔记

DataFeed是BT回测数据的框架。

## 继承关系




## fda

基类：DataFeeds
子类：GenericCSV(DataFeeds)
子类：BacktraderCSV(GenericCSV)

下面介绍主要的属性：
- fromDate /  toDate :

### fromDate / toDate
- fromDate/toDate : Lines的起始日期
- ticktype : 日期元素的类型，如DAY, WEEK, MINTUES 

## DataFeed的客户化扩展

## 
