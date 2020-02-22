# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# ## math 数学函数

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


# + [markdown] toc-hr-collapsed=true
# ## str 方法
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
# ```python
# str.strip([chars])
# ```
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
# ```python
# str.split(str="", num=string.count(str))
# ```
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


# -

# ## function 函数

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
# ```
# + [markdown] toc-hr-collapsed=false toc-hr-collapsed=false
# ## re 正则
# -


# **正则表达式是对字符串操作的一种逻辑公式，就是用事先定义好的一些特定字符、及这些特定字符的组合，组成一个“规则字符串”，这个“规则字符串”用来表达对字符串的一种过滤逻辑。**

# ### 匹配过程

# 1. 依次拿出表达式和文本中的字符比较，
# 2. 如果每一个字符都能匹配，则匹配成功；一旦有匹配不成功的字符则匹配失败。
# 3. 如果表达式中有量词或边界，这个过程会稍微有一些不同。

# + [markdown] toc-hr-collapsed=true
# ### 语法规则
# -

# #### 基本语法
#
# 语法|说明|表达式实例|完整匹配的字符串字符
# :---:|:--|:---|:---
# 一般字符|匹配自身|abc|abc
# \\|<p>转义字符，使后面一个字符改变原来的意思. <p>如果有字符\*需要匹配，可以使用\\\*或者字符集[\*]|a\\\.c<p>a\\\\c|a.c<p>a\\c
# [...]|<p>字符集（字符类）。对应的位置可以是字符集中任意字符。<p>字符集中的字符可以逐个列出，也可以给个范围，如[abc]或者[a-c]。<p>第一个字符如果是^则表示取反，如[^abc]表示不是abc的其它字符。<p>所有的特殊字符在字符集中都失去其原有的特殊含义。在字符集中如果使用]、-或者^，可以在前面加上反斜杠，或者把]、-放在第一个字符，把^放在非第一个字符。|a[bcde]e|abc<p>ace<p>ade<p>aee
#

import re
print(re.search('abc', 'abc'))

specialcharlst = ['.', '*', '\\', '-', '(', ')', '[', ']']
print(specialcharlst)
print(re.findall('a\.c', 'a.c'))

ptn = r"[.*\-()\[\]^]"
print(ptn)
print(re.findall(ptn, "abc.(Home is warmful.[chasing]) *.txt is text file. 2^2=4"))

# #### 预定义字符集
#
# 语法|说明|表达式实例|完整匹配的字符串字符
# :---:|:--|:---|:---
# |**预定义字符集（可以写在字符集[...]中）**||
# \\d|数字：0-9|a\\dc|<p>a1c<p>~~abc~~
# \\D|非数字：[^\\d]|a\\Dc|<p>abc<p>~~a3c~~
# \\s|空白字符：[ \t\r\n\f\v]|a\\sc|<p>a c<p>~~abc~~
# \\S|非空白字符：[^\\s]|a\\Sc|<p>abc<p>~~a c~~
# \\w|单词字符：[A-Za-z0-9_]|a\\wc|abc
# \\W|非单词字符：[^\\w]|a\\Wc|a c
#

predefinedteststr = 'abc a2c a4c a c '
print(re.findall('a\dc', predefinedteststr))
print(re.findall('a\Dc', predefinedteststr))
print(re.findall('a\sc', predefinedteststr))
print(re.findall('a\Sc', predefinedteststr))
print(re.findall('a\wc', predefinedteststr))
print(re.findall('a\Wc', predefinedteststr))

# #### 数量词
#
# 语法|说明|表达式实例|完整匹配的字符串字符
# :---:|:--|:---|:---
# |**数量词（用在字符或(...)之后）**||
# \*|匹配前一个字符0次或无限次|abc\*|<p>ab<p>abc<p>abccc
# \+|匹配前一个字符1次或无限次|abc+|<p>~~ab~~<p>abc<p>abccc
# \?|匹配前一个字符0次或1次|abc?|<p>ab<p>abc<p>~~abcc~~
# {m}|匹配前一个字符m次|ab{2}c|<p>abbc<p>~~abbbc~~
# {m,n}|<p>匹配前一个字符m至n次。<p>m和n可以省略；若省略m，则匹配0至m次；若省略n，则匹配m至无限次。|ab{1,2}c|<p>~~ac~~<p>abc<p>abbc<p>~~abbbc~~
# \*\? \+\? \?\? {m,n}\?|使\* \+ \? 和{m,n}变成非贪婪模式|示例在下文介绍|
#

numberteststr = 'ab abc abcc abccc abcccc'
print(re.findall('abc*', numberteststr))
print(re.findall('abc+', numberteststr))
print(re.findall('abc?', numberteststr))
print(re.findall('abc{2}', numberteststr))
print(re.findall('abc{2,4}', numberteststr))
print("-----?的非贪婪模式-----")
print(re.findall('abc*?', numberteststr))
print(re.findall('abc+?', numberteststr))
print(re.findall('abc??', numberteststr))
print(re.findall('abc{2}?', numberteststr))
print(re.findall('abc{2,4}?', numberteststr))

# #### 边界匹配
#
# 语法|说明|表达式实例|完整匹配的字符串字符
# :---:|:--|:---|:---
# |**边界匹配**（不消耗待匹配字符串的字符）||
# \^|<p>匹配字符串开头<p>在多行模式中匹配每一行的开头|^abc|abc
# \$|<p>匹配字符串末尾<p>在多行模式中匹配每一行的末尾|abc$|abc
# \\A|仅匹配字符串开头|\\Aabc|abc
# \\Z|仅匹配字符串结尾|abc\\Z|abc
# \\b|<p>匹配\\w和\\W之间<p>**python中\\b为退格，因此需要r"\\bword"（即raw字符串）来表示**|a\\b!bc|a!bc
# \\B|<p>匹配\\w和\\w之间<p>[^\b]|a\Bbc|abc
#

delimiterstr = 'abc abc abd abe abf a!bg abg\nabb abz'
print(re.findall('^ab\w', delimiterstr, re.MULTILINE))
print(re.findall('^ab\w', delimiterstr))
print(re.findall('ab\w$', delimiterstr, re.MULTILINE))
print(re.findall('ab\w$', delimiterstr))
print(re.findall('\Aa\w', delimiterstr, re.MULTILINE))
print(re.findall('\Aa\w', delimiterstr))
print(re.findall('ab\w\Z', delimiterstr, re.MULTILINE))
print(re.findall('abc\Z', delimiterstr))
print(re.findall(r'a\b\Wb\w', delimiterstr))
print(re.findall('a\Bb\w*', delimiterstr))
print(re.findall(r'\b\w+\b', delimiterstr))

# #### 逻辑、分组
#
# 语法|说明|表达式实例|完整匹配的字符串字符
# :---:|:--|:---|:---
# |**逻辑、分组**||
# \||<p>\|代表左右表达式任意匹配一个<p>它总是先尝试匹配左边的表达式，一旦成功则跳过对右边表达式的判断<p>如果没有括号包括，则范围指的是整个正则表达式|abc\|def|<p>abc<p>def
# (...)|<p>被括起来的表达式将作为分组，从左边开始每遇到一个左括号\(，编号+1<p>另外，分组表达式作为一个整体，可以后接数量词。表达式中的\|仅在该括号中有效|<p>\(abc\){2}<p>a\(123\|456\)c|<p>abcabc<p>a456c
# \(\?P\<name\>\)|分组，除了原有的编号外再指定一个额外的别名|\(\?P\<id\>abc\){2}|abcabc
# \\\<number\>|<p>引用编号为\<number\>的分组匹配到的字符串<p>需要用raw标识正则字符串<p>引用时匹配的是内容物，而不是规则，这里面有个实例化的意思|\(\\d\)abc\\1|<p>2abc2<p>~~4abc5~~
# \(\?P\=name\)|引用别名为\<name\>的分组匹配到的字符串|\(\?P\<id\>\\d\)abc\(\?P\=id\)|<p>2abc2<p>~~4abc5~~
#

logicgroupstr = "abc def abcabc a123c a456c 34abc34 23abc34 2abc2"
print(re.findall('abc|def', logicgroupstr))
print(re.findall('(?:abc){2}', logicgroupstr))
print(re.findall('a(?:123|456)c', logicgroupstr))
print(re.search(r'(\d)abc\1', logicgroupstr))
print(re.search(r'(?P<id>\d)abc(?P=id)', logicgroupstr))

# #### 特殊构造（不作为分组）
#
# 语法|说明|表达式实例|完整匹配的字符串字符
# :---:|:--|:---|:---
# |特殊构造（不做为分组）||
# \(\?:...\)|\(...\)的不分组版本，用于使用“\|”或后接数量词|\(\?:abc\){2}|abcabc
# \(\?iLmsux\)|iLmsux的每个字符代表一个匹配模式，只能用在正则表达式的开头，可选多个。|\(\?i\)abc|AbC
# \(\?#...\)|#之后的内容作为注释会被忽略|abc\(\?#comment\)123|abc123
# \(\?\=...\)|之后的字符串内容需要匹配表达式才能匹配成功。不消耗字符串内容。|a\(\?\=\\d\)|<p>a2<p>~~ab~~
# \(\?\!...\)|之后的字符串内容需要匹配表达式才能匹配成功。不消耗字符串内容。|a\(\?\!\\d\)|<p>~~a2~~<p>ab
# \(\?\<\=...\)|之前的字符串内容需要匹配表达式才能匹配成功。不消耗字符串内容。|\(\?\<\=\\d\)a|<p>2a<p>~~ba~~
# \(\?\<\!...\)|之前的字符串内容需要匹配表达式才能匹配成功。不消耗字符串内容。|\(\?\<\!\\d\)a|<p>~~2a~~<p>ba
# \(\?\(id/name\)yes-pattern\|no-pattern\)|<p>如果id/别名为name的组匹配到字符，则需要匹配yes-pattern，否则需要匹配no-pattern。<p>no-pattern可以省略。|\(\\d\)abc\(\?\(1\)\\d\|abc\)|<p>1abc2<p>abcabc

specialgroupstr = "abcabc AbC abc123 a2 ab 2a ba aabcabc 1abc2 aabcabc"
print(re.search('(?:abc){2}', specialgroupstr))
print(re.findall('(?i)abc', specialgroupstr))
print(re.findall('abc(?=\d).*?\s', specialgroupstr))
print(re.findall('abc(?!\d).+?\s', specialgroupstr))
print(re.findall('(.(?<=\d)abc)', specialgroupstr))
print(re.findall('(?<!\d)abc', specialgroupstr))
print(re.findall('(\d)abc(?(1)\d|abc)', specialgroupstr))
print(re.search('(\d)abc(?(1)\d|abc)', specialgroupstr)) # 迷迷糊糊，没搞懂

# ### 演练池

# #### 去除控制符

neirong = "\x04heart5\x011 is a man."
print(neirong)
re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f]', '', neirong)

# #### just for test

# +
import re
findit = re.findall(r'\b(\w+)\b', 'a@!bc@kcde')
print(f"{findit}")
findit = re.findall(r'\b\w+', 'a@!bc@kcde')
print(f"{findit}")
findit = re.findall(r'\B\w+', 'a@!bc@kcde')
print(f"{findit}")
findit = re.findall(r'\w+\B', 'a@!bc@kcde')
print(f"{findit}")
print(re.findall(r"a\b\Wbc", "a!bc"), "\n")

print(re.findall(r"(\d)abc\1", "5abc5"))
print(re.findall(r"(\d)abc\1", "5abc6"))
print(re.findall(r"(?P<id>\d)abc(?P=id)", "5abc5"))
print(re.findall(r"(?P<id>\d)abc(?P=id)", "5abc6"))
print(re.findall(r"(?P<id>\d)abc(?=\d)", "5abc5"))
print(re.findall(r"(?P<id>\d)abc(?=id)", "5abc6"))

# -
# #### 从房间链接提取用户名和房间号

fangtabstr = "2020-02-13 11:27:21	True	搓雀雀(群)白晔峰	Text	http://s0.lgmob.com/h5_whmj_qp/?d=852734"
namestr = fangtabstr.split('\t')[2]
ptn = r'\b\w+\b'
print(ptn, re.findall(ptn, namestr))
print(ptn, re.findall(ptn, namestr)[-1])
print(ptn, re.findall(ptn, "白晔峰")[-1])
fangidstr = fangtabstr.split("\t")[-1]
print(re.findall("d=(\d+)", fangidstr)[-1])

# ## 列表和字典之间的相互转换


# ### 使用zip函数

a = ['a1','a2','a3','a4']
b = ['b1','b2','b3']
d = zip(a,b)
print(dict(d)) 

# ### 使用嵌套列表转换成字典

a = ['a1','a2']
b = ['b1','b2']
c = [a,b]
print(dict(c)) # {'a1': 'a2', 'b1': 'b2'}
# 相当于遍历子列表，如下
dit = {}
for i in c:
    dit[i[0]] = i[1]
print(dit)

# 字典转换成列表

# +
dit = {'name':'zxf',
       'age':'22',
       'gender':'male',
       'address':'shanghai'}
 
# 将字典的key转换成列表
lst = list(dit.keys())
print(lst)  # ['name', 'age', 'gender', 'address']
 
# 将字典的value转换成列表
lst2 = list(dit.values())
print(lst2)
# -


