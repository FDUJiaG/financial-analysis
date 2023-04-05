import os
from utils import print_new_info, MARGIN_RATE, HANDLING_RATE, LEVERAGE
import pandas as pd
from datetime import datetime


# 设定初始资金
AF = 1e8


def loop_test(d_path):
    df = pd.read_csv(d_path, header=0)
    df.columns = ["date", "time", "close", "settlement"]
    # df.columns = ["date", "time", "code", "close", "settlement"]
    print(print_new_info(), end=" ")
    print("Get row data: \n{}".format(df.head()))
    p0, js0 = 5255.4, 5269.2
    b1, s1 = 5247, 5257
    # 持仓数量
    yl_pos, ys_pos = 50, 0
    tl_pos, ts_pos = 0, 0
    # 网格成交数量
    l_deal, s_deal = 0, 0
    # 网格成交价格
    l_total, s_total = 0, 0
    # 净多头持仓和手续费
    net_long = yl_pos + tl_pos - ys_pos - ts_pos
    handling_fee = p0 * LEVERAGE * net_long * HANDLING_RATE
    # 今仓，昨仓，多空分别记录保证金
    yl_margin = cal_margin(yl_pos, js0)
    tl_margin = cal_margin(tl_pos, p0)
    ys_margin = cal_margin(ys_pos, js0)
    ts_margin = cal_margin(ts_pos, p0)
    long_margin = yl_margin + tl_margin
    short_margin = ys_margin + ts_margin
    now_margin = max(long_margin, short_margin)
    # pos_margin = cal_margin(net_long, p0)
    close_pl = 0
    pos_pl = 0
    static = AF
    dynamic = static + close_pl + pos_pl - handling_fee
    af = dynamic - now_margin

    # 构筑一个启动字典包括
    # 日期和时间, 价格
    # 昨多仓, 昨空仓, 今多仓, 今空仓, 净多持仓
    # 多空单占用保证金, 总保证金
    # 平仓盈亏, 持仓盈亏
    # 手续费, 可用资金, 静态权益, 动态权益
    # 买单成交量, 卖单成交量, 相应点数
    columns_dict = {
        "date": "base date",
        "time": "base time",
        "close": p0,
        "yes_js": js0,
        "self_b1": b1,
        "self_s1": s1,
        "yl_pos": yl_pos,
        "tl_pos": tl_pos,
        "ys_pos": ys_pos,
        "ts_pos": ts_pos,
        "net_long": net_long,
        "yl_margin": yl_margin,
        "tl_margin": tl_margin,
        "ys_margin": ys_margin,
        "ts_margin": ts_margin,
        "margin": now_margin,
        "close_pl": close_pl,
        "pos_pl": pos_pl,
        "handling_fee": handling_fee,
        "available": af,
        "static": static,
        "dynamic": dynamic,
        "l_deal": l_deal,
        "s_deal": s_deal,
        "l_total": l_total,
        "s_total": s_total
    }
    columns_keys = list(columns_dict.keys())

    del_list = ["date", "time", "net_long", "margin"]
    para_dict = get_para(columns_dict, del_list)

    # 定义输出数据框
    df_output = pd.DataFrame(columns=columns_keys)
    df_output = df_output.append(columns_dict, ignore_index=True)
    for idx in df.index:
        # 用于区分是否无需考虑跳空
        op_flag = True
        # 逐行处理数据
        item = df.iloc[idx].tolist()
        columns_dict["time"] = item[1]      # 每条记录的时间
        columns_dict["close"], columns_dict["yes_js"] = item[-2], item[-1]      # 每条记录的收盘价，结算价
        # 如果日期不一样, 需要将该日的开仓对应到昨日的开仓
        if item[0] != columns_dict["date"]:
            columns_dict["date"] = item[0]
            print(print_new_info(), end=" ")
            print("Operating the Date: {}".format(columns_dict["date"]))
            # 更新多头持仓
            columns_dict["yl_pos"] += columns_dict["tl_pos"]
            columns_dict["tl_pos"] = 0
            # 更新多头保证金
            columns_dict["yl_margin"] = cal_margin(columns_dict["yl_pos"], columns_dict["yes_js"])
            columns_dict["tl_margin"] = 0
            # 更新空头持仓
            columns_dict["ys_pos"] += columns_dict["ts_pos"]
            columns_dict["ts_pos"] = 0
            # 更新空头保证金
            columns_dict["ys_margin"] = cal_margin(columns_dict["ys_pos"], columns_dict["yes_js"])
            columns_dict["ts_margin"] = 0
            columns_dict["margin"] = max(columns_dict["yl_margin"], columns_dict["ys_margin"])

            # 平仓盈亏重置
            columns_dict["static"] += columns_dict["close_pl"] + columns_dict["pos_pl"]
            columns_dict["close_pl"], columns_dict["pos_pl"] = 0, 0
            # 更新可用资金
            columns_dict["dynamic"] = columns_dict["static"] - columns_dict["close_pl"] - columns_dict["pos_pl"]
            columns_dict["available"] = columns_dict["dynamic"] - columns_dict["margin"]
            op_flag = False

        # 迭代输入数据，作为下一个输入
        para_dict = get_para(columns_dict, del_list)
        # 传参列表
        para_list = list(para_dict.values())
        para_list.append(op_flag)
        item_list = judge_price(*para_list)
        judge_list = [
            columns_dict["date"], columns_dict["time"]
        ]
        judge_list += item_list

        columns_dict = dict(zip(columns_keys, judge_list))
        df_output = df_output.append(columns_dict, ignore_index=True)

        if columns_dict["time"] == "15:00:00":
            # 每天结束存一个表格
            df_output.to_csv(
                "output/result_{}.csv".format(
                    datetime.strptime(item[0], "%Y/%m/%d").strftime("%Y%m%d")
                ),
                index=False,
                encoding="utf_8_sig"
            )
            df_output = df_output.tail(1)

    grid_pl = cal_grid_pl(
        b1, s1,
        columns_dict["l_deal"], columns_dict["s_deal"],
        columns_dict["l_total"], columns_dict["s_total"]
    )

    print(print_new_info(), end=" ")
    print("The Grid point is: {:.2f}, the Profit of Grid is: {:.2f} the Net Profit of Grid is {:.2f}".format(
        grid_pl, grid_pl * LEVERAGE, grid_pl * LEVERAGE - columns_dict["handling_fee"]
    ))

    df_output.to_excel("output.xlsx", index=None)
    print(print_new_info(), end=" ")
    print("Analyse result saved!")

    return True


def judge_price(
        n_price, n_js, b1, s1,
        n_yl_pos, n_tl_pos,                 # 多单持仓
        n_ys_pos, n_ts_pos,                 # 空单持仓
        n_yl_margin, n_tl_margin,           # 多单占用保证金
        n_ys_margin, n_ts_margin,           # 空单占用保证金
        n_close_pl, n_pos_pl,               # 盈亏情况
        n_handling_fee,                     # 手续费
        n_af, n_static, n_dynamic,          # 可用资金, 静态权益, 动态权益
        n_l_deal, n_s_deal,                 # 成交手数
        n_l_total, n_s_total,               # 成交金额
        n_flag
):
    # if n_price > s1:
    #     adj = -5
    # elif n_price < b1:
    #     adj = 5

    if b1 < n_price < s1:
        # 如果仅价格变动，但是没有实际成交
        # 浮盈计算
        yl_pl = n_price * n_yl_pos * LEVERAGE - n_yl_margin / MARGIN_RATE
        tl_pl = n_price * n_tl_pos * LEVERAGE - n_tl_margin / MARGIN_RATE
        long_pl = yl_pl + tl_pl
        ys_pl = - n_price * n_ys_pos * LEVERAGE + n_ys_margin / MARGIN_RATE
        ts_pl = - n_price * n_ts_pos * LEVERAGE + n_ts_margin / MARGIN_RATE
        short_pl = ys_pl + ts_pl
        n_pos_pl = long_pl + short_pl

        # 保证金计算
        long_margin = n_yl_margin + n_tl_margin
        short_margin = n_ys_margin + n_ts_margin
        now_margin = max(long_margin, short_margin)

        # 权益和可用资金计算
        n_dynamic = n_static + n_pos_pl + n_close_pl - n_handling_fee
        n_af = n_dynamic - now_margin

    while n_price >= s1:
        # 当价格上涨时
        # 可用资金非负时才操作
        if n_af <= 0:
            print(print_new_info("W", "R"), end=" ")
            print("No Available Funds!")
            break
        # 净多头为正时才操作
        elif net_long_pos(n_yl_pos, n_tl_pos, n_ys_pos, n_ts_pos) <= 0:
            print(print_new_info("W", "R"), end=" ")
            print("No Net Long Position to Trade!")
            break
        # 优先卖平昨日的多头持仓, 在卖开新仓
        elif n_yl_pos > 0:
            n_yl_pos -= 1
            n_yl_margin -= cal_margin(1, n_js)              # 平多单, 按结算价减保证金占用
            # 区分跳空的价格
            if n_flag:
                n_close_pl += (s1 - n_js) * LEVERAGE        # 平昨多的平仓盈亏
            else:
                n_close_pl += (n_price - n_js) * LEVERAGE   # 平昨多的平仓盈亏
        else:
            n_ts_pos += 1
            # 区分跳空的价格
            if n_flag:
                n_ts_margin += cal_margin(1, s1)
            else:
                n_ts_margin += cal_margin(1, n_price)

        # 网格获利需要数据
        n_s_deal += 1
        # 区分跳空的价格
        if n_flag:
            n_s_total += s1
            # 手续费计算
            n_handling_fee += s1 * LEVERAGE * HANDLING_RATE
        else:
            n_s_total += n_price
            # 手续费计算
            n_handling_fee += n_price * LEVERAGE * HANDLING_RATE

        # 浮盈计算
        yl_pl = n_price * n_yl_pos * LEVERAGE - n_yl_margin / MARGIN_RATE
        tl_pl = n_price * n_tl_pos * LEVERAGE - n_tl_margin / MARGIN_RATE
        long_pl = yl_pl + tl_pl
        ys_pl = - n_price * n_ys_pos * LEVERAGE + n_ys_margin / MARGIN_RATE
        ts_pl = - n_price * n_ts_pos * LEVERAGE + n_ts_margin / MARGIN_RATE
        short_pl = ys_pl + ts_pl
        n_pos_pl = long_pl + short_pl

        # 保证金计算
        long_margin = n_yl_margin + n_tl_margin
        short_margin = n_ys_margin + n_ts_margin
        now_margin = max(long_margin, short_margin)

        # 权益和可用资金计算
        n_dynamic = n_static + n_pos_pl + n_close_pl - n_handling_fee
        n_af = n_dynamic - now_margin

        # 价格迭代
        s1 += 5
        b1 += 5

    # 开1手的资金
    single_margin = cal_margin(1, n_price)
    while n_price <= b1 and n_af > single_margin:
        # 当价格下跌
        # 对价格判断，不产生极端价格
        if b1 <= 0:
            print(print_new_info("E", "R"), end=" ")
            print("Buy Price {} Error!!!".format(b1))
            return False
        # 可用资金至少可以再开一手才操作
        elif n_af <= single_margin:
            print(print_new_info("W", "R"), end=" ")
            print("Available Funds: {}, can not buy anymore!".format(n_af))
            break
        # 优先买平以往空头持仓, 再新开多头
        elif n_ys_pos > 0:
            n_ys_pos -= 1
            n_ys_margin -= cal_margin(1, n_js)          # 平多单, 按结算价减保证金占用
            if n_flag:
                n_close_pl += (n_js - b1) * LEVERAGE    # 平昨多的平仓盈亏
            else:
                n_close_pl += (n_js - n_price) * LEVERAGE
        else:
            n_tl_pos += 1
            if n_flag:
                n_tl_margin += cal_margin(1, b1)
            else:
                n_tl_margin += cal_margin(1, n_price)

        # 网格获利需要数据
        n_l_deal += 1
        # 区分跳空的价格
        if n_flag:
            n_l_total += b1
            # 手续费计算
            n_handling_fee += b1 * LEVERAGE * HANDLING_RATE
        else:
            n_l_total += n_price
            # 手续费计算
            n_handling_fee += n_price * LEVERAGE * HANDLING_RATE

        # 浮盈计算
        yl_pl = n_price * n_yl_pos * LEVERAGE - n_yl_margin / MARGIN_RATE
        tl_pl = n_price * n_tl_pos * LEVERAGE - n_tl_margin / MARGIN_RATE
        long_pl = yl_pl + tl_pl
        ys_pl = - n_price * n_ys_pos * LEVERAGE + n_ys_margin / MARGIN_RATE
        ts_pl = - n_price * n_ts_pos * LEVERAGE + n_ts_margin / MARGIN_RATE
        short_pl = ys_pl + ts_pl
        n_pos_pl = long_pl + short_pl

        # 保证金计算
        long_margin = n_yl_margin + n_tl_margin
        short_margin = n_ys_margin + n_ts_margin
        now_margin = max(long_margin, short_margin)

        # 权益和可用资金计算
        n_dynamic = n_static + n_pos_pl + n_close_pl - n_handling_fee
        n_af = n_dynamic - now_margin

        # 价格迭代
        b1 -= 5
        s1 -= 5

    item_list = [
        n_price, n_js, b1, s1,
        n_yl_pos, n_tl_pos,         # 多单持仓
        n_ys_pos, n_ts_pos,         # 空单持仓
        net_long_pos(n_yl_pos, n_tl_pos, n_ys_pos, n_ts_pos),           # 净多持仓
        n_yl_margin, n_tl_margin,   # 多单占用保证金
        n_ys_margin, n_ts_margin,   # 空单占用保证金
        max(n_yl_margin + n_tl_margin, n_ys_margin + n_ts_margin),      # 总保证金
        n_close_pl, n_pos_pl,       # 平仓盈亏, 持仓盈亏
        n_handling_fee,             # 手续费
        n_af, n_static, n_dynamic,  # 可用资金, 静态权益, 动态权益
        n_l_deal, n_s_deal,         # 成交手数
        n_l_total, n_s_total        # 成交点数
    ]

    return item_list


def net_long_pos(n_yl_pos, n_tl_pos, n_ys_pos, n_ts_pos):
    # 计算净多头持仓
    return n_yl_pos + n_tl_pos - n_ys_pos - n_ts_pos


def cal_margin(num, ave_p):
    # 计算持仓保证金
    return num * ave_p * LEVERAGE * MARGIN_RATE


def get_para(b_dict, del_lst):
    c_dict = b_dict.copy()
    for d_item in del_lst:
        if d_item in c_dict.keys():
            del c_dict[d_item]
    return c_dict


def cal_grid_pl(buy1, sell1, l_d, s_d, l_t, s_t):
    if l_d < s_d:
        adj_p = sell1 + 5 * (abs(l_d - s_d) - 1) / 2
    else:
        adj_p = buy1 - 5 * (abs(l_d - s_d) - 1) / 2
    grid_pl = s_t - l_t + adj_p * (l_d - s_d)
    return grid_pl


if __name__ == '__main__':
    data_dir = os.path.join(os.path.abspath("."), "data")
    data_name = "data_test.csv"
    data_path = os.path.join(data_dir, data_name)
    loop_test(data_path)
