import os
from utils import print_new_info, MARGIN_RATE, HANDLING_RATE, LEVERAGE
import pandas as pd


# 设定初始资金
AF = 1e8


def loop_test(d_path):
    df = pd.read_excel(d_path, header=None)
    df.columns = ["date", "time", "close", "settlement"]
    print(df.head())
    p0 = 5255.4
    b1, s1 = 5252, 5262
    now_position = 50
    now_handling_fee = 0
    now_margin = now_position * p0 * LEVERAGE * MARGIN_RATE
    # now_available_funds
    columns_list = [
        "self_buy1",
        "self_sell1",
        "position",
        "handling_fee",
        "margin",
        "available_funds",
        "profit_and_loss"
    ]
    df_output = pd.DataFrame(columns=columns_list)
    for idx, p_item in zip(df.index, df["price"].to_list()):
        b1, s1, now_position, now_handling_fee, now_margin, now_available_funds, p_l = judge_price(
            p_item,
            b1,
            s1,
            now_position,
            now_handling_fee,
            now_margin
        )
        judge_list = [b1, s1, now_position, now_handling_fee, now_margin, now_available_funds, p_l]
        dict_append = dict(zip(columns_list, judge_list))
        df_output = df_output.append(dict_append, ignore_index=True)

    df_output.to_excel("output.xlsx", index=None)

    return 1


def judge_price(n_price, b1, s1, n_position, n_handling_fee, n_margin):
    # 输入现价, 账户挂单的买1 和 卖1, 现在的持仓, 总手续费, 总保证金
    p_l = n_price * n_position * LEVERAGE - n_margin / MARGIN_RATE
    n_available_funds = AF - n_price * n_position * LEVERAGE * MARGIN_RATE + p_l - n_handling_fee
    while n_price > s1 and n_available_funds > 0:
        n_position -= 1
        s1 += 5
        b1 += 5
        n_handling_fee += s1 * LEVERAGE * HANDLING_RATE
        # n_margin = n_position * n_price * LEVERAGE * MARGIN_RATE
        n_margin -= s1 * LEVERAGE * MARGIN_RATE
        p_l = n_price * n_position * LEVERAGE - n_margin / MARGIN_RATE      # 总盈亏
        # 原始资金 - 目前保证金占用 + 总盈亏 - 手续费
        n_available_funds = AF - n_price * n_position * LEVERAGE * MARGIN_RATE + p_l - n_handling_fee
    while n_price < b1 and n_available_funds > 0:
        n_position += 1
        b1 -= 5
        s1 -= 5
        if b1 <= 0:
            print(print_new_info("E", "R"), end=" ")
            print("Buy Price {} Error!!!".format(b1))
            return False
        n_handling_fee += b1 * LEVERAGE * HANDLING_RATE
        n_margin += b1 * LEVERAGE * MARGIN_RATE
        p_l = n_price * n_position * LEVERAGE - n_margin / MARGIN_RATE      # 总盈亏
        # 原始资金 - 目前保证金占用 + 总盈亏 - 手续费
        n_available_funds = AF - n_price * n_position * LEVERAGE * MARGIN_RATE + p_l - n_handling_fee

    return b1, s1, n_position, n_handling_fee, n_margin, n_available_funds, p_l


if __name__ == '__main__':
    data_dir = os.path.join(os.path.abspath("."), "data")
    data_name = "price.xlsx"
    data_path = os.path.join(data_dir, data_name)
    loop_test(data_path)
