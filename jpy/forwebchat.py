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

# +
import os
import itchat
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters

import pathmagic
with pathmagic.context():
    from func.first import getdirmain, touchfilepath2depth
    from life.wcdelay import getdelaydb, showdelayimg
# -

pklabpath = os.path.relpath(touchfilepath2depth(getdirmain() / 'itchat.pkl'))
print(pklabpath)
itchat.auto_login(hotReload=True, statusStorageDir=pklabpath)   #热启动你的微信

frdlst = itchat.get_friends()

# +

import matplotlib.pyplot as plt # plt 用于显示图片
import matplotlib.image as mpimg # mpimg 用于读取图片
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import numpy as np

register_matplotlib_converters()

print(frdlst[10])
frdinfolst = list()
attrlst = ['UserName', 'NickName', 'ContactFlag', 'RemarkName', 'Sex', 'Signature', 'StarFriend', 'AttrStatus', 'Province', 'City', 'SnsFlag', 'KeyWord']
for frd in frdlst[:3]:
    frdinfo = list()
    if 'UserName' in frd.keys():
#         print(frd['StarFriend'])
        headimg = itchat.get_head_img(frd["UserName"])
        imgfrombytes = Image.open(BytesIO(headimg))
        # 转成array格式——常规
        imgnp = np.array(imgfrombytes)
        print(type(headimg), imgfrombytes, imgnp)
        
        # 展示array代表的图像
        plt.imshow(imgnp)
        plt.show()
#         print(headimg)
        for attr in attrlst:
            print(attr, frd[attr])
#         for key, value in frd.items():
#             print(key, value)
        print('\n')
    else:
        print(f'不存在UserName键值')

# +

import matplotlib.pyplot as plt # plt 用于显示图片
import matplotlib.image as mpimg # mpimg 用于读取图片
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import numpy as np
 
lena = mpimg.imread('../QR.png') # 读取和代码处于同一目录下的 lena.png
# 此时 lena 就已经是一个 np.array 了，可以对它进行任意处理
lena.shape #(512, 512, 3)
 
plt.imshow(lena) # 显示图片
plt.axis('off') # 不显示坐标轴
plt.show()
