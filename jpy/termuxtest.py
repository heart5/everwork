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
import pandas as pd
import time

import pathmagic
with pathmagic.context():
    from func.first import dirmainpath, touchfilepath2depth, getdirmain
    from life.wcdelay import showdelayimg
    from life.phonecontact import getphoneinfodb
    from func.pdtools import lststr2img
    from func.termuxtools import *
# -

# ### termuxtools各种功能函数

# 几乎都是硬件相关

# #### 粘贴板

termux_clipboard_get()

# #### 手机联系人

# ##### `showphoneinfoimg`函数

jujinm, ctdf = getphoneinfodb()
jujinm
ctdf

# +
ctdf.dtypes
ctdf.shape[0]
ctdf.groupby('appendtime').count().shape[0]
contactoutstr = f"目前联系人共有{ctdf.shape[0]}个，有效添加次数为：{ctdf.groupby('appendtime').count().shape[0]}，最近一次添加时间为：{ctdf['appendtime'].max()}。\n"
contactoutstr

dayrange = 30
descbegintime = pd.to_datetime(time.ctime()) + pd.Timedelta(f'-{dayrange}d')
descbegintime

contactoutstr += f"最近{dayrange}天添加的联系人如下(前20位）：\n"
ctrecentstr = ctdf[ctdf.appendtime > descbegintime][-20:].to_string(justify='left', show_dimensions=True, index=False)
contactoutstr += ctrecentstr
contactoutstr
# -

lststr2img(contactoutstr, title="手机联系人综合描述", showincell=True)

# ##### 联系人相关各种调试

ctstr = termux_contact_list()

type(ctstr)
type(eval(ctstr))
ctlst = eval(ctstr)
ctlst[:5]
ctlst[0].items()
ctlst[0].values()

# + jupyter={"outputs_hidden": true}
[value.replace(' ', '') for item in ctlst for value in item.values()]
# -

ctdf = pd.DataFrame(ctlst)
ctdf['number'] = ctdf['number'].apply(lambda x: x.replace(" ", ''))
ctdf['appendtime'] = time.time()
ctdf
ctdf['appendtime'].max()

ctdf.drop_duplicates('number')

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

from collections import Counter
namecounter = Counter(ctphonelst)
{key:value for key, value in namecounter.items() if value > 1}

# #### 电池

# ##### 【电池电量模块调用】

# +
import pandas as pd
import matplotlib.pyplot as plt

import pathmagic
with pathmagic.context():
    from etc.battery_manage import getbattinfodb, showbattinfoimg
    from func.first import touchfilepath2depth, getdirmain

dbnameouter = touchfilepath2depth(getdirmain() / "data" / "db" / f"batteryinfo.db")
# -

showbattinfoimg(dbnameouter)
# getbattinfodb(dbnameouter)

# ##### `showbattinfoimg`函数

jujinm, battinfodf = getbattinfodb(dbnameouter)
print(f"充电记录新鲜度：刚过去了{jujinm}分钟")
jingdu=300

# +
plt.figure(figsize=(36, 12), dpi=jingdu)
plt.style.use("ggplot")  # 使得作图自带色彩，这样不用费脑筋去考虑配色什么的；

def drawdelayimg(pos, timedfinner, title):
    # 画出左边界
    tmin = timedfinner.index.min()
    tmax = timedfinner.index.max()
    shicha = tmax - tmin
    bianjie = int(shicha.total_seconds() / 40)
    print(f"左边界：{bianjie}秒，也就是大约{int(bianjie / 60)}分钟")
    # plt.xlim(xmin=tmin-pd.Timedelta(f'{bianjie}s'))
    plt.subplot(pos)
    plt.xlim(xmin=tmin)
    plt.xlim(xmax=tmax + pd.Timedelta(f"{bianjie}s"))
    # plt.vlines(tmin, 0, int(timedf.max() / 2))
#     plt.vlines(tmax, 0, int(timedfinner.max() / 2))

    # 绘出主图和标题
    plt.scatter(timedfinner.index, timedfinner, s=timedfinner)
    plt.scatter(timedfinner[timedfinner == 0].index, timedfinner[timedfinner == 0], s=0.5)
    plt.title(title, fontsize=40)
    plt.tight_layout()

timedf = battinfodf['percentage']
drawdelayimg(321, timedf[timedf.index > timedf.index.max() + pd.Timedelta('-2d')], "电量%（最近两天）")
plt.ylim(0, 110)
drawdelayimg(312, timedf, "电量%（全部）")
plt.ylim(0, 110)
# imgwcdelaypath = touchfilepath2depth(getdirmain() / "img" / "hard" / "battinfo.png")

timedf = battinfodf['temperature']
drawdelayimg(322, timedf[timedf.index > timedf.index.max() + pd.Timedelta('-2d')], "温度℃（最近两天）")
# ax = plt.gca()
# ax.spines["bottom"].set_position(("data", 20))
plt.ylim(20, 40)
drawdelayimg(313, timedf, "温度℃（全部）")
plt.ylim(20, 40)
fig1 = plt.gcf()

imgwcdelaypath = touchfilepath2depth(getdirmain() / "img" / "hard" / "batttempinfo.png")
plt.show()
fig1.savefig(imgwcdelaypath, dpi=jingdu)
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


