import time
import pandas as pd
import tushare as ts
from src.calNetValue.utils import print_info, get_api, tushare_token, player_dict, stock_dict, figs_dict, index_dict
import pyecharts.options as opts
from pyecharts.charts import Line


def all_net_value(player_pool, start_date, end_date, adj="qfq"):
    # 计算所有参与者的净值数据
    # 输入参与者名称字典
    # 输出参与者净值数据总表
    dict_all = dict()
    col_list = list()
    col_list.append("trade_date")
    df_all = pd.DataFrame(columns=col_list)
    for player_item, product_item in player_pool.items():
        print(print_info(), end=" ")
        print("Deal with {} ...".format(product_item))
        # 计算每个参与者的净值情况
        dict_all[player_item] = cal_net_value(stock_dict[player_item], start_date, end_date, adj)
        df_all = pd.merge(df_all, dict_all[player_item][["trade_date", "net_value"]], how="outer", on="trade_date")
        col_list.append(product_item)

    df_all.columns = col_list
    # 日期化时间
    df_all["trade_date"] = pd.to_datetime(df_all["trade_date"])
    df_all["trade_date"] = df_all["trade_date"].apply(lambda x: x.strftime('%Y-%m-%d'))
    print("\n", print_info(), end=" ")
    print("Get all players' net value data:\n {}".format(df_all))
    # 计算指数的净值情况
    df_index = cal_index_net_value(index_pool=index_dict, start_date=START_DATE, end_date=END_DATE)
    df_index["trade_date"] = pd.to_datetime(df_all["trade_date"])
    df_index["trade_date"] = df_index["trade_date"].apply(lambda x: x.strftime('%Y-%m-%d'))
    df_all = pd.merge(df_all, df_index, how="outer", on="trade_date")
    print("\n", print_info(), end=" ")
    print("Get all players' net value data:\n {}".format(df_all))

    return df_all


def cal_net_value(stock_pool, start_date, end_date, adj="qfq"):
    # 计算组合的净值数据
    # 输入股票代码列表，起止日期
    # 输出考察区间内的净值表格
    col_list = list()
    col_list.append("trade_date")
    df_net = pd.DataFrame(columns=col_list)

    for stock_item in stock_pool:
        s_code = six_code_to_ts_code(stock_item)
        df_item = ts.pro_bar(ts_code=s_code, adj=adj, start_date=start_date, end_date=end_date)
        df_item["close"] = round(df_item["close"] / df_item["close"].tolist()[-1] * 0.2, 6)
        df_net = pd.merge(df_net, df_item[["trade_date", "close"]], how="outer", on="trade_date")
        col_list.append(s_code.split(".")[0])

    # 根据日期排序
    df_net.sort_values(by="trade_date", inplace=True)
    # 根据前值替换NaN值
    df_net.fillna(method='ffill', inplace=True)
    df_net.reset_index(inplace=True, drop=True)
    df_net.columns = col_list
    temp = df_net[col_list[1:]]
    df_net["net_value"] = temp.sum(axis=1)
    print(print_info(), end=" ")
    print("The dataframe tail is:\n {}".format(df_net.tail()))

    return df_net


def cal_index_net_value(index_pool, start_date, end_date):
    # 计算指数的净值数据
    # 输入指数列表，起止日期
    # 输出考察区间内的净值表格
    col_list = list()
    col_list.append("trade_date")
    df_net = pd.DataFrame(columns=col_list)

    for index_item in index_pool.values():
        s_code = index_item[1]
        df_item = pro.index_daily(ts_code=s_code, start_date=start_date, end_date=end_date)
        df_item["close"] = round(df_item["close"] / df_item["close"].tolist()[-1], 6)
        df_net = pd.merge(df_net, df_item[["trade_date", "close"]], how="outer", on="trade_date")
        col_list.append(index_item[0])

    # 根据日期排序
    df_net.sort_values(by="trade_date", inplace=True)
    # 根据前值替换NaN值
    df_net.fillna(method='ffill', inplace=True)
    df_net.reset_index(inplace=True, drop=True)
    df_net.columns = col_list
    print(print_info(), end=" ")
    print("The index net dataframe tail is:\n {}".format(df_net.tail()))

    return df_net


def df_to_flourish(df):
    # 将数据转换成 flourish 的格式
    flourish_col = ["Label", "Categories", "Image"]
    df.rename(columns={"trade_date": flourish_col[0]}, inplace=True)
    df_col = df.columns
    print(print_info(), end=" ")
    print("The flourish dataframe tail is:\n {}".format(df.tail()))
    # print(df_col)
    top_row_dict = dict()
    top_row_dict[flourish_col[0]] = flourish_col[1:]
    for col_item, figs_item in zip(df_col[1:], list(figs_dict.values())):
        top_row_dict[col_item] = [col_item, figs_item]
    top_row = pd.DataFrame(top_row_dict)
    df = pd.concat([top_row, df]).reset_index(drop=True)
    df_trans = pd.DataFrame(df.values.T, index=df.columns, columns=df.index)
    return df_trans


def six_code_to_ts_code(code):
    # 将股票代码转换成标准格式
    code = str(code)
    code = code.split(".")[0]

    if len(code) == 6 and code.isdigit():
        if code[0] == "6":
            exc_label = "SH"
        elif code[0] in ["0", "3"]:
            exc_label = "SZ"
        else:
            print(print_info("W"), end=" ")
            print("Can not get the Exchange Info from the code: {}".format(code))
            return False
        return ".".join([code, exc_label])
    else:
        print(print_info("E"), end=" ")
        print("The stock code: {} is Error! Please check again!".format(code))
        return False


if __name__ == '__main__':
    pro = get_api(tushare_token)
    START_DATE = "20210531"
    TODAY = time.strftime("%Y%m%d", time.localtime())
    END_DATE = TODAY
    all_df = all_net_value(player_dict, START_DATE, END_DATE)
    df_flourish = df_to_flourish(all_df)
    df_flourish.to_excel("flourish_data.xlsx", header=None)

    # net_line = Line(init_opts=opts.InitOpts(width="1680px", height="800px"))
    # net_line.add_xaxis(xaxis_data=all_df["trade_date"])
    # for item in player_dict.values():
    #     net_line.add_yaxis(
    #         series_name=item,
    #         y_axis=round(all_df[item], 4),
    #         label_opts=opts.LabelOpts(
    #             is_show=False,
    #             position="end",
    #         ),
    #         is_smooth=True,
    #         # is_symbol_show=False,
    #     )
    # net_line.set_global_opts(
    #     title_opts=opts.TitleOpts(title="首陀罗争霸赛", subtitle="测试数据"),
    #     tooltip_opts=opts.TooltipOpts(
    #         trigger="axis",
    #     ),
    #     toolbox_opts=opts.ToolboxOpts(is_show=True),
    #     xaxis_opts=opts.AxisOpts(type_="category"),
    #     yaxis_opts=opts.AxisOpts(
    #         type_="value",
    #         name_location="start",
    #         min_=800,
    #         is_scale=True,
    #         axistick_opts=opts.AxisTickOpts(is_inside=False),
    #     ),
    # )
    # net_line.render("首陀罗争霸赛.html")
