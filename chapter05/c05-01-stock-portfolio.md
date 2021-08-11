# Stock Portfolio

在现代金融学中，投资组合理论占据极其重要的地位，该理论的开山鼻祖是 Harry Markowitz，并于 20 世纪 50 年代最早提出，时至今日，在涉及投资组合的研究与实践中依然广泛运用该理论

## Key Variables of the Portfolio

假设存在一个投资组合，它由 N 只股票构成，描述一个投资组合需要用到包括投资组合的预期收益率以及投资组合收益率的波动率这两个重要变量

### Expected Rate of Return on the Portfolio

投资组合的预期收益率，可以由以下公式得出

$$
\begin{aligned}
E(R_P) &= E(\sum_{i=1}^N \omega_i R_i) = \sum_{i=1}^N \omega_i E(R_i) \\
&=[\omega_1,\omega_2,\cdots,\omega_N][E(R_1),E(R_2),\cdots,E(R_N)]^T
\end{aligned} \tag{5-1}
$$

其中，

$$
\begin{aligned}
&E(R_P) : 投资组合的预期收益率 \\
&\omega_i : 投资组合中第\ i\ 只股票所占的权重，通常是运用股票的市值占投资组合整体市值的比例，且\ \sum_{i=1}^N \omega_i=1 \\
& E(R_i) : 投资组合中第\ i\ 只股票的预期收益率，通常是运用该股票过去收益率的均值代替 \\
& [\omega_1,\omega_2,\cdots,\omega_N] : 每只股票权重的向量（行向量）\\
& [E(R_1),E(R_2),\cdots,E(R_N)]^T : 每只股票预期收益率的向量（列向量） 
\end{aligned}
$$

在计算股票收益率的时候，针对第\ i\ 只股票在第\ t\ 个交易日的收益率用如下式子表示，就可以将收益率变为连续复利的收益率

$$
R_tt = \ln \frac{P_{it}}{P_{it-1}} \tag{5-2}
$$

其中，

$$
\begin{aligned}
&P_{it}: 表示第\ i\ 只股票在\ t\ 时刻的价格 \\
&P_{it-1}: 表示第\ i\ 只股票在\ t-1\ 时刻的价格
\end{aligned}
$$

此外，在 Python 中，可以生成投资组合中每只股票的随机权重

```python
import numpy as np

x = np.random.random(5)         # 从均匀分布中随机抽取5个从0到1的随机数
weights = x/np.sum(x)           # 生成一个权重数组
print(weights)
print(round(sum(weights), 2))   # 验证生成的权重随机数是否合计等于1
```

输出

```console
[0.10220201 0.27353176 0.1263887  0.32700943 0.1708681 ]
1.0
```

### Portfolio Volatility (Risk)

在计算投资组合的波动率之前，需要首先计算得到每只股票收益率之间的协方差和相关系数

首先，考虑由两只股票组成的投资组合收益率的波动率（下文简称 **收益波动率** 或 **波动率**），具体的表达式如下

$$
\begin{aligned}
\sigma_P^2 &= \omega_1^2 + \omega_2^2 + 2\omega_1\omega_2Cov(R_1,R_2) \\
&= \omega_1^2 + \omega_2^2 + 2\omega_1\omega_2 \rho_{12}\sigma_1\sigma_2 
\end{aligned} \tag{5-3}
$$

等式 5-3 两边开根号就得到

$$
\begin{aligned}
\sigma_P^2 &= \sqrt{\omega_1^2 + \omega_2^2 + 2\omega_1\omega_2 Cov(R_1,R_2)} \\
&= \sqrt{\omega_1^2 + \omega_2^2 + 2\omega_1\omega_2 \rho_{12}\sigma_1\sigma_2} 
\end{aligned} \tag{5-4}
$$

其中，

$$
\begin{aligned}
&\sigma_P: 投资组合的收益波动率，也表示投资组合的风险 \\
&\sigma_1,\sigma_2: 第\ 1,2\ 只股票的收益波动率 \\
&Cov(R_1,R_2): 表示第\ 1,2\ 只股票收益率之间的协方差 \\
&\rho_{12}: 表示第\ 1,2\ 只股票收益率之间的相关系数
\end{aligned}
$$

从以上的公式不难发现，一个投资组合的波动率会受到组合中股票收益的相关系数影响

$$
\sigma_P = \left \{
\begin{aligned}
&\omega_1\sigma_1 + \omega_2\sigma_2,\quad &\rho_{12}=1 \\
&\vert\omega_1\sigma_1 - \omega_2\sigma_2\vert,\quad &\rho_{12}=-1 
\end{aligned}
\right. \tag{5-5}
$$

- 当完全线性正相关时，投资组合的收益波动率就是两只股票收益波动率的加权平均值
- 当完全线性负相关时，投资组合的收益波动率就是两只股票加权波动率之差的绝对值

接着，考虑由 N 只股票组成的投资组合的收益波动率，具体的表达式如下

$$
\begin{aligned}
\sigma_P^2 &= \sum_{i=1}^N\sum_{j=1}^N\omega_i \omega_j Cov(R_i, R_j) \\
&=\sum_{i=1}^N\sum_{j=1}^N\omega_i \omega_j\rho_{ij}\sigma_i\sigma_j
\end{aligned} \tag{5-6}
$$

两边开根号就可以得到

$$
\begin{aligned}
\sigma_P &= \sqrt{\sum_{i=1}^N\sum_{j=1}^N\omega_i \omega_j Cov(R_i, R_j)} \\
&=\sqrt{\sum_{i=1}^N\sum_{j=1}^N\omega_i \omega_j\rho_{ij}\sigma_i\sigma_j}
\end{aligned} \tag{5-7}
$$

其中，

$$
\begin{aligned}
&\sigma_i: 第\ i\ 只股票的收益波动率 \\
&Cov(R_i,R_j): 表示第\ i,j\ 只股票收益率之间的协方差 \\
&\rho_{ij}: 表示第\ i,j\ 只股票收益率之间的相关系数
\end{aligned}
$$

并且，

$$
\rho_{ij}=\frac{Cov(R_i,R_j)}{\sigma_i,\sigma_j} \tag{5-8}
$$

注意，

$$
\begin{aligned}
&当 i=j 时,\;Cov(R_i,R_j)=\sigma_i^2=\sigma_j^2,\; \rho_{ij}=1 \\
&当 i\neq j 时,\;Cov(R_i,R_j)=Cov(R_j,R_i),\; \rho_{ij}=\rho_{ji}
\end{aligned}
$$

由于涉及大量的计算，可以运用矩阵进行比较方便的计算，设如下符号

$$
\boldsymbol{\omega} = [\omega_1,\omega_2,\cdots,\omega_N],\quad
\boldsymbol{\Sigma}=\begin{bmatrix}
\sigma_1^2 & \sigma_{12} & \cdots & \sigma_{1N} \\
\sigma_{21} & \sigma_2^2 & \cdots & \sigma_{2N} \\
\vdots & \vdots & \ddots & \vdots \\
\sigma_{N1} & \sigma_{N2} & \cdots & \sigma_N^2 \\
\end{bmatrix},\quad
\sigma_{ij}=Cov(R_i,R_j)
$$

因此，投资组合收益波动率的表达式可以写成

$$
\sigma_P=\sqrt{\boldsymbol{\omega\Sigma\omega}^T} \tag{5-9}
$$

此外，波动率大致遵循平方根法则，并且按照交易日的天数计算，具体如下

$$
\begin{aligned}
周波动率 &= \sqrt{5} \times 日波动率 \\
月波动率 &= \sqrt{22} \times 日波动率 \\
年波动率 &= \sqrt{252} \times 日波动率 \\
\end{aligned}
$$

### Cases

下面通过基于A股市场的一个案例演示如何计算一个投资组合的收益率和波动率

【eg 8-1】假定投资组合配置了5只A股股票，数据是2019年至2021年期间的每个交易日收盘价格

|股票代码|600009|600036|600519|000002|002594|
|:---:|:---:|:---:|:---:|:---:|:---:|
|证券简称|上海机场|招商银行|贵州茅台|万科A|比亚迪|

#### Step 1

导入股票的收盘价格数据并且进行可视化

使用 Tushare [通用行情接口](https://tushare.pro/document/2?doc_id=109) 请求数据

```python
import tushare as ts
import pandas as pd

TOKEN="SET_YOUR_TOKEN"
ts.set_token(TOKEN)

# 设置股票列表
code_dict = {
    "600009.SH": "上海机场",
    "600036.SH": "招商银行",
    "600519.SH": "贵州茅台",
    "000002.SZ": "万科A",
    "002594.SZ": "比亚迪"
}
code_str = ",".join(code_dict.keys())

data = pd.DataFrame(columns=["trade_date"])
col_list = ["日期"]
start_date = "20190101"
end_date = "20201231"

for code_item in code_dict.keys():
    df_item = ts.pro_bar(
        ts_code=code_item,  # 股票标准代码
        asset="E",          # 资产类别：E股票
        adj="qfq",          # 复权类型
        start_date=start_date,
        end_date=end_date
    )
    # 根据日期合并每只标的的收盘信息
    data = pd.merge(data, df_item[["trade_date", "close"]], how="outer", on="trade_date")
    col_list.append(code_dict[code_item])

data.columns = col_list     # 重置列名 
data.sort_values(by=col_list[0], inplace=True)  # 按照日期升序排列
data.fillna(method='ffill', inplace=True)       # 根据前值替换NaN值
data.set_index(col_list[0], inplace=True, drop=True)    # 重新设置索引

print(data.head())  # 查看前5行数据
```

输出

```console
             上海机场     招商银行      贵州茅台      万科A      比亚迪
日期
20190102  49.4780  23.2058  583.4473  22.1556  48.9292
20190103  48.8102  23.4986  574.7002  22.3132  47.8246
20190104  48.9280  24.0936  586.3890  23.1104  50.4020
20190107  48.8888  24.1031  589.7885  23.2216  51.1383
20190108  48.9477  23.8197  589.1066  23.1753  52.6210
```

将股价按首个交易日进行归一化处理

```python
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']    # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False      # 用来正常显示负号
(data/data.iloc[0]).plot(figsize=(8, 6))
plt.show()
```

得到股价从2019年至2020年的走势图（股价在2019年首个交易日归一化处理）

![Stock Price Chart](./figs/stock-price-chart.png)

不难看出，走势还是存在一定的分化

#### Step 2