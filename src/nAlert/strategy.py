import os
import tushare as ts
import numpy as np
import pandas as pd
from pandas import DataFrame, Series
from datetime import datetime, timedelta
from dateutil.parser import parse
import time
from src.nAlert.common_util import get_format_code, TS_TOKEN
import src.nAlert.sina_data as sina_data

"""
1. 开盘价，最高价，现价
2. 第一天价格逻辑 20%，44%
3. 低于流通值 3%，低于开盘封单一半，封单绝对值小于 3 万手
"""


def get_time(date=False, utc=False, msl=3):
    if date:
        time_fmt = "%Y-%m-%d %H:%M:%S.%f"
    else:
        time_fmt = "%H:%M:%S.%f"

    if utc:
        return datetime.utcnow().strftime(time_fmt)[:(msl-6)]
    else:
        return datetime.now().strftime(time_fmt)[:(msl-6)]


def print_info(status="I"):
    return "\033[0;33;1m[{} {}]\033[0m".format(status, get_time())


# 新股开板预警
def new_share_selling_signal():
    # 新股筛选
    # 获取股票列表
    pro = ts.pro_api(TS_TOKEN)
    basic_data = pro.stock_basic()
    print(print_info(), end=" ")
    print("股票筛选")
    # basic_data.to_excel(r'C:\Users\duanp\Desktop\test\stock_basic.xlsx')
    # basic_data = pd.read_excel(r'C:\Users\duanp\Desktop\test\stock_basic.xlsx')
    # 筛选上市日期为近一月的股票
    start_date = datetime.now() + timedelta(-30)
    end_date = datetime.now() + timedelta(1)
    basic_data["list_date"] = basic_data["list_date"].apply(lambda x: parse(str(x)))
    basic_data = basic_data[basic_data['list_date'] > start_date]
    basic_data = basic_data[basic_data['list_date'] < end_date]
    # 剔除科创板股票
    basic_data = basic_data[basic_data['market'] != '科创板']
    # 剔除创业板股票
    basic_data = basic_data[basic_data['market'] != '创业板']
    print(print_info(), end=" ")
    print("删除注册制股票")
    # 筛选未开板的股票
    basic_data["target_flag"] = basic_data.apply(lambda x: is_sold(x['ts_code'], x['list_date']), axis=1)
    # basic_data = basic_data[basic_data['target_flag']]
    print(print_info(), end=" ")
    print("补充流通股本数据")
    # 补充流通股本信息
    basic_data['float_share'] = basic_data.apply(lambda x: get_float_share(x['ts_code']), axis=1)
    basic_data['float_share'] = basic_data['float_share'].fillna('100000')
    print(print_info(), end=" ")
    print("预警股票如下：")
    print(basic_data)

    change_rate = 0.01
    buy1_rate = 0.03
    buy1_volume = 1e5

    tick_list = [
        '股票代码',
        '今日开盘价',
        '昨日收盘价',
        '当前价',
        '今日最高价',
        '今日最低价',
        '成交股票数',
        '买一量'
    ]

    flag_dict = {
        "low_flag": "当日曾开板！",
        "price_flag": "已经开板！",
        "volume_top_flag": "换手率超过 {:.0%}！".format(change_rate),
        "buy1_percent_flag": "封单不足总流通市值的 {:.0%}！".format(buy1_rate),
        "buy1_volume_flag": "买一量不足 {} 股！".format(buy1_volume),
    }

    flag_list = list(flag_dict.keys())
    flag_len = len(flag_list)

    # 判断当日是否开板
    while True:
        localtime = time.localtime(time.time())
        tm_hour, tm_min = localtime.tm_hour, localtime.tm_min
        op_time = tm_hour + tm_min / 60
        # 交易时间，稍放宽
        if 9.2 <= op_time <= 11.6 or 12.9 <= op_time <= 15.1:
            try:
                basic_data['target_code'] = basic_data['ts_code'].apply(lambda x: get_format_code(x, 'num'))
                # tick_data = sina_data.get_tick_data(basic_data['ts_code'].to_list())
                tick_data = sina_data.get_tick_data(basic_data['symbol'].to_list())
                tick_data['股票代码'] = tick_data['股票代码'].apply(lambda x: get_format_code(x, 'wind'))
                tick_data = tick_data[tick_list]
                temp_data = basic_data.merge(tick_data, left_on='ts_code', right_on='股票代码')
                judge_list = judgement(temp_data, change_rate, buy1_rate, buy1_volume)
                # temp_data['flag'] = temp_data.apply(lambda x: float(x['买一量']) < float(x['float_share']) * 0.03, axis=1)
                alert_dict = dict()
                count = 0

                for idx in range(flag_len):
                    temp_data[flag_list[idx]] = judge_list[idx]
                    alert_dict[flag_list[idx]] = temp_data[temp_data[flag_list[idx]]]["name"].tolist()
                    if len(alert_dict[flag_list[idx]]) > 0:
                        print(print_info("W"), end=" ")
                        print(flag_dict[flag_list[idx]])
                        print("，".join(alert_dict[flag_list[idx]]))
                    else:
                        count += 1

                if count == flag_len:
                    print(print_info(), end=" ")
                    print("IPO Limit-Up！")

                # temp_data = temp_data[temp_data['flag']]
                # if len(temp_data) > 0:
                #     print('新股开板')
                #     print(temp_data)
                #     play_music()
                #     basic_data['drop_flag'] = basic_data['ts_code'].apply(lambda x: not (x in temp_data['ts_code'].tolist()))
                #     basic_data = basic_data[basic_data['drop_flag']]
                #     basic_data = basic_data.drop('drop_flag', axis=1)
                # print(tick_data)

            except Exception as e:
                print(e)
            time.sleep(6)

        elif 11.6 <= op_time <= 12.8:
            print(print_info(), end=" ")
            print("Lunch Break!")
            time.sleep(360)
        else:
            print(print_info(), end=" ")
            print("Not Trading Times")
            return True


def judgement(df, change_rate=0.01, buy1_rate=0.03, buy1_volume=1e5):
    float_share = df['float_share'].to_numpy().astype(np.int)
    open = df['今日开盘价'].to_numpy().astype(np.float)
    pre_close = df['昨日收盘价'].to_numpy().astype(np.float)
    limit_up = limit_up_price(pre_close)
    price = df['当前价'].to_numpy().astype(np.float)
    high = df['今日最高价'].to_numpy().astype(np.float)
    low = df['今日最低价'].to_numpy().astype(np.float)
    volume = df['成交股票数'].to_numpy().astype(np.int)
    buy_1v = df['买一量'].to_numpy().astype(np.int)

    judge_list = [
        low < limit_up,
        price < high,
        volume > float_share * change_rate,
        buy_1v < float_share * buy1_rate,
        buy_1v < buy1_volume
    ]

    return judge_list


# 基于前一交易日收盘价的涨停价计算
def limit_up_price(pre_close):
    return np.around(pre_close * 1.1, decimals=2)


# 日K数据判断是否开板
def is_sold(code, start_date):
    print(code)
    try:
        time.sleep(1)
        pro = ts.pro_api(TS_TOKEN)
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
        pro = ts.pro_api(TS_TOKEN)
        # target_date = datetime.now().strftime('%Y%m%d')
        target_data = []
        delta = 0
        count = 1
        while len(target_data) == 0:
            target_date = datetime.now() + timedelta(delta)
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
        print('再次请求 ts 数据.....')


def play_music():
    file = r'C:\working_path\coding\data_handle\position_sum\src\bgmusic1.mp3'
    os.system(file)


def temp():
    pro = ts.pro_api(TS_TOKEN)
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
