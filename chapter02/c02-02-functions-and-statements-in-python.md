# Functions and Statements in Python

## Functions

定义函数有两种方式，一种是用 `def` 语法构建新的函数，另一种是直接运用 `lambda` 函数构建新的函数

### Using def Syntax

运用 `def` 语法时，函数的基本框架如下

```python
def 函数名(参数):
    '''函数说明文档'''
    函数主体
    return 返回对象
```

注意

- 函数说明文档可以选择不写
- 输入函数主体以及 `return` 的前面要缩进，在 Python 中缩进是运用 Tab 键（4个空格）来完成

以计算算术平均收益率为例，表达式如下

$$
\overline{R}=\frac{\sum_{i=1}^{n}R_i}{n} \tag{2-1}
$$

代码如下

```python
def mean_a(r):
    '''定义一个求解算术平均收益率的函数
    r: 代表收益率的一个列表'''
    total=sum(r)
    return total/len(r)
```

这样就把计算算术平均收益率的函数 `mean_a` 在 Python 中做了定义，并可以实际使用

```python
list1 = [-0.0568, -0.0703, 0.0393, 0.0544, 0.1232]
mean_a(list1)
```

输出

```console
0.01796
```

通过以上的计算得到算术平均收益率是 1.796%，当然也可以通过 `sum(list1)/5` 来进行验算结果是否正确

### Using lambda Functions

`lambda` 函数在 Python 中被称为是匿名函数，具体的函数基本格式如下

$$
函数名=lambda 参数:表达式
$$

运用 `lambda` 定义函数时，撰写的代码通常是控制在一行以内，因此可以用 `lambda` 写相对简单的函数，或者复杂函数的一个组成部分

对于前面的例子，示例代码如下

```python
mean_A = lambda r: sum(r)/len(r)    # 用 lambda 定义函数

mean_A(r=list1)
```

输出

```console
0.01796
```

显然，计算结果与用 `def` 所定义函数的计算结果是完全一样的

## Statements in Python

在 Python 中，编程的语句分为条件语句和循环语句两大类，可以单独运用，也可以结合使用

### Conditional Statements

条件语句是通过一条或多条语句的执行结果（`True` 或 `False`）来决定执行的代码块，条件语句的基本语法框架分为以下三大类型

1. 只有一个判断条件

```python
if 判断语句:
    执行语句 1
else:
    执行语句 2
```

1. 有两个判断条件

```python
if 判断语句 1:
    执行语句 1
elif 判断语句 2:
    执行语句 2
else:
    执行语句 3
```

1. 有三个及以上的判断条件

```python
if 判断语句 1:
    执行语句 1
elif 判断语句 2:
    执行语句 2
elif 判断语句 3:
    执行语句 3
...
elif 判断语句 n:
    执行语句 n
else:
    执行语句 n+1
```

需要注意的是，在执行语句前面需要缩进，缩进依然是运用 Tab 键，并且在 Ipython 中会自动进行缩进

比如我们写一个猜总监身高的游戏

```python
high_of_ty = 159
guess = int(input(">>:"))
if guess > high_of_ty:
    print("猜的太高了，往矮里试试...")
elif guess < high_of_ty:
    print("猜的太矮了，往高里试试...")
else:
    print("恭喜你，猜对了...")
```

再来个匹配成绩的小程序吧，成绩有 ABCDE 这 5 个等级，与分数的对应关系如下

```console
A    90-100
B    80-89
C    60-79
D    40-59
E    0-39
```

要求用户输入 0-100 的数字后，你能正确打印其对应成绩

```python
score = int(input("输入分数:"))
if score > 100:
    print("注意，最高分才100...")
elif score >= 90:
    print("A")
elif score >= 80:
    print("B")
elif score >= 60:
    print("C")
elif score >= 40:
    print("D")
else:
    print("太笨了...E")
```

这里有个问题，就是当我输入 `95` 的时候 ，它打印的结果是 `A`，但是 `95` 明明也大于第二个条件 `elif score >=80:`, 为什么不打印 B 呢？这是因为代码是从上到下依次判断，只要满足一个，就不会再往下走啦，这一点一定要清楚呀！

### Loop Statements

在 Python 中，循环语句包括了 `for` 循环和 `while` 循环，但是在金融领域中，常用的是 `for` 循环

#### for Loop

`for` 循环可以遍历各种序列的项目，如一个列表或者字符串，`for` 循环的语法结构如下

```python
for 迭代变量(iterating_var) in 序列(比如列表、字符串等):
    陈述(statements)
```

注意，在陈述前面需要缩进，并且缩进依然是运用 Tab 键

#### while Loop

`while` 语句是用于循环执行程序，具体就是在某条件下，循环执行某段程序，以处理需要重复处理的相同任务，基本的语法结构如下

```python
while 判断条件:
    执行语句
```

注意，在执行语句前面需要缩进，并且缩进依然是运用 Tab 键

#### Loop Control Statements

在 Python 中，循环控制语句包括了 `break`、`continue`、`pass`，下表列出了循环控制语句的名称以及相关的功能

| 循环控制语句名称 | 具体功能 |
|:---:|:---|
| break | 终止当前循环、且跳出整个循环 |
| continue | 终止当次循环，直接执行下一次循环 |
| pass | 不执行任何操作，一般用于占据一个位置 |

- 关于 `break` 的列子

    ```python
    count = 0
    while count <= 100:     # 只要count<=100就不断执行下面的代码
        print("loop ", count)
        if count == 5:
            break
        count += 1          # 每执行一次，就把count+1，要不然就变成死循环啦，因为count一直是0
    print("-----out of while loop ------")
    ```

    输出

    ```console
    loop  0
    loop  1
    loop  2
    loop  3
    loop  4
    loop  5
    -----out of while loop ------
    ```

- 关于 `continue` 的列子

    ```python
    count = 0
    while count <= 100 : 
        count += 1
        if count > 5 and count < 95:
            # 只要count在6-94之间，就不走下面的print语句，直接进入下一次loop
            continue 
        print("loop ", count)
    print("-----out of while loop ------")
    ```

    输出

    ```console
    loop  1
    loop  2
    loop  3
    loop  4
    loop  5
    loop  95
    loop  96
    loop  97
    loop  98
    loop  99
    loop  100
    loop  101
    -----out of while loop ------
    ```
