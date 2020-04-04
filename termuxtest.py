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

# ### 库准备

# +
import os
import itchat

import pathmagic
with pathmagic.context():
    from func.first import dirmainpath
    from life.wcdelay import showdelayimg
    from func.termuxtools import *
# -

# ### termuxtools各种功能函数

# 几乎都是硬件相关

# #### 粘贴板

termux_clipboard_get()

# #### 手机联系人

ctlst = termux_contact_list()

type(ctlst)

# +
import re
ptn = re.compile(u"{(.+)}", re.MULTILINE)
ptn = re.compile(u"({.+?})", re.MULTILINE | re.DOTALL)
re.findall(ptn, ctlst)[:3]
ptnname = re.compile("\"name\": \"(.+?)\"", re.MULTILINE)
ctnamelst = re.findall(ptnname, ctlst)
ptnphone = re.compile("\"number\": \"(.+?)\"", re.MULTILINE)
ctphonelst = re.findall(ptnphone, ctlst)
len(list((zip(ctnamelst, ctphonelst))))
len(dict((zip(ctnamelst, ctphonelst))))

# print(ctlst)
# -

# #### 电池

# ##### 【电池电量模块调用】

# +
import pathmagic
with pathmagic.context():
    from etc.battery_manage import getbattinfodb, showbattinfoimg
    from func.first import touchfilepath2depth, getdirmain
    
dbnameouter = touchfilepath2depth(getdirmain() / "data" / "db" / f"batteryinfo.db")
showbattinfoimg(dbnameouter)
# getbattinfodb(dbnameouter)
# -

# ##### 各种调试

bsdict = battery_status()
bsdict
bsdict['percentage']

bsdict = battery_status()
bsdict
bsdict['percentage']

import time
perlst = list()
while (bsdict := battery_status())['plugged'].upper() == 'PLUGGED_AC':
    perlst.insert(0, bsdict['percentage'])
    print(perlst)
    if bsdict['percentage'] == 100:
        break
    time.sleep(20)

# ### 启动微信发送图片

itchat.auto_login(hotReload=True)   #热启动你的微信

# + jupyter={"outputs_hidden": true}
#查看你的群
rooms=itchat.get_chatrooms(update=True)
for i in range(len(rooms[:2])):
    for key, value in rooms[i].items():
        print(f"{key}\t{value}")
    print('\n')   
# -

#这里输入你好友的名字或备注。
frd = itchat.search_friends(name=r'')  
print(frd)
username = frd['UserName']
print(username)
dbname = dirmainpath / 'data' / 'db' / 'wcdelay_白晔峰.db'
img = showdelayimg(dbname)
print(img)

print(img)
import os
imgrelatepath = os.path.relpath(img)
print(imgrelatepath)

imgwcdelay = 'img/webchat/wcdelay.png'
try:
    itchat.send_image(imgrelatepath,toUserName=username)  # 如果是其他文件可以直接send_file
    print("success")
except Exception as e:
    print(f"fail.{e}")


