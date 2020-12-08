import tushare as ts

TOKEN = '341d66d4586929fa56f3f987e6c0d5bd23fb2a88f5a48b83904d134b'


def get_api():
    """取得tushare api连接

    Returns:
        [ts.pro_api]: tushare pro的api对象
    """
    ts.set_token(TOKEN)
    pro = ts.pro_api()
    return pro
