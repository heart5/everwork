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

# ## 试验田

numb = 127136
print(hex(127136))
hh = chr(127136) # 127136
hh 

# ## UNICODE字符

# ### 麻将

startcode = 126976
numbegin = 0
numend = 288
codenumlst = [startcode + i for i in range(numbegin, numend)]
# print(codenumlst)
codehexlst = [hex(x) for x in codenumlst]
# print(codehexlst)
codecharlst = [chr(x) for x in codenumlst]
print(codecharlst)

# ### 十二生肖

shiershengxiao = ['\N{Snake}', '\N{Horse}', '\N{Sheep}', '\N{Monkey}', '\N{Chicken}', '\N{Dog}', '\N{Pig}', '\N{Mouse}', '\N{Ox}', '\N{Tiger}', '\N{Rabbit}', '\N{Dragon}']
for animal in shiershengxiao:
    print(animal + f"{ord(animal)}", end='\t')

# ### 扑克牌

startcode = 127136
numbegin = 0
numend = 64
codenumlst = [startcode + i for i in range(numbegin, numend)]
# print(codenumlst)
codehexlst = [hex(x) for x in codenumlst]
# print(codehexlst)
codecharlst = [chr(x) for x in codenumlst]
print(codecharlst)

# ### 象棋

startcode = 129536
numbegin = 0
numend = 64
codenumlst = [startcode + i for i in range(numbegin, numend)]
# print(codenumlst)
codehexlst = [hex(x) for x in codenumlst]
# print(codehexlst)
codecharlst = [chr(x) for x in codenumlst]
print(codecharlst)

# ### 图标

startcode = 127744
numbegin = 0
numend = 512
codenumlst = [startcode + i for i in range(numbegin, numend)]
# print(codenumlst)
codehexlst = [hex(x) for x in codenumlst]
# print(codehexlst)
codecharlst = [chr(x) for x in codenumlst]
print(codecharlst)

hex(ord('🐎'))
startcode = '🐎'
codenumlst = [ord(startcode) + i for i in range(-10, 10)]
print(codenumlst)
codehexlst = [hex(ord(startcode) + i) for i in range(1, 10)]
print(codehexlst)
codecharlst = [chr(x) for x in codenumlst]
print(codecharlst)

# ## 小测试

# +
import sys

print("红黄褐")
print(sys)
print(sys.api_version)
print(f'this is what? meaning')
int('1FA00', 16)
# -
print("This is another cell.")
print("谁去")


print("The third.")
print('好了吧。需要手动安装啊。')

import pathmagic
aaa = "120"
print(f"The code is {aaa}")
print(pathmagic.context)


