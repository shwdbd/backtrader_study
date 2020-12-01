# 5 Strategy策略

## 策略的执行流程

策略执行的过程中，Strategy实现类的各函数相应被调用，其调用顺序如下图所示：

![image-20201130170524360](5 Strategy策略.assets/image-20201130170524360.png)

说明：

- 如在 __init__() 中计算了SMA等需要窗口时间的指标，如窗口期还未结束则调用prenext，结束了调用next。



## 策略+分析器的执行流程

当回测中既有策略（Strategy）也有分析器（Analyzer）的时候，各函数回测调用顺序如下图：

![image-20201130174102919](5 Strategy策略.assets/image-20201130174102919.png)



