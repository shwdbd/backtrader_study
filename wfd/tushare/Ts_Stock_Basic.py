#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   Ts_Stock_Basic.py
@Time    :   2020/12/07 11:31:56
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   None
'''
import wfd.tushare.ts_cfg as cfg
import datetime, os


class BaseDL:
    _data = None    # 数据的dataframe对象


    def log(self, msg):
        dt = datetime.date.today()
        print('%s, %s' % (dt.isoformat(), msg))

    def set_data(self, df):
        # 设置数据源
        self._data = df

    def get_data(self):
        # 取得数据源
        return self._data

    def save_to_localfile(self):
        # 存放到本地文件中

        # TODO 生成文件，要统一上base中
        
        if self.get_data() is None or self.get_data().empty:
            self.log("数据未下载或下载数据为空！")
        else:
            file_path = self.params["file_path"]
            self.get_data().to_csv(file_path, index=False, encoding="UTF-8")    # 参数要可配置
            self.log("下载成功")


class StockBasicDL(BaseDL):
    """A股股票列表
    """

    _data = None

    fields = ['ts_code', 'symbol', 'name', 'area', 'industry', 'fullname', 'enname',
              'market', 'exchange', 'curr_type',  'list_status', 'list_date', 'delist_date', 'is_hs']

    params = {
        'file_path': "C:/fd_data/tushare/stock_basic/stock_basic.csv",
    }

    def receive(self):
        """接受并加载数据


        """
        try:

            # self.log(",".join(self.params["fields"]))

            # TODO 各df的分别取得和合并

            # 加载数据
            df1 = cfg.get_api().stock_basic(list_status='L', exchange='SSE', is_hs='N',
                                            fields=",".join(self.fields))
            # self.log(df1.head())

            df2 = cfg.get_api().stock_basic(list_status='L', exchange='SSE', is_hs='H',
                                            fields=",".join(self.fields))
            # self.log(df2.head())

            # 合并
            df_all = df1.append(df2)
            self.log(df_all.head())
            return df_all
        
        except Exception as err:
            self.log("失败原因 = " + str(err))
            return None


if __name__ == "__main__":
    dl = StockBasicDL()
    df = dl.receive()
    dl.set_data(df)
    dl.save_to_localfile()
