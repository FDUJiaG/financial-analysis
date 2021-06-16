import re
from dateutil.parser import parse
import pandas as pd
import calendar
import os
import os.path
import time
from datetime import datetime

TS_TOKEN = "ba73b3943bdd57c2ff05991f7556ef417f457ac453355972ff5d01ce"


# 格式化标的代码
def get_format_code(code, format_class):
    """
    format_class  要求的 format 类型：
    wind  000001.SZ
    sina  sz000001
    num   000001
    tushare 同 wind
    """
    code = str(code)
    if len(code) < 6:
        code = '0' * (6 - len(code)) + code
    elif len(code) > 9:
        return code
    re_num = re.compile("\d{6}")
    sh_list = ['60', '68', '11', '13']
    sz_list = ['30', '00', '12']
    try:
        result = re_num.search(code).group()
    except Exception as e:
        return code
    if format_class == 'num':
        return result
    elif format_class == 'sina':
        if result[:2] in sh_list:
            result = 'sh' + result
        elif result[:2] in sz_list:
            result = 'sz' + result
        else:
            result = result
    elif format_class == 'wind' or format_class == 'tushare':
        if result[:2] in sh_list:
            result = result + r'.SH'
        elif result[:2] in sz_list:
            result = result + r'.SZ'
        else:
            result = result

        return result


# 标的种类划分
def get_asset_class(code):
    code = str(code)
    if code.startswith('1002') and len(code) == 4:
        return '银行存款'
    if code.startswith('1021') and len(code) == 4:
        return '结算备付金'
    elif code.startswith('1031') and len(code) == 4:
        return '存出保证金'
    elif code.startswith('1102') and len(code) == 14 and (not code[6:8]=='99'):
        return '股票投资'
    elif code.startswith('1103') and len(code) == 14 and (not code[6:8]=='99'):
        return '债券投资'
    elif code.startswith('1105') and len(code) == 14 and (not code[6:8]=='99'):
        return '基金投资'
    elif code.startswith('1109') and len(code) == 14 and (not code[6:8]=='99'):
        return '其他投资'
    elif code.startswith('1204') and len(code) == 4:
        return '应收利息'
    elif code.startswith('22') and len(code) == 4:
        return '负债'
    elif code== '实收资本':
        return '实收资本'
    elif code.startswith('2') and len(code)==4:
        return '其他负债'
    elif code.startswith('1') and len(code) == 4:
        return '其他资产'
    else:
        return '未知分类'


# 生成一个区间内的每个月末月初序列
def gen_month_series(start_date, end_date):
    start_date = parse(start_date).strftime('%Y%m%d')[:6] + r'01'
    date_series = pd.date_range(start_date, end_date)
    start_date_list = []
    end_date_list = []
    for date in date_series:
        date = date.strftime('%Y%m%d')
        if date[-2:]=='01':
            start_date_list.append(date)
            month_range = calendar.monthrange(int(date[:4]), int(date[4:6]))
            end_date_list.append(date[:6] + str(month_range[1]))
    return start_date_list, end_date_list


# 清空特定文件夹历史导出数据
def clear_sp_path(target_path):
    walker = os.walk(target_path)
    for each in walker:
        for file in each[2]:
            chg_time = parse(time.ctime(os.path.getctime(each[0]+file)))
            if chg_time < parse(datetime.now().strftime('%Y%m%d')+' 00:00:00'):
                os.remove(each[0]+file)


if __name__ == '__main__':
    # a = get_format_code('002983.SZ','wind')
    # print(a)
    # gen_month_series('20200506','20201004')
    clear_sp_path(r'C:\Users\1\Desktop\ff'+'\\')
