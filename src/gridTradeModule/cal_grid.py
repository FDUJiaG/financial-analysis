import os
from utils import print_new_info, MARGIN_RATE, HANDLING_RATE, LEVERAGE
import pandas as pd
from datetime import datetime
from loopTest import cal_grid_pl


def cal_grid(d_path, o_path, b1, s1, f_type="csv"):
    df = pd.read_csv(d_path, header=0)
    df.columns = ["date", "time", "code", "close", "settlement"]
    print(print_new_info(), end=" ")
    print("Get row data: \n{}".format(df.head()))
    df = df[["date", "code"]]
    df.drop_duplicates(inplace=True)
    code_dict = dict(zip(df["date"].tolist(), df["code"].tolist()))

    f_list = os.listdir(o_path)
    cal_columns = [
        "date", "code", "close",
        "l_deal", "s_deal",
        "l_total", "s_total",
        "handling_fee", "net_grid_pl"
    ]
    df_cal = pd.DataFrame(columns=cal_columns)

    cal_dict = {
        cal_columns[0]: "2021/3/7",
        cal_columns[1]: "IF2103",
        cal_columns[2]: 5255.4,
        cal_columns[3]: 0,
        cal_columns[4]: 0,
        cal_columns[5]: 0,
        cal_columns[6]: 0,
        cal_columns[7]: 0,
        cal_columns[8]: 0
    }
    df_cal = df_cal.append(cal_dict, ignore_index=True)
    for f_item in f_list:
        if f_item.split(".")[-1] == f_type and "result" in f_item:
            df_item = pd.read_csv(os.path.join(o_path, f_item), header=0)
            tail_idx = len(df_item) - 1
            df_item = df_item.tail(1)
            cal_dict[cal_columns[0]] = df_item[cal_columns[0]][tail_idx]
            cal_dict[cal_columns[1]] = code_dict[cal_dict[cal_columns[0]]]
            for idx in range(2, len(cal_columns) - 1):
                cal_dict[cal_columns[idx]] = df_item[cal_columns[idx]][tail_idx]
            cal_dict[cal_columns[-1]] = cal_grid_pl(
                b1, s1,
                cal_dict[cal_columns[3]],
                cal_dict[cal_columns[4]],
                cal_dict[cal_columns[5]],
                cal_dict[cal_columns[6]],
            ) * LEVERAGE - cal_dict[cal_columns[7]]
            df_cal = df_cal.append(cal_dict, ignore_index=True)

    df_cal.to_csv("grid_pl_daily.csv", index=False, encoding="utf_8_sig")

    return True


if __name__ == '__main__':
    buy1, sell1 = 5247, 5257
    root_path = os.path.abspath(".")
    data_path = os.path.join(root_path, "data", "data_iftick.csv")
    result_path = os.path.join(root_path, "output_all")
    judge = cal_grid(data_path, result_path, buy1, sell1)
