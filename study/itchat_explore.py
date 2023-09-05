# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     formats: ipynb,py:percent
#     notebook_metadata_filter: jupytext,-kernelspec,-jupytext.text_representation.jupytext_version
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
# ---

# %% [markdown]
# # itchat扒库

# %% [markdown]
# ## 库准备

# %%
import uuid
import os
import random
import itchat

import matplotlib.pyplot as plt # plt 用于显示图片
import matplotlib.image as mpimg # mpimg 用于读取图片
from pandas.plotting import register_matplotlib_converters
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

import numpy as np
import pandas as pd
import sqlite3 as lite
from binascii import hexlify, unhexlify

import pathmagic
with pathmagic.context():
    from func.first import getdirmain, touchfilepath2depth
    from life.wcdelay import getdelaydb, showdelayimg
    from func.litetools import ifnotcreate
    from func.wrapfuncs import timethis, logit
    from func.logme import log
    from func.sysfunc import uuid3hexstr, sha2hexstr
    from func.nettools import isitchat

# %% [markdown]
# ## 热启动

# %% [markdown]
# ##### 直接热启动

# %%
pklabpath = os.path.relpath(touchfilepath2depth(getdirmain() / 'itchat.pkl'))
print(pklabpath)

# %%
# isitchat??

# %%
# itchat.auto_login??

# %%
itchat.auto_login(hotReload=True, statusStorageDir=pklabpath)   #热启动你的微信

# %% [markdown]
# ##### 函数方式热启动

# %%
isitchat(pklabpath)

# %% [markdown]
# ##### 判断是否处于活跃状态

# %%
itchat.originInstance.alive

# %%
itchat.originInstance.hotReloadDir
os.path.abspath(itchat.originInstance.hotReloadDir)

# %% [markdown]
# ##### `itchat.search_friends()`

# %% [markdown]
# 1. 直接调用，返回登录用户信息

# %%
itchat.search_friends()

# %% [markdown]
# 2. 输入备注、微信号、昵称任意一种赋给name，返回对应用户的信息

# %%
itchat.search_friends(name='小元宝')

# %% [markdown]
# 3. 获取特定UserName的用户信息

# %%
itchat.search_friends(userName='@aaf224b457aa35a3f5ebef4ae47a945a')
log.info(f"just a test for connect changed")

# %% [markdown]
# 4. 通过wechatAccount获取用户信息。不成功！可能是微信的隐私政策导致的。

# %%
itchat.search_friends(wechatAccount='heart57479')

# %% [markdown]
# ##### `itchat.web_init()`

# %% [markdown]
# 初始化，成功则返回值为0，内容包括：

# %% [markdown]
#     1. BaseResponse。0是成功，返回的错误信息为空字符串；否则
#     2. Count。待显示的最近联系人数量。
#     3. ContactList。最近联系人信息。
#     4. SyncKey。同步口令。有数量count，还有信息id？
#     5. User。登录者信息。
#     6. Chatset。聊天集？
#     7. 'SKey': '@crypt_8dc3f7b8_e63df55a027c431016c33d3135f2d9fa'
#     8. 'ClientVersion': 654314551,
#     9. 'SystemTime': 1584465493,
#     10. 'GrayScale': 1,
#     11. 'InviteStartCount': 40,
#     12. 'MPSubscribeMsgCount': 4, 待显示的公众号数量
#     13. 'MPSubscribeMsgList': 公众号信息列表
#     14. 'ClickReportInterval': 600000

# %%
itchat.web_init()

# %% [markdown]
# ##### `itchat.get_contact()`

# %% [markdown]
# 群列表。好像是所有群，就是不知道是按照什么顺序排列的，还是随意排？！
#
# dict中有IsOwner属性，是否群主

# %%
ctlst = itchat.get_contact(update=True)
len(ctlst)
# [ct for ct in ctlst if ct['NickName'] == '白晔峰']
# 列出群名，还可以区别是否群主的群
'\t'.join([qun['NickName'] for qun in ctlst if qun['IsOwner'] == 0])

# %% [markdown]
# ##### `itchat.originInstance.HotReloadDir`

# %% [markdown]
# 热启动的pkg文件地址。

# %%
itchat.originInstance.hotReloadDir

# %%
os.path.abspath(itchat.originInstance.hotReloadDir)

# %%
uuid3hexstr(os.path.abspath(itchat.originInstance.hotReloadDir))

# %% [markdown]
# 参照，看是不是每次会不一样

# %%
uuid3hexstr(os.path.abspath(itchat.originInstance.hotReloadDir))

# %% [markdown]
# ##### `itchat.originInstance.receivingRetryCount`

# %% [markdown]
# 接收信息时重试的次数（默认值是5），还可以赋值设定

# %%
itchat.originInstance.receivingRetryCount

# %%
itchat.originInstance.receivingRetryCount = 20

# %% [markdown]
# ##### `itchat.originInstance.loginInfo`

# %% [markdown]
# 登录相关信息明细：
# 1. url。主地址
# 2. fileUrl。文件地址？
# 3. syncUrl。同步网址？
# 4. deviceid。设备id。因设备不同而不同？
# 5. Sid。未知
# 6. Uin。未知。微信顺序号？
# 7. DeviceID。
# 8. skey。同步密匙。
# 9. wxsid。同Sid
# 10. wxuin。同Uin
# 11. pass_ticket。同DeviceID。
# 12. User。用户信息。可以用dict转换成字典格式。
# 13. SyncKey。同步值？

# %%
itchat.originInstance.loginInfo

# %% [markdown]
# 备参。看每次运行是否有什么不一样。

# %%
itchat.originInstance.loginInfo

# %%
dict(itchat.originInstance.loginInfo['User'])

# %% [markdown]
# ##### 联系人列表、公众号列表、聊天群列表

# %%
print(u'\u2005')

# %%
itchat.originInstance.memberList

# %%
itchat.originInstance.mpList

# %%
itchat.originInstance.chatroomList

# %%
itchat.load_login_status('../itchat.pkl')

# %%
