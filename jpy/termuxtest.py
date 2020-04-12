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
import numpy as np
import sqlite3 as lite
import time

import pathmagic
with pathmagic.context():
    from func.first import dirmainpath, touchfilepath2depth, getdirmain
    from life.wcdelay import showdelayimg
    from life.phonecontact import getphoneinfodb, checkphoneinfotable
    from func.pdtools import lststr2img
    from func.sysfunc import sha2hexstr, set_timeout, after_timeout
    from func.termuxtools import *
    from func.litetools import droptablefromdb
    from func.configpr import getcfpoptionvalue, setcfpoptionvalue
# -

# ### 时间耗尽测试

# +
import datetime

dt1 = datetime.datetime.now()
# -

dt1
dt1.minute
dt1.second

None != 4


@set_timeout(6, after_timeout)
def runever():
    while 1:
        print("i am a ever...")
        time.sleep(2)


runever()

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

# #### 短信

# ##### 手机上短信数据入库

smslst = termux_sms_list(num=10000)

smsdf = pd.DataFrame(smslst)
smsdf

smsdf.groupby('type').count().index
smsdfclean = smsdf[smsdf.type != 'failed']

smsdf[smsdf.type == 'sent']

# +
import re
ptn = re.compile("^\+86")
smsdfclean['sent'] = smsdfclean['type'].apply(lambda x: True if x =='sent' else False)
smsdfclean['number'] = smsdfclean['number'].apply(lambda x: re.sub(ptn, '', x))


smsdfdone = smsdfclean[['sent', 'sender', 'number', 'received', 'body']]
smsdfdone['smsuuid'] = smsdfdone.apply(lambda x: sha2hexstr(list(x.values)), axis=1)
smsdfdone['type'] = 'sms'
smsdfdone.columns = ['sent', 'name', 'number', 'time', 'content', 'smsuuid', 'type']
# -

smsdfdone.sort_values('time', ascending=False)

smsdfdone

# ##### evernote中《SMS》笔记本中短信存档信息入库

# ###### 库准备

from bs4 import BeautifulSoup
import re
import random
import pandas as pd
import sqlite3 as lite
import pathmagic
with pathmagic.context():
    from func.evernttest import findnotefromnotebook, get_notestore, evernoteapijiayi
    from func.logme import log
    from func.nettools import trycounttimes2

# ###### 提取ini数据，用于对比

guidchuli = getcfpoptionvalue('everpim', "noteguid", 'noteguid')
len(guidchuli.split(','))

# ###### 获取笔记列表

notelst = findnotefromnotebook("25f718c1-cb76-47f6-bdd7-b7b5ee09e445", titlefind='李', notecount=10000)
len(notelst)

[item for item in notelst if item[1] == '李红亮']

ns = get_notestore()
testnum = 20
nstitle = ns.getNote(notelst[testnum][0], False, False, False, False)
nstitle.title
notecontent = ns.getNoteContent(notelst[testnum][0])


# ###### `splitcontentfromnote`函数

def splitcontentfromnote(noteguid: str):
    
    @trycounttimes2('evernote服务器')
    def gettitleandcontent(ntguid: str):
        ns = get_notestore()
        nttitle = ns.getNote(ntguid, False, False, False, False).title
        evernoteapijiayi()
        ntcontent = ns.getNoteContent(ntguid)
        evernoteapijiayi()
        
        return nttitle, ntcontent
    nstitle, notecontent = gettitleandcontent(noteguid)
    print(nstitle)
    nclines = BeautifulSoup(notecontent, 'lxml').find('en-note')
    print(nclines.text)
    validlines = [line for line in nclines.text.split("\n") if len(line) > 0]
    log.info(f"有内容的行共有：\t{len(validlines)}")
    yuefentuple = "(?:(?:January|February|March|April|May|June|July|August|September|October|November|December)|(?:Jan|Feb|Mar|Apr|Aug|Sept|Oct|Nov|Dec))"
    # yuefentuple = "(January|February|March|April|May|June|July|August|September|October|November|December)"
    ptntimestr = f"{yuefentuple}" + "\s\d{2}, \d{4} at \d{2}:\d{2}[AP]M"
    ptntime = re.compile(ptntimestr, re.M)
    
    # Phone call placed to 林常德 8613975648088 Call length: 19 seconds April 26, 2014 at 10:31PM
    # November 11, 2014 at 10:53AM，Phone call placed to 罗峰 13647208959 Call length: 37 seconds 
    # 先处理这个再进入所谓常规流程
    ncphonecall = [line.strip() for line in nclines.text.split("\n") if re.findall("(Phone call)", line)]
    if len(ncphonecall) > 0:
        phonecalllststr = "\n".join(ncphonecall)
        pcsplitlst = ncphonecall[0].split(f"\s*Phone call placed to ")
        print(pcsplitlst)
        descpc = ("", pcsplitlst[0])[re.findall(ptntime, pcsplitlst[0]) is None]
        print(f"Phone call desc is :\t{descpc}")
        pclst = [[pd.to_datetime(re.findall(ptntime, item)[0])] + [initem.strip() for initem in some[0]] for item in ncphonecall if (some := re.findall("(\w*)?\s?(\d+) Call length: (.+)", re.sub(ptntime, "", re.sub("\s*Phone call placed to ", "", item))))]
        # [[Timestamp('2014-09-14 09:21:00'), '余晗', '18008623925', '29 seconds']]
        # columns=['sender', 'time', 'number', 'body', 'type', 'sent']
        pcdone = [[item[1], item[0], item[2], item[3], "call", True] for item in pclst]
    else:
        descpc = ""
        pcdone = []
    log.info(f"可以被拆分成有效（Phone call）条目：\t{len(pcdone)}")
        
    ncnormal = [line.strip() for line in nclines.text.split("\n") if not re.findall("Phone call", line)]
#     print(ncnormal)
    
    splitcontent = [line.strip() for line in re.split(ptntime, "\n".join(ncnormal))]
    descnormal = splitcontent[0]
    splittime = [pd.to_datetime(line) for line in re.findall(ptntime, "\n".join(ncnormal))]
    log.info(f"可以被拆分成有效（非Phone call）条目：\t{len(splittime)}")
    ptnwenbiao = re.compile("\W*(?:发来短信|短信发出|电话打给|电话来自|错过来电)", re.M)
    wenbiaolst = [line for line in zip(splittime, splitcontent[1:]) if re.findall(ptnwenbiao, line[1])]
    log.info(f"其中用短语分隔的有：\t{len(wenbiaolst)}")
    wenbiaobody = [([line[0]] + (re.split(ptnwenbiao, line[1].strip("， ,")))) for line in wenbiaolst]
    wenbiaotype = [re.findall(ptnwenbiao, line[1])[0].strip("， ,") for line in wenbiaolst]
    
    def detecttype(instr: str):
        if instr == '发来短信':
            return ['sms', False]
        elif instr == "短信发出":
            return ['sms', True]
        elif instr == "电话来自":
            return ['call', False]
        elif instr == "电话打给":
            return ['call', True]
        elif instr == "错过来电":
            return ['call', False]

    wenbiaotypesplit = [detecttype(line) for line in wenbiaotype]
    wenbiaoall = [[nstitle] +line[0] + list(line[1]) for line in zip(wenbiaobody, wenbiaotypesplit)]
    wenbiaosms = [line for line in wenbiaoall if line[-2] == 'sms']
    wenbiaocall = [line for line in wenbiaoall if line[-2] == 'call']
    print(wenbiaocall[:3])
    wenbiaocallformat = [[line[0], line[1], re.findall("\d+", line[3])[0], re.sub("^([\w\(\)（）]+\s\d+，?)", "", line[3]), line[4], line[5]] for line in wenbiaocall]
    wenbiaodone = wenbiaosms + wenbiaocallformat
    
    fubiaolst = [line for line in zip(splittime, splitcontent[1:]) if not re.findall(ptnwenbiao, line[1])]
    print(fubiaolst[:3])
    log.info(f"其中用符号分隔的有：\t{len(fubiaolst)}")
    fubiaothree = [[line[0]] + line[1].rsplit('，', 1) for line in fubiaolst]
#     print(fubiaothree)
    fubiaofinal = [[nstitle, pd.to_datetime(line[0]), line[2].split("||| ")[1], line[1].strip("："), "sms", False] for line in fubiaothree]

    def normalname(nameold, number, content):
        if nameold == "Mailed in note":
            return number
        ptnname = re.compile("(?:【(\w+)】$|^【(\w+)】|\[(\w+)\]$|^\[(\w+)\])")
        tiqu = [[x for x in item if len(x) > 0][0] for item in re.findall(ptnname, content) if (rst :=re.findall(ptnname, content) and len(item) > 0)]
        if content.startswith("【"):
            print(nameold, number, content)
            print(tiqu)
        if len(tiqu) == 0:
            return nameold
        else:
            return tiqu[-1]
    alllst = pcdone + wenbiaodone + fubiaofinal
    alldone = [[normalname(item[0], item[2], item[3]), item[1], item[2], item[3], item[4], item[5]] for item in alllst]
    smsnotedf = pd.DataFrame(alldone, columns=['name', 'time', 'number', 'content', 'type', 'sent'])
    smsnotedf['smsuuid'] = smsnotedf[['sent', 'name', 'number', 'time', 'content']].apply(lambda x: sha2hexstr(list(x.values)), axis=1)
    
    return [nstitle, descpc + descnormal], smsnotedf[['sent', 'name', 'number', 'time', 'content', 'smsuuid', 'type']].sort_values('time', ascending=False)


# ###### 【方括号中联系人规范名称的提取】

# + [markdown] jupyter={"source_hidden": true}
# **不够智能，有错误提取，暂存后决**

# + jupyter={"source_hidden": true}
def normalname(nameold, number, content):
    if nameold == "Mailed in note":
        return number
    ptnname = re.compile("(?:【(\w+)】$|^【(\w+)】)")
    tiqu = [[x for x in item if len(x) > 0][0] for item in re.findall(ptnname, content) if (rst :=re.findall(ptnname, content) and len(item) > 0)]
    if len(tiqu) == 0:
        return nameold
    else:
        return tiqu[0]


# + jupyter={"source_hidden": true, "outputs_hidden": true}
teststr1 = "【中国平安】平安金管家APP“VIP服务”专区恭候亲使用积分权益兑换服务，火速登陆看看吧！详询您的VIP服务专员。"
teststr1 = "【招联金融】您的18941.96元借款已发放到尾号9929的招商银行卡，请注意查收。"
teststr2 = "亲爱的平安VIP俱乐部会员白晔峰，您当前VIP层级为黄金，会籍期为2016年10月26日至2017年10月25日，VIP专属积分余量为80000分，积分有效期与会籍期一致。平安金管家APP“VIP服务”专区恭候亲使用积分权益兑换服务，火速登陆看看吧！详询您的VIP服务专员。【中国平安】"
teststr3 = "亲爱的平安VIP俱乐部会员白晔峰【中国平安】会籍期为2016年10月26日至2017年10月25日"
# ptnname = re.compile("(?:【(\w+)】$|^【(\w+)】|【(\w+)】)")
ptnname = re.compile("(?:【(\w+)】$|^【(\w+)】)")
re.findall(ptnname, teststr1)
[[x for x in item if len(x) > 0][0] for item in re.findall(ptnname, teststr2) if (rst :=re.findall(ptnname, teststr2) and len(item) > 0)]

# + jupyter={"source_hidden": true, "outputs_hidden": true}
normalname('Mailed in note', 95559, teststr1)
# -

# ###### 罗峰

desc, pimdf = splitcontentfromnote("bf147a41-8c18-4531-8e19-5053102b028c")
desc
pimdf

# ###### 李红亮

desc, pimdf = splitcontentfromnote("ae2b34ab-f2a1-4703-9155-bd28b1d7d743")
desc
pimdf

# ###### 调试Phone call类记录

desc, pimdf = splitcontentfromnote("352e3f93-0027-425b-8daf-444ceade42d3")

# +
phonecalllst = ['鄂AZJ785，福克斯夫人：左洁，女儿：小金果Phone call placed to 余晗 18008623925 Call length: 29 seconds September 14, 2014 at 09:21AM']
phonecalllststr = "".join(phonecalllst)
phonecalllststr.split("Phone call placed to ")[0]

yuefentuple = "(?:(?:January|February|March|April|May|June|July|August|September|October|November|December)|(?:Jan|Feb|Mar|Apr|Aug|Sept|Oct|Nov|Dec))"
# yuefentuple = "(January|February|March|April|May|June|July|August|September|October|November|December)"
ptnstr = f"{yuefentuple}" + "\s\d{2}, \d{4} at \d{2}:\d{2}[AP]M"
ptn = re.compile(ptnstr, re.M)
# pclst = [(re.findall(ptn, item)) + re.findall("(\w*)?\s?(\d+) Call length: (.+)\s", re.sub(ptn, "", item)) for item in phonecalllststr.split("Phone call placed to ")[1:]]
# pclst = [(re.findall(ptn, item)) + [some[0][0], some[0][1], some[0][2]] for item in phonecalllststr.split("Phone call placed to ")[1:] if (some := re.findall("(\w*)?\s?(\d+) Call length: (.+)\s", re.sub(ptn, "", item)))]
# pclst = [(re.findall(ptn, item)) + [initem for initem in some[0]] for item in phonecalllststr.split("Phone call placed to ")[1:] if (some := re.findall("(\w*)?\s?(\d+) Call length: (.+)\s", re.sub(ptn, "", item)))]
pclst = [[pd.to_datetime(re.findall(ptn, item)[0])] + [initem for initem in some[0]] for item in phonecalllststr.split("Phone call placed to ")[1:] if (some := re.findall("(\w*)?\s?(\d+) Call length: (.+)\s", re.sub(ptn, "", item)))]

pclst
# -

# ###### 随机抽取笔记展示结果

testnum = random.randrange(0, len(notelst))
# testnum = 1
desc, rstdf = splitcontentfromnote(notelst[testnum][0])
# rstdf[rstdf.type == 'call'].iloc[-50:]
# rstdf.iloc[-50:]
desc
rstdf
rstdf.iloc[0, 4]

# ###### 调试日期开头的通讯记录，分为文字短语和冒号两种

# notecontent
nclxml = BeautifulSoup(notecontent, 'lxml')
# nclxml
# nclxmlreplaced = nclxmlstr.replace("<div><br/></div>", "\n")
nclines = nclxml.find('en-note')
# nclines.text
# nclines.split("\n")
validlines = [line for line in nclines.text.split("\n") if len(line) > 0]
# validlines[:25]
yuefentuple = "(?:(?:January|February|March|April|May|June|July|August|September|October|November|December)|(?:Jan|Feb|Mar|Apr|Aug|Sept|Oct|Nov|Dec))"
# yuefentuple = "(January|February|March|April|May|June|July|August|September|October|November|December)"
ptnstr = f"{yuefentuple}" + "\s\d{2}, \d{4} at \d{2}:\d{2}[AP]M"
print(ptnstr)
ptn = re.compile(ptnstr, re.M)
splitcontent = [line.strip() for line in re.split(ptn, nclines.text)]
len(splitcontent)
splittime = [pd.to_datetime(line) for line in re.findall(ptn, nclines.text)]
len(splittime)
wenbiaolst = [line for line in zip(splittime, splitcontent[1:]) if re.findall("发来短信|短信发出|电话打给|电话来自", line[1])]
len(wenbiaolst)
wenbiaolst[:2]
wenbiaobody = [([line[0]] + (re.split("\W*(?:发来短信|短信发出|电话打给|电话来自)\W", line[1].strip("， ,")))) for line in wenbiaolst]
len(wenbiaobody)
wenbiaobody[:5]
wenbiaotype = [re.findall("\W*(?:发来短信|短信发出|电话打给|电话来自)\W", line[1])[0].strip("， ,") for line in wenbiaolst]
len(wenbiaotype)
wenbiaotype[:5]
def detecttype(instr: str):
    if instr == '发来短信':
        return ['sms', False]
    elif instr == "短信发出":
        return ['sms', True]
    elif instr == "电话来自":
        return ['call', False]
    elif instr == "电话打给":
        return ['call', True]
wenbiaotypesplit = [detecttype(line) for line in wenbiaotype]
wenbiaoall = [[nstitle.title] +line[0] + list(line[1]) for line in zip(wenbiaobody, wenbiaotypesplit)]
wenbiaosms = [line for line in wenbiaoall if line[-2] == 'sms']
wenbiaosms[:1]
wenbiaocall = [line for line in wenbiaoall if line[-2] == 'call']
# wenbiaocall[:5]
wenbiaocallformat = [[line[0], line[1], line[3].split("，")[0].split(" ")[1], re.findall("\d+", line[3])[-1], line[4], line[5]] for line in wenbiaocall]
# wenbiaocallformat
wenbiaodone = wenbiaosms + wenbiaocallformat
len(wenbiaodone)
# wenbiaodone[-20:]

fubiaolst = [line for line in zip(splittime, splitcontent[1:]) if not re.findall("发来短信|短信发出|电话打给|电话来自", line[1])]
len(fubiaolst)
fubiaolst[:2]

fubiaothree = [[line[0]] + line[1].rsplit('，', 1) for line in fubiaolst]
fubiaothree[:2]
fubiaofinal = [[nstitle.title, pd.to_datetime(line[0]), line[2].split("||| ")[1], line[1].strip("："), "sms", False] for line in fubiaothree]
fubiaofinal[:5]

divstr = '<div>November 28, 2014 at 09:34PM，95555，<b>发来短信</b> 您尾号8256的信用卡28日21:34消费人民币437.00元。送你99积分，马上领 t.cn/8s52qAr 。[招商银行]<div><br/></div>December 01, 2014 at 06:47PM，95555，<b>发来短信</b> 【代扣查询】截至12月01日，您的缴费号码0904843679 总计欠费0元，如疑请询95555。[招商银行]<div><br/></div>December 01, 2014 at 08:36PM，95555，<b>发来短信</b> 【代扣查询】截至12月01日，您的缴费号码6626515632 总计欠费0元，如疑请询95555。[招商银行]<div><br/></div>December 04, 2014 at 02:29PM，95555，<b>发来短信</b> 白晔峰先生，您个人信用卡临时额度后天失效，2014年12月05日09点前回#YLEY可重新申请临额至66000元，短信回复为准。巧用额度理财，猛戳 t.cn/8FdmPg8 查询[招商银行]<div><br/></div>December 04, 2014 at 02:35PM，95555，<b>短信发出</b> #yley<div><br/></div>December 04, 2014 at 02:36PM，95555，<b>发来短信</b> 白晔峰先生，您个人信用卡账户临额调整成功，该账户临额66000元，有效期至2015年03月03日，当前可用额度为32281元，超出信用额度使用的款项将计入最低还款额。巧用额度理财，猛戳 t.cn/8FdmPg8 查询[招商银行]</div><br clear="none"/>'

divhtml = BeautifulSoup(divstr, 'lxml')
divhtml.div

[line for line in validlines if not re.findall("(电话(来自|打给)|(错过来电))", line)]

testitem = 'December 26, 2014 at 03:22PM，电话来自 徐志伟 13207166125，时长 61 秒'
testitem.split("，", 3)

# ###### 【删除类型为call的纪录】

tablename = "sms"
dbname = touchfilepath2depth(getdirmain() / "data" / "db" / "phonecontact.db")
conn = lite.connect(dbname)
sqldel = f"delete from {tablename} where type=\'call\'"
print(sqldel)
cursor = conn.cursor()
cursor.execute(sqldel)
conn.close()


# ##### 联系人信息查询

def showinfostream(keyin:str):
    print(keyin)
    dbname = touchfilepath2depth(getdirmain() / "data" / "db" / "phonecontact.db")
    tablename="sms"
    checkphoneinfotable(dbname)

    conn = lite.connect(dbname)
    recordctdf = pd.read_sql(f"select * from {tablename} where (number like \'%{keyin}%\') or (name like \'%{keyin}%\')", con=conn)
    conn.close()
    return recordctdf


ctdf = showinfostream("黄兆钢")
ctdf.dtypes
ctdf

ctdf[ctdf['number'].str.contains("6").notnull()]

showinfostream("8881")

# ##### 【删除sms数据表，为重构做准备】

dbname = touchfilepath2depth(getdirmain() / "data" / "db" / "phonecontact.db")
tablename="sms"
droptablefromdb(dbname, tablename, confirm=True)

# #### 提醒消息列表

termux_notification()

# #### 电话信息

termux_telephony_cellinfo()

termux_telephony_deviceinfo()

termuxinfostr = termux_info()

print(termuxinfostr)

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
    
    plt.tick_params(labelsize=20)
#     fontlabel = {'size' : 20}
#     plt.xlabel("时间", fontlabel)
#     plt.xlabel(font=fontlabel)
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


