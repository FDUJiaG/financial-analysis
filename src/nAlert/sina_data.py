import requests
import re
import pandas as pd
from pandas import DataFrame
from datetime import datetime
import time


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


def get_format_code(code):
    code = str(code)
    if len(code) < 6:
        code = '0' * (6 - len(code)) + code
    elif len(code) > 6:
        return code
    re_num = re.compile('\d{6}')
    sh_list = ['60', '68', '11', '13']
    sz_list = ['30', '00', '12']
    result = re_num.search(code).group()
    if result[:2] in sh_list:
        result = 'sh' + result
    elif result[:2] in sz_list:
        result = 'sz' + result
    else:
        result = result
    return result


def get_tick_data(code_list):
    # print(code_list)
    # 格式化股票代码
    target_code_list = []
    for code in code_list:
        target_code_list.append(get_format_code(code))
    # 请求数据
    target_url = r'http://hq.sinajs.cn/list=' + ','.join(target_code_list)
    response_context = requests.get(target_url)
    response_text = response_context.text
    response_text = response_text.replace(r'"', '')
    response_text = response_text.replace(r'var hq_str_', '')
    # 格式化返回数据
    target_list = []
    result = response_text.split(';')
    for each in result[:-1]:
        target_list.append(each.split(','))
    target_data = DataFrame(target_list)
    target_data = target_data.drop(target_data.columns[-1], axis=1)
    target_data = target_data.drop(target_data.columns[-1], axis=1)
    columns = [
        'name', '今日开盘价', '昨日收盘价', '当前价', '今日最高价', '今日最低价',
        '市价_买一', '市价_卖一', '成交股票数', '成交金额', '买一量', '买一价', '买二量',
        '买二价', '买三量', '买三价', '买四量', '买四价', '买五量', '买五价', '卖一量',
        '卖一价', '卖二量', '卖二价', '卖三量', '卖三价', '卖四量', '卖四价', '卖五量',
        '卖五价', '日期', '时间'
    ]
    try:
        target_data.columns = columns
    except Exception as e:
        target_data.columns = columns[:31]
    target_data['股票代码'] = target_data['name'].apply(lambda x: x.split('=')[0])
    target_data['股票名称'] = target_data['name'].apply(lambda x: x.split('=')[1])
    target_data = target_data.drop('name', axis=1)
    # target_data.to_excel(r'C:\Users\duanp\Desktop\001.xlsx')
    return target_data


# 获取买一价
def get_bid1(code):
    try:
        data = get_tick_data([code])
        target_price = data['买一价'].values[0]
        target_amount = data['买一量'].values[0]
        target_price = float(target_price)
        target_amount = float(target_amount)
        return target_price, target_amount
    except Exception as e:
        print(e)
        return 0, 0


# 获取卖一价
def get_ask1(code):
    try:
        data = get_tick_data([code])
        target_price = data['卖一价'].values[0]
        target_amount = data['卖一量'].values[0]
        target_price = float(target_price)
        target_amount = float(target_amount)
        return target_price, target_amount
    except Exception as e:
        print(e)
        return 0, 0


def start():
    while True:
        try:
            a = get_tick_data(['000001', '605118', '605199'])
            file_name = r'D:\PyProj\tick' + '\\' + datetime.now().strftime('%Y%m%d_%H%M%S') + r'.xlsx'
            print(print_info(), end=" ")
            print("Save the data to: {}".format(file_name))
            a.to_excel(file_name)
        except Exception as e:
            print(e)
        time.sleep(5.5)


if __name__ == '__main__':
    # a = get_tick_data(['002983', '002985', '002987', '300830', '300831', '603212', '603392', '603439'])
    # print(a)
    # a.to_excel(r'C:\Users\duanp\Desktop\test\tt.xlsx')
    # temp_price,temp_amount = get_bid1('002983')
    # print(temp_price)
    # print(temp_amount)
    # a = get_tick_data(['113518'])
    # print(a['当前价'])
    start()
