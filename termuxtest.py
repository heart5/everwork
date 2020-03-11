t -*- coding: utf-8 -*-
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

import os
import itchat
from life.wcdelay import showdelayimg

itchat.auto_login(hotReload=True)   #热启动你的微信

#查看你的群
rooms=itchat.get_chatrooms(update=True)
gor i in range(len(rooms[:2])):
    for key, value in rooms[i].items():
        print(f"{key}\t{value}")
    print('\n')   

#这里输入你好友的名字或备注。
frd = itchat.search_friends(name=r'')  
print(frd)
username = frd['UserName']
print(username)
img = showdelayimg()
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
