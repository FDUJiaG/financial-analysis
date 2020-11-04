import tushare as ts
import sina_data
import pandas as pd
from pandas import DataFrame, Series
from datetime import datetime, timedelta
from dateutil.parser import parse
import time
import common_util
import os

'''
1. 开盘价，最高价，现价
2. 第一天价格逻辑 20%，44%
3. 低于流通值3%，低于开盘封单一半，封单绝对值小于3万手
'''


# 新股开板预警
def new_share_selling_signal():
    # 新股筛选
    # 获取股票列表
    pro = ts.pro_api('ba73b3943bdd57c2ff05991f7556ef417f457ac453355972ff5d01ce')
    basic_data = pro.stock_basic()
    print('股票筛选')
    # basic_data.to_excel(r'C:\Users\duanp\Desktop\test\stock_basic.xlsx')
    # basic_data = pd.read_excel(r'C:\Users\duanp\Desktop\test\stock_basic.xlsx')
    # 筛选上市日期为近一月的股票
    start_date = datetime.now() + timedelta(-30)
    end_date = datetime.now() + timedelta(1)
    basic_data['list_date'] = basic_data['list_date'].apply(lambda x: parse(str(x)))
    basic_data = basic_data[basic_data['list_date'] > start_date]
    basic_data = basic_data[basic_data['list_date'] < end_date]
    # 剔除科创板股票
    basic_data = basic_data[basic_data['market'] != '科创板']
    # 筛选未开板的股票
    basic_data['target_flag'] = basic_data.apply(lambda x: is_sold(x['ts_code'], x['list_date']), axis=1)
    basic_data = basic_data[basic_data['target_flag']]
    print('补充流通股本数据')
    # 补充流通股本信息
    basic_data['float_share'] = basic_data.apply(lambda x: get_float_share(x['ts_code']), axis=1)
    basic_data['float_share'] = basic_data['float_share'].fillna('100000')
    print('预警股票如下：')
    print(basic_data)
    # 判断当日是否开板
    while True:
        try:
            basic_data['target_code'] = basic_data['ts_code'].apply(lambda x: common_util.get_format_code(x, 'num'))
            tick_data = sina_data.get_tick_data(basic_data['ts_code'].to_list())
            tick_data['股票代码'] = tick_data['股票代码'].apply(lambda x: common_util.get_format_code(x, 'wind'))
            tick_data = tick_data[['股票代码', '买一量']]
            temp_data = basic_data.merge(tick_data, left_on='ts_code', right_on='股票代码')
            temp_data['flag'] = temp_data.apply(lambda x: float(x['买一量']) < float(x['float_share']) * 0.03, axis=1)
            temp_data = temp_data[temp_data['flag']]
            if len(temp_data) > 0:
                print('新股开板')
                print(temp_data)
                play_music()
                basic_data['drop_flag'] = basic_data['ts_code'].apply(lambda x: not (x in temp_data['ts_code'].tolist()))
                basic_data = basic_data[basic_data['drop_flag']]
                basic_data = basic_data.drop('drop_flag', axis=1)
            # print(tick_data)
            time.sleep(6)
        except Exception as e:
            print(e)
            time.sleep(6)


# 日K数据判断是否开板
def is_sold(code, start_date):
    print(code)
    try:
        time.sleep(1)
        pro = ts.pro_api('ba73b3943bdd57c2ff05991f7556ef417f457ac453355972ff5d01ce')
        start_date = (parse(str(start_date))+timedelta(1)).strftime('%Y%m%d')
        end_date = datetime.now().strftime('%Y%m%d')
        daily_k = pro.daily(ts_code=code, start_date=start_date, end_date=end_date)
        if len(daily_k) > 0:
            daily_k['flag'] = daily_k.apply(
                lambda x: x['high'] == x['low'] and x['open'] == x['close'] and x['high'] == x['low'],
                axis=1
            )
            flag = daily_k['flag'].sum()
            result = True
            for each in daily_k['flag'].tolist():
                result = result and each
            return result
        else:
            return True
    except Exception as e:
        print('再次请求ts数据')
        time.sleep(1)
        a = is_sold(code, start_date)
        return a


# 获取流通股本
def get_float_share(code):
    print(code)
    try:
        time.sleep(1)
        pro = ts.pro_api('ba73b3943bdd57c2ff05991f7556ef417f457ac453355972ff5d01ce')
        # target_date = datetime.now().strftime('%Y%m%d')
        target_data = []
        delta = 0
        count = 1
        while len(target_data) == 0:
            target_date = datetime.now()+timedelta(delta)
            target_data = pro.daily_basic(
                ts_code=code, trade_date=target_date.strftime('%Y%m%d'), fields='free_share'
            )
            delta = delta - 1
            time.sleep(0.5)
            count = count + 1
            if count > 3:
                return 1000000
        return target_data.values[0][0] * 10000

    except Exception as e:
        time.sleep(1)
        get_float_share(code)
        print('再次请求ts数据.....')


def play_music():
    file = r'C:\working_path\coding\data_handle\position_sum\src\bgmusic1.mp3'
    os.system(file)


def temp():
    pro = ts.pro_api('ba73b3943bdd57c2ff05991f7556ef417f457ac453355972ff5d01ce')
    data = pro.fut_daily(ts_code='IH1912.CFX', start_date='20190708', end_date='20190709')
    a = pro.fut_basic(exchange='CFFEX', fut_type='1', fields='ts_code,symbol,name,list_date,delist_date')
    data.to_excel(r'C:\working_path\test.xlsx')
    a.to_excel(r'C:\working_path\a.xlsx')


if __name__ == '__main__':
    new_share_selling_signal()
    # a = is_sold('002980.SZ','20200428')
    # print(a)
    # a = get_float_share('603439.SH')
    # print(a)
    # play_music()
    # temp()
