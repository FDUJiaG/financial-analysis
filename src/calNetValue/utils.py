from datetime import datetime
import tushare as ts

player_dict = {
    "ty": "争七保八",
    "lxx": "superX",
    "hyj": "和光同尘",
    "hh": "守旧待时",
    "zcf": "轴心国",
    "hss": "小虾米",
    "zmj": "包工头",
    "dpf": "菜狗"
}

index_dict = {
    "hs300": ["沪深300", "399300.SZ"],
    "sse": ["上证指数", "000001.SH"],
}

figs_dict = {
    "ty": "https://i.loli.net/2021/05/25/4JjxO1eNzCVv9TR.jpg",
    "lxx": "https://i.loli.net/2021/05/25/MGxrJSu6eCWHPRB.jpg",
    "hyj": "https://i.loli.net/2021/05/25/u5RCtFTrqa8KBs1.jpg",
    "hh": "https://i.loli.net/2021/05/25/t8IC6L735Axkg2T.jpg",
    "zcf": "https://i.loli.net/2021/05/25/jT2zd8FSYOhKQR5.jpg",
    "hss": "https://i.loli.net/2021/05/25/itqK1juGeDfAJXp.jpg",
    "zmj": "https://i.loli.net/2021/05/25/F3PWGyL5cB4gr79.jpg",
    "dpf": "https://i.loli.net/2021/05/25/PVMqakRbUlIusTd.jpg",
    "hs300": "https://i.loli.net/2021/06/16/VGcy9QqHPWgBYuF.jpg",
    "sse": "https://i.loli.net/2021/06/16/3EMHx6BsdLSwbRG.jpg"
}

stock_dict = {
    "ty": [
        "603040", "002777", "603995", "000002", "600887"
        # 新坐标，久远银海，甬金股份，万科A，伊利股份
    ],
    "lxx":  [
        "002304", "000568", "600887", "688063", "300677"
        # 洋河股份，泸州老窖，伊利股份，派能科技，英科医疗
    ],
    "hyj": [
        "601318", "000581", "000049", "600009", "600438"
        # 中国平安，威孚高科，德赛电池，上海机场，通威股份
    ],
    "hh": [
        "600519", "000333", "600900", "601012", "600309"
        # 贵州茅台，美的集团，长江电力，隆基股份，万华化学
    ],
    "zcf": [
        "000333", "600887", "002555", "002607", "601128"
        # 美的集团，伊利股份，三七互娱，中公教育，常熟银行
    ],
    "hss": [
        "000002", "600176", "603506", "000915", "002434"
        # 万科A，中国巨石，南都物业，华特达因，万里扬
    ],
    "zmj": [
        "000786", "000333", "603506", "002043", "603369"
        # 北新建材，美的集团，南都物业，兔宝宝，今世缘
    ],
    "dpf":  [
        "605077", "002570", "600166", "605089", "002405"
        # 华康股份，贝因美，福田汽车，味知香，四维图新
    ]
}

# 段老师的 token
tushare_token = "ba73b3943bdd57c2ff05991f7556ef417f457ac453355972ff5d01ce"


def get_time(date=False, utc=False, msl=3):
    if date:
        time_fmt = "%Y-%m-%d %H:%M:%S.%f"
    else:
        time_fmt = "%H:%M:%S.%f"

    if utc:
        return datetime.utcnow().strftime(time_fmt)[:(msl - 6)]
    else:
        return datetime.now().strftime(time_fmt)[:(msl - 6)]


def print_info(status="I"):
    return "\033[0;33;1m[{} {}]\033[0m".format(status, get_time())


def get_api(token):
    # 设置 tushare pro 的 token 并获取连接，仅首次和重置时需获取，对于日 K 每分钟最多调取两百次
    ts.set_token(token)
    pro = ts.pro_api()
    return pro