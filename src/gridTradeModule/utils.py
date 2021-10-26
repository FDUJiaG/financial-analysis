from datetime import datetime


# 定义保证金比例, 手续费率, 平今仓手续费, 杠杆点数
MARGIN_RATE = 0.14
HANDLING_RATE = 0.24e-4
CLOSE_OUT_RATE = 15 * HANDLING_RATE
LEVERAGE = 300


def get_time(date=False, utc=False, msl=3):
    if date:
        time_fmt = "%Y-%m-%d %H:%M:%S.%f"
    else:
        time_fmt = "%H:%M:%S.%f"

    if utc:
        return datetime.utcnow().strftime(time_fmt)[:(msl - 6)]
    else:
        return datetime.now().strftime(time_fmt)[:(msl - 6)]


def print_new_info(status="I", color="Y"):
    if color == "R":
        return "\033[0;31;1m[{} {}]\033[0m".format(status, get_time())
    else:
        return "\033[0;33;1m[{} {}]\033[0m".format(status, get_time())
