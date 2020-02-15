# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.3
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# + [markdown] pycharm={"name": "#%% md\n"}
# ### python中的除法和取整
#
# 1. /是精确除法，//是向下取整除法，%是求模
# 2. %求模是基于向下取整除法规则的
# 3. 四舍五入取整round, 向零取整int, 向下和向上取整函数math.floor, math.ceil
# ---
# - first
# - second
# - third

# + pycharm={"name": "#%%\n", "is_executing": false}

print('usage of 3 operators /, // and % in python 3.4')
print('1). usage of /')
print('10/4 = ', 10 / 4)
print('-10/4 = ', -10 / 4)
print('10/-4 = ', 10 / -4)
print('-10/-4 = ', -10 / -4)

print('\n2). usage of //')
print('10//4 = ', 10 // 4)
print('-10//4 = ', -10 // 4)
print('10//-4 = ', 10 // -4)
print('-10//-4 = ', -10 // -4)

print('\n3). usage of %')
print('10%4 = ', 10 % 4)
print('-10%4 = ', -10 % 4)
print('10%-4 = ', 10 % -4)
print('-10%-4 = ', -10 % -4)

# -

# ### **find() 方法**
# ##### 用于查找字符串中是否能够找到子字符串，找到就返回所处位置，找不到则返回-1

teststr = "This is a very hard road."
print(f"\'is\' is find in \"{teststr}\" at {teststr.find('is')}")
print(f"\'iss\' is find in \"{teststr}\" at {teststr.find('iss')}")

# ### **strip() 方法**
# ##### 用于移除字符串头尾指定的字符（默认为空格或换行符）或字符序列。
#
# #### 语法
# ##### str.strip([chars])
#
# ---

# + pycharm={"name": "#%%\n", "is_executing": false}
tstr1 = " 我是一个兵 \n"
print(tstr1)
print(tstr1.strip())

tstr2 = "12dfahkj56232211"
print(tstr2)
print(tstr2.strip('12'))

# + [markdown] pycharm={"name": "#%% md\n"}
# ### **split() 方法**
# ##### split() 通过指定分隔符对字符串进行切片，如果参数 num 有指定值，则分隔 num+1 个子字符串
#
# #### 语法
# ##### str.split(str="", num=string.count(str))
#
# #### 参数
# * str -- 分隔符，默认为所有的空字符，包括空格、换行(\n)、制表符(\t)等。
# * num -- 分割次数。默认为 -1, 即分隔所有。
# -

strp = "This is a line.\n Will you be happy?\t"
print(strp.split())
print(strp.split('.'))
print(type(strp.split('.')))
print([x.strip() for x in strp.split('.')])

# + [markdown] pycharm={"name": "#%% md\n"}
# ### **translate() 方法**
# ##### str def translate(self, table: Union[Mapping[int, Union[int, str, None]], Sequence[Union[int, str, None]]])
#   -> str
# ##### 使用给出的转换表替换字符串中的每一个字符

# + pycharm={"is_executing": false}
user_input = "This\nstring has\tsome whitespaces...\r\n"

character_map = {
    ord('\n'): ' ',
    ord('\t'): ' ',
    ord('\r'): None
}
user_input.translate(character_map)  # This string has some whitespaces... "


# + [markdown] pycharm={"name": "#%% md\n"}
# #### 仅支持关键字参数（kwargs）的函数
#
#
#

# + pycharm={"name": "#%%\n", "is_executing": false}
def test(*, a, b):
    print(a, b)
    print()


test(a="value", b="value 2")  # Works...
test(a='2', b='you are great')  # TypeError: test() takes 0 positional arguments...

# + [markdown] pycharm={"name": "#%% md\n"}
# ```
# def test(*, a, b):
#     print(a, b)
#     print()
#
# test(a="value", b="value 2")  # Works...
# test(a='2', b='you are great')  # TypeError: test() takes 0 positional arguments...
# ```
# 流程图
#
# ```flow
# st=>start: 开始
# op=>operation: My Operation
# cond=>condition: Yes or No?
# e=>end
# st->op->cond
# cond(yes)->e
# cond(no)->op
# &```
