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

# ### 和白珍石一起学编程（python）

# #### 文本在电脑屏幕的输出

print('白珍石是一名优秀的少年。\n这是第二排的内容。。\b')
print("我们在海南隔离。\t前面有一个Tab控制符。")

print('我爱学习')

print('我和同学去野餐，，\b\t我们都很高兴\n\n然后我们就回家了。')

# #### 变量

hainanstr = '我是小小少年'
print(hainanstr)
hainanstr = '学习编程是一件很棒的事情'
print(hainanstr)

goodstr = '我和我的同学一起玩'
print(goodstr)
goodstr = '我们都很高兴'
print(goodstr)

# #### 数字

age = 10
name = '白珍石'
print(f"{name}的年龄是{age}岁。")

personlist = [['白珍石',10], ['戚轩溢',9], ['王贞元',10], ['白珍赫',8], ['白珍星', 21]]
for name,age in personlist:
    print(f"{name}的年龄是{age}岁")

firstnum = 19
secondnum = 6
print(f"{firstnum} + {secondnum} = {firstnum + secondnum}")
print(f"{firstnum} - {secondnum} = {firstnum - secondnum}")
print(f"{firstnum} * {secondnum} = {firstnum * secondnum}")
print(f"{firstnum} / {secondnum} = {firstnum / secondnum}")
print(f"{firstnum} 整除 {secondnum} , 商为  {firstnum // secondnum}")
print(f"{firstnum} 整除 {secondnum} ，余数为  {firstnum % secondnum}")

personlist = [['白珍石',10], ['戚轩溢',9], ['王贞元',10], ['白珍赫',8], ['白珍星', 21]]
for name,age in personlist:
    print(f"{name}的年龄是{age}岁")

personlist = [['白珍石', '黄'], ['戚轩溢', '蓝']]
for name,team in personlist:
    print(f"{name}喜欢{team}色")

www  = 1
wwww = 1
print(f"{www} + {wwww} = {www + wwww}")
print(f"{www} - {wwww} = {www - wwww}")
print(f"{www} * {wwww} = {www * wwww}")
print(f"{www} / {wwww} = {www / wwww}")
print(f"{www} 整除 {wwww} , 商为  {www // wwww}")
print(f"{www} 整除 {wwww} ，余数为  {www % wwww}")

print('\t\t\t888\n\n\n\t\t\t666')

a = 1
b = 2
c = 3
d = 4
e = 5
print(f"{a*a}")
print(f"{a*b}\t{b*b}")
print(f"{a*c}\t{b*c}\t{c*c}")
print(f"{a*d}\t{b*d}\t{c*d}\t{d*d}")
print(f"{a*e}\t{b*e}\t{c*e}\t{d*e}\t{e*e}")

a = 1
b = 2
c = 3
d = 4
e = 5
f = 6
g = 7
h = 8
i = 9
print(f"{a*a}\n{a*b}\t{b*b}\n{a*c}\t{b*c}\t{c*c}\n{a*d}\t{b*d}\t{c*d}\t{d*d}\n{a*e}\t{b*e}\t{c*e}\t{d*e}\t{e*e}")
print(f"{a*f}\t{b*f}\t{c*f}\t{d*f}\t{e*f}\t{f*f}\n{a*g}\t{b*g}\t{c*g}\t{d*g}\t{e*g}\t{f*g}\t{g*g}")
print(f"{a*h}\t{b*h}\t{c*h}\t{d*h}\t{e*h}\t{f*h}\t{g*h}\t{h*h}\n{a*i}\t{b*i}\t{c*i}\t{d*i}\t{e*i}\t{f*i}\t{g*i}\t{h*i}\t{i*i}")

# +
tenlst = list(range(1, 10))
print(tenlst)
# print('\t'.join([str(x) for x in tenlst]))

for i in range(1, 10):
    if i!= 1:
        print(str(i) + "\t" * (i - 1), end='')
    for j in range(1, 10):
        if i > j:
            continue
        print(f"{i * j}", end='\t')
        if j ==9:
            print()
# -
print('我是一个好学生，\n我爱学习。')

try1 = '我是好学生'
print(try1)

water = "水"
hot = True
print(water)
print(f'{water} is hot ?\t', hot)
print('\n')

stone = 1/2/3/4/5/6/7/8/9
print(stone)

ans = 9*8*7*6
print(ans)

# 给出一个数，比如432，按照一定的步长，比如50，分组。形如：(0, 50, 50), (50, 50, 100), (100, 50, 150), (150, 50, 200),...,(400, 32, 432)

432 // 50 + 1


