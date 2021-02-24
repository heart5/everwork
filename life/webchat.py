# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     formats: ipynb,py
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.10.1
# ---

"""
微信大观园，工作优先，娱乐生活
"""

import time
import datetime
import re
import os
import sys
import math
import itchat
import itchat.storage
from itchat.content import *
from bs4 import BeautifulSoup

import pathmagic

with pathmagic.context():
    from func.first import touchfilepath2depth, getdirmain, dirmainpath
    from func.configpr import getcfpoptionvalue, setcfpoptionvalue
    from func.logme import log
    from func.nettools import trycounttimes2
    from func.sysfunc import uuid3hexstr, not_IPython
    from func.evernttest import get_notestore, makenote, imglist2note, \
        evernoteapijiayi, getinivaluefromnote
    from func.datatools import readfromtxt, write2txt
    from func.termuxtools import termux_sms_send
    # from work.weixinzhang import showjinzhang, showshoukuan
    import evernote.edam.type.ttypes as ttypes
    from work.zymessage import searchcustomer, searchqiankuan, searchpinxiang
    from etc.getid import getdeviceid
    from muse.majjianghuojie import updateurllst, splitmjurlfromtext, zhanjidesc, showzhanjiimg
    from life.wcdelay import inserttimeitem2db, showdelayimg
    from life.wccontact import updatectdf, getctdf, showwcsimply
    from life.phonecontact import showphoneinfoimg
    from etc.battery_manage import showbattinfoimg
    from func.pdtools import db2img, lststr2img


def newchatnote():
    global note_store
    # parentnotebook = \
    # note_store.getNotebook('4524187f-c131-4d7d-b6cc-a1af20474a7f')
    parentnotebook = \
        note_store.getNotebook(getinivaluefromnote(
            'notebookguid', 'notification'))
    evernoteapijiayi()
    note = ttypes.Note()
    note.title = f"微信（{getowner()['User']['NickName']}）记录:" \
                 f"{time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime(time.time()))}"
    print(note.title)
    token = getcfpoptionvalue('everwork', 'evernote', 'token')
    notechat = makenote(token, note_store, note.title, notebody='',
                        parentnotebook=parentnotebook)

    return notechat


@trycounttimes2('微信服务器')
def get_response(msg):
    txt = msg['Text']
    # print(msg)
    return txt


def showmsg(msg):
    # print(msg)
    for item in msg:
        # print(item)
        # if item.lower().find('name') < 0:
        # continue
        print(f'{item}\t{type(msg[item])}', end='\t')
        if type(msg[item]) in [dict, itchat.storage.templates.Chatroom,
                               itchat.storage.templates.User]:
            print(len(msg[item]))
            for child in msg[item]:
                childmsg = msg[item][child]
                print(f'\t{child}\t{type(childmsg)}', end='\t')
                if type(childmsg) in [dict, itchat.storage.templates.User,
                                      itchat.storage.templates.ContactList]:
                    lenchildmsg = len(childmsg)
                    print(lenchildmsg)
                    lmt = getinivaluefromnote('webchat', 'itemshowinmsg')
                    shownum = lmt if lenchildmsg > lmt else lenchildmsg
                    print(f'\t\t{childmsg[:shownum]}')
                    # print(f'\t\t{childmsg}')
                else:
                    print(f'\t\t{childmsg}')

        else:
            print(msg[item])


def formatmsg(msg):
    timetuple = time.localtime(msg['CreateTime'])
    timestr = time.strftime("%Y-%m-%d %H:%M:%S", timetuple)
    # print(msg['CreateTime'], timetuple, timestr)
    men_wc = getcfpoptionvalue('everwebchat', get_host_uuid(), 'host_nickname')
    dbname = touchfilepath2depth(getdirmain() / "data" / "db" /
                                 f"wcdelay_{men_wc}.db")
    inserttimeitem2db(dbname, msg['CreateTime'])
    # owner = itchat.web_init()
    meu_wc = getcfpoptionvalue('everwebchat', get_host_uuid(), 'host_username')
    send = (msg['FromUserName'] == meu_wc)
    if 'NickName' in msg["User"].keys():
        showname = msg['User']['NickName']
        if len(msg['User']['RemarkName']) > 0:
            showname = msg['User']['RemarkName']
    elif 'UserName' in msg['User'].keys():
        showname = msg['User']['UserName']
    elif 'userName' in msg['User'].keys():
        showname = msg['User']['userName']
    else:
        showname = ""
        log.warning(f"NickName或者UserName或者userName键值不存在哦")
        showmsg(msg)

    # 过滤掉已经研究过属性公众号信息，对于尚未研究过的显示详细信息
    ignoredmplist = getinivaluefromnote('webchat', 'ignoredmplist')
    imlst = re.split('[，,]', ignoredmplist)
    ismp = type(msg['User']) == itchat.storage.MassivePlatform
    if ismp and (showname not in imlst):
        showmsg(msg)
        print(f"{showname}\t{imlst}")

    if type(msg['User']) == itchat.storage.templates.Chatroom:
        isfrom = msg['FromUserName'].startswith('@@')
        isto = msg['ToUserName'].startswith('@@')
        # qunmp = isfrom or isto
        # showmsg(msg)
        if isfrom:
            # print(f"（群)\t{msg['ActualNickName']}", end='')
            showname += f"(群){msg['ActualNickName']}"
        elif isto:
            # print(f"（群）\t{msg['User']['Self']['NickName']}", end='')
            showname += f"(群){msg['User']['Self']['NickName']}"
        # print(f"\t{msg['Type']}\t{msg['MsgType']}\t{msg['Text']}")
        # print(f"\t{send}\t{msg['Type']}\t{msg['Text']}")
    fmtext = msg['Text']

    finnalmsg = {'fmId': msg['MsgId'], 'fmTime': timestr, 'fmSend': send,
                 'fmSender': showname, 'fmType': msg['Type'], 'fmText': fmtext}

    return finnalmsg


def getsendernick(msg):
    # sendernick = itchat.search_friends(userName=msg['FromUserName'])
    if msg['FromUserName'].startswith('@@'):
        qun = itchat.search_chatrooms(userName=msg['FromUserName'])
        sendernick = qun['NickName'] + '(群)' + msg['ActualNickName']
    else:
        senderuser = itchat.search_friends(userName=msg['FromUserName'])
        if senderuser is None:
            return "self?"
        if len(senderuser['RemarkName']) == 0:
            sendernick = senderuser['NickName']
        else:
            sendernick = senderuser['RemarkName']
    # sendernick = itchat.search_friends(userName=msg['FromUserName'])['NickName']
    return sendernick


def showfmmsg(inputformatmsg):
    msgcontent = ""
    for item in inputformatmsg:
        if item == "fmId":
            continue
        msgcontent += f"{inputformatmsg[item]}\t"
    msgcontent = msgcontent[:-1]
    print(f"{msgcontent}")

    men_wc = getcfpoptionvalue('everwebchat', get_host_uuid(), 'host_nickname')
    chattxtfilename = str(getdirmain() / 'data' / 'webchat' /
                          f'chatitems({men_wc}).txt')
    chatitems = readfromtxt(chattxtfilename)
    global note_store
    # webchats.append(chatmsg)
    chatitems.insert(0, msgcontent)
    write2txt(chattxtfilename, chatitems)

    # if inputformatmsg['fmText'].startswith('收到转账'):
    # showjinzhang()

    # if inputformatmsg['fmText'].startswith('微信支付收款'):
    # showshoukuan()

    # readinifromnote()
    # cfpfromnote, cfpfromnotepath = getcfp('everinifromnote')
    if len(men_wc) ==0 :
        log.critical(f"登录名为空！！！")
        return
    if (chatnoteguid := getinivaluefromnote('webchat', men_wc+f"_{getdeviceid()}").lower()) is None:
        chatnoteguid = getinivaluefromnote('webchat', men_wc).lower()
    updatefre = getinivaluefromnote('webchat', 'updatefre')
    showitemscount = getinivaluefromnote('webchat', 'showitems')
    # print(f"{type(showitemscount)}\t{showitemscount}")
    neirong = "\n".join(chatitems[:showitemscount])
    neirongplain = neirong.replace('<', '《').replace('>', '》') \
        .replace('=', '等于').replace('&', '并或')
    if (len(chatitems) % updatefre) == 0:
        neirongplain = "<pre>" + neirongplain + "</pre>"
        imglist2note(note_store, [], chatnoteguid, f"微信（{men_wc}）_（{getinivaluefromnote('device', getdeviceid())}）记录更新笔记",
                     neirongplain)
    # print(webchats)


@itchat.msg_register([CARD, FRIENDS], isFriendChat=True, isGroupChat=True,
                     isMpChat=True)
def tuling_reply(msg):
    # showmsg(msg)
    showfmmsg(formatmsg(msg))


@itchat.msg_register([NOTE], isFriendChat=True, isGroupChat=True, isMpChat=True)
def note_reply(msg):
    # showmsg(msg)
    innermsg = formatmsg(msg)
    if msg["FileName"] == "微信转账":
        ptn = re.compile("<pay_memo><!\\[CDATA\\[(.*)\\]\\]></pay_memo>")
        pay = re.search(ptn, msg["Content"])[1]
        innermsg['fmText'] = innermsg['fmText'] + f"[{pay}]"
    if msg["FileName"].find('红包') >= 0:
        showmsg(msg)
    showfmmsg(innermsg)


@itchat.msg_register([MAP], isFriendChat=True, isGroupChat=True, isMpChat=True)
def map_reply(msg):
    # showmsg(msg)
    innermsg = formatmsg(msg)
    gps = msg['Url'].split('=')[1]
    # print(f"[{gps}]")
    innermsg['fmText'] = innermsg['fmText'] + f"[{gps}]"
    showfmmsg(innermsg)


@itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO],
                     isFriendChat=True, isGroupChat=True, isMpChat=True)
def fileetc_reply(msg):
    innermsg = formatmsg(msg)
    createtimestr = time.strftime("%Y%m%d", time.localtime(msg['CreateTime']))
    filepath = getdirmain() / "img" / "webchat" / createtimestr
    filepath = filepath / f"{innermsg['fmSender']}_{msg['FileName']}"
    touchfilepath2depth(filepath)
    log.info(f"保存{innermsg['fmType']}类型文件：\t{str(filepath)}")
    msg['Text'](str(filepath))
    innermsg['fmText'] = str(filepath)

    showfmmsg(innermsg)


def soupclean2item(msgcontent):
    rpcontent = msgcontent.replace('<![CDATA[', '').replace(']]>', '')
    soup = BeautifulSoup(rpcontent, 'lxml')
    category = soup.category
    if category:
        items = category.find_all('item')
        if not items:
            items = []
    else:
        items = []

    return soup, items


@itchat.msg_register([SHARING], isFriendChat=True, isGroupChat=True, isMpChat=True)
def sharing_reply(msg):
    sendernick = getsendernick(msg)
    innermsg = formatmsg(msg)

    # showmsg(msg)
    # 处理火界麻将战绩网页
    # http://zj.lgmob.com/h5_whmj_qp/fks0_eb81c193dea882941fe13dfa5be24a11.html
    # ptn = re.compile("h5_whmj_qp/fks0_")
    # http://s0.lgmob.com/h5_whmj_qp/zhanji/index.php?id=fks0_eb81c193dea882941fe13dfa5be24a11
    # ptn = re.compile("h5_whmj_qp/zhanji/index.php\\?id=")
    men_wc = getcfpoptionvalue('everwebchat', get_host_uuid(), 'host_nickname')
    msgurl = msg['Url']
    print(msgurl)
    if (ulst := splitmjurlfromtext(msgurl)) and (len(ulst) > 0):
        roomid = updateurllst(men_wc, ulst)
        outstr = f"【Sharing】信息中发现新的火界麻将战绩网页链接：\t{roomid}"
        # log.info(outstr)
        itchat.send_msg(f'({sendernick})'  +outstr)
        makemsg2write(innermsg, outstr)
        makemsg2write(innermsg, msgurl)

    # 处理开房链接
    # http://s0.lgmob.com/h5_whmj_qp/?d=217426
    ptnfang = re.compile("s0.lgmob.com/h5_whmj_qp/\\?d=(\d+)")
    if re.findall(ptnfang, msgurl):
        if msgurl.startswith('http'):
            outstr = f"【Sharing】信息中发现新的火界麻将开房链接：\t{re.findall(ptnfang, msgurl)[0]}: {msg['Text']}"
            # log.info(outstr)
            itchat.send_msg(f'({sendernick})'  +outstr)
            makemsg2write(innermsg, outstr)

    soup, items = soupclean2item(msg['Content'])

    # 过滤掉已经研究过属性公众号信息，对于尚未研究过的显示详细信息
    impimlst = re.split('[，,]', getinivaluefromnote('webchat', 'impmplist'))

    cleansender = re.split("\\(群\\)", innermsg['fmSender'])[0]

    if cleansender in impimlst:
        if cleansender == '微信支付' and innermsg["fmText"].endswith("转账收款汇总通知"):
            itms = soup.opitems.find_all('opitem')
            userfre = [f'{x.weapp_username.string}\t{x.hint_word.string}' for x in itms if x.word.string.find(
                '收款记录') >= 0][0]
            innermsg['fmText'] = innermsg['fmText'] + f"[{soup.des.string}\n[{userfre}]]"
        # elif innermsg["fmText"].endswith("微信支付凭证"):
        # innermsg['fmText'] = innermsg['fmText']+f"[{soup.des.string}]"
        elif cleansender == '微信运动' and innermsg["fmText"].endswith("刚刚赞了你"):
            innermsg['fmText'] = innermsg['fmText'] + \
                                 f"[{soup.rankid.string}\t{soup.displayusername.string}]"
        elif cleansender == '微信运动' and innermsg["fmText"].endswith("排行榜冠军"):
            ydlst = []
            mni = soup.messagenodeinfo
            minestr = f"heart57479\t{mni.rankinfo.rankid.string}\t{mni.rankinfo.rank.rankdisplay.string}"
            ydlst.append(minestr)
            ril = soup.rankinfolist.find_all('rankinfo')
            for item in ril:
                istr = f"{item.username.string}\t{item.rank.rankdisplay.string}\t{item.score.scoredisplay.string}"
                ydlst.append(istr)
            pay = "\n".join(ydlst)
            innermsg['fmText'] = innermsg['fmText'] + f"[{pay}]"
        elif soup.des or soup.digest:
            valuepart = soup.des or soup.digest
            innermsg['fmText'] = innermsg['fmText'] + f"[{valuepart.string}]"
        else:
            showmsg(msg)
    elif len(items) > 0:
        itemstr = '\n'
        for item in items:
            itemstr += item.title.string + '\n'
        # 去掉尾行的回车
        itemstr = itemstr[:-1]
        innermsg['fmText'] = innermsg['fmText'] + itemstr
    elif type(msg['User']) == itchat.storage.MassivePlatform:
        log.info(f"公众号信息\t{msg['User']}")
        showmsg(msg)

    showfmmsg(innermsg)


def makemsg2write(innermsg, inputtext=''):
    """
    make record then write to items for chatitems
    """
    nowtuple = time.time()
    nowdatetime = datetime.datetime.fromtimestamp(nowtuple)
    finnalmsg = {'fmId': math.floor(nowtuple),
                 'fmTime': nowdatetime.strftime("%Y-%m-%d %H:%M:%S"),
                 'fmSend': True, 'fmSender': innermsg['fmSender'],
                 'fmType': 'Text',
                 'fmText': f"{inputtext}"
                }
    showfmmsg(finnalmsg)


@itchat.msg_register([TEXT], isFriendChat=True, isGroupChat=True, isMpChat=True)
def text_reply(msg):
    sendernick = getsendernick(msg)
    innermsg = formatmsg(msg)
    soup, items = soupclean2item(msg['Content'])

    # 是否在清单中
    mp4txtlist = re.split('[，,]', getinivaluefromnote('webchat', 'mp4txtlist'))
    cleansender = re.split("\\(群\\)", innermsg['fmSender'])[0]
    if cleansender in mp4txtlist:
        itemstr = '\n'
        for item in items:
            itemstr += item.title.string + '\n'
        # 去掉尾行的回车
        itemstr = itemstr[:-1]
        innermsg['fmText'] = itemstr

    showfmmsg(innermsg)

    # 特定指令则退出
    if msg['Text'] == '退出小元宝系统':
        log.info(f"根据指令退出小元宝系统")
        itchat.logout()

    # 如何不是指定的数据分析中心，则不进行语义分析
    thisid = getdeviceid()
    # print(f"type:{type(thisid)}\t{thisid}")
    houseid = getinivaluefromnote('webchat', 'datahouse')
    # print(f"type:{type(houseid)}\t{houseid}")
    if thisid != str(houseid):
        print(f"不是数据分析中心，咱不管哦")
        return

    # 处理火界麻将战绩网页
    men_wc = getcfpoptionvalue('everwebchat', get_host_uuid(), 'host_nickname')
    ptn = re.compile("h5_whmj_qp/(zhanji/index.php\\?id=|fks0_)")
    msgtxt = msg['Text']
    if (ulst := splitmjurlfromtext(msgurl)) and (len(ulst) > 0):
        descstr = updateurllst(men_wc, ulst)
        outstr = f"【Text】信息中发现新的火界麻将战绩网页链接并处理：\t{descstr}"
        # log.info(outstr)
        itchat.send_msg(sendernick + outstr)
        makemsg2write(innermsg, outstr)
        makemsg2write(innermsg, msgtxt)

    # 根据口令显示火界麻将战绩综合统计结果
    if msg['Text'].startswith('火界麻将战果统计') or msg['Text'].startswith('麻果'):
        log.info(f"根据口令显示火界麻将战绩综合统计结果")
        msgtxt = msg['Text']
        recentday = ""
        if msgtxt.find('日') != -1:
            recentday = "日"
        elif msgtxt.find('周') != -1:
            recentday = "周"
        elif msgtxt.find('旬') != -1:
            recentday = "旬"
        elif msgtxt.find('月') != -1:
            recentday = "月"
        elif msgtxt.find('年') != -1:
            recentday = "年"
        elif msgtxt.find('全部') != -1:
            recentday = "全部"
        else:
            recentday = '周'

        simpledesc = True
        if msgtxt.find('综合') != -1:
            simpledesc = False
        zhanji = zhanjidesc(men_wc, recentday, simpledesc)
        # 发回给查询者
#         itchat.send_msg(f"{zhanji}", toUserName=msg['FromUserName'])
#         makemsg2write(innermsg, zhanji)
        imgzhanji = lststr2img(zhanji)
        imgwcrel = os.path.relpath(imgzhanji)
        itchat.send_image(imgwcrel, toUserName=msg['FromUserName'])
        makemsg2write(innermsg, imgwcrel)
        outstr = f"{sendernick}\t查询信息：\n{msgtxt}"
        # 查询记录发给自己一份备档
        itchat.send_msg(outstr)
        makemsg2write(innermsg, outstr)

        if msgtxt.find('折线图') != -1:
            imgzhanji = showzhanjiimg(men_wc, recentday)
            imgzhanjirel = os.path.relpath(imgzhanji)
            itchat.send_image(imgzhanjirel, toUserName=msg['FromUserName'])
            # 折线图发送记录备档
            makemsg2write(innermsg, imgzhanjirel)

    if msg['Text'].find('真元信使') >= 0:
        qrylst = msg['Text'].split('\n')
        # 去除某行首位空格
        qrylst = [x.strip() for x in qrylst]
        # 去掉空行
        qrylst = [x.strip() for x in qrylst if len(x.strip()) != 0]
        print(f"{qrylst}")
        diyihang = qrylst[0].split()
        if diyihang[0].strip() == '真元信使':
            if len(diyihang) == 1:
                if (len(qrylst) == 1) or (qrylst[1].strip == ''):
                    rstfile, rst = searchcustomer()
                else:
                    qrystr = qrylst[1].strip()
                    rstfile, rst = searchcustomer(qrystr.split())
            elif diyihang[1] == '延时图':
                delaydbname = getdirmain() / 'data' / 'db' / f"wcdelay_{men_wc}.db"
                imgwcdelay = showdelayimg(delaydbname)
                imgwcdelayrel = os.path.relpath(imgwcdelay)
                itchat.send_image(imgwcdelayrel, toUserName=msg['FromUserName'])
                makemsg2write(innermsg, imgwcdelayrel)
                # 延时图发送记录备档
                return
            elif diyihang[1] == '电量图':
                delaydbname = touchfilepath2depth(getdirmain() / "data" / "db" / f"batteryinfo.db")
                imgbattinfo = showbattinfoimg(delaydbname)
                imgbattinforel = os.path.relpath(imgbattinfo)
                itchat.send_image(imgbattinforel, toUserName=msg['FromUserName'])
                makemsg2write(innermsg, imgbattinforel)
                # 延时图发送记录备档
                return
            elif diyihang[1] == '联系人':
                contactinfo = showphoneinfoimg()
                imgcontactinforel = os.path.relpath(contactinfo)
                itchat.send_image(imgcontactinforel, toUserName=msg['FromUserName'])
                makemsg2write(innermsg, imgcontactinforel)
                # 延时图发送记录备档
                return
            elif diyihang[1] == '连更':
                updatectdf()
                return
            elif diyihang[1] == '连显':
                frddfread = getctdf()
                imgwc = db2img(showwcsimply(frddfread))
                imgwcrel = os.path.relpath(imgwc)
                itchat.send_image(imgwcrel, toUserName=msg['FromUserName'])
                makemsg2write(innermsg, imgwcrel)
                return
            elif diyihang[1] == '欠款':
                qrystr = qrylst[1].strip()
                rstfile, rst = searchqiankuan(qrystr.split())
            elif diyihang[1] == '品项':
                qrystr = qrylst[1].strip()
                rstfile, rst = searchpinxiang(qrystr.split())
            else:
                rstfile, rst = None, None

            itchat.send_msg(rst, toUserName=msg['FromUserName'])
            # 查询结果文件路径备档
            makemsg2write(innermsg, rst)

            if rstfile:
                # rstfile必须是绝对路径，并且不能包含中文字符
                itchat.send_file(rstfile, toUserName=msg['FromUserName'])
                # 发给自己一份存档
                makemsg2write(innermsg,rstfile.replace(os.path.abspath(dirmainpath),""))
                itchat.send_file(rstfile)
                infostr = f"成功发送查询结果文件：{os.path.split(rstfile)[1]}给{innermsg['fmSender']}"
                itchat.send_msg(infostr)
                makemsg2write(innermsg, infostr)
                log.info(infostr)
            # return rst


def listfriends(num=-10):
    friends = itchat.get_friends(update=True)
    for fr in friends[num:]:
        print(fr)


def listchatrooms():
    chatrooms = itchat.get_chatrooms(update=True)
    for cr in chatrooms:
        print(cr)


@itchat.msg_register(FRIENDS)
def add_friend(msg):
    msg.user.verify()
    msg.user.send('Nice to meet you!')
    showfmmsg(msg)
    log.info(msg)


def after_login():
    men_wc = getcfpoptionvalue('everwebchat', get_host_uuid(), 'host_nickname')
    log.info(f"登入《{men_wc}》的微信服务")


def after_logout():
    men_wc = getcfpoptionvalue('everwebchat', get_host_uuid(), 'host_nickname')
    try:
        termux_sms_send(f"微信({men_wc})登录已退出，如有必要请重新启动")
    except Exception as e:
        log.critical(f"尝试发送退出提醒短信失败。{e}")
    log.critical(f'退出微信({men_wc})登录')


def get_host_uuid():
    return uuid3hexstr(os.path.abspath(itchat.originInstance.hotReloadDir))


@trycounttimes2('微信服务器', 200, 50)
def keepliverun():
    # 为了让实验过程更加方便（修改程序不用多次扫码），我们使用热启动
    status4login = itchat.check_login()
    log.critical(f"微信登录状态为：\t{status4login}")
    if status4login == '200':
        log.info(f'已处于成功登录状态')
        return
    itchat.auto_login(hotReload=True, loginCallback=after_login, exitCallback=after_logout)
    # itchat.auto_login(hotReload=True)

    # 设定获取信息时重试的次数，默认是5，设定为50，不知道是否能够起作用
    itchat.originInstance.receivingRetryCount = 50

    init_info = itchat.web_init()
    # showmsg(init_info)
    if init_info['BaseResponse']['Ret'] == 0:
        logstr = f"微信初始化信息成功返回，获取登录用户信息"
        log.info(logstr)
        host_nickname = init_info['User']['NickName']
        host_username = init_info['User']['UserName']
        log.info(f"函数《{sys._getframe().f_code.co_name}》中用户变量为：\t{(host_nickname, host_username)}")
        if len(host_username) > 0:
            setcfpoptionvalue('everwebchat', get_host_uuid(), 'host_nickname',
                              host_nickname)
            setcfpoptionvalue('everwebchat', get_host_uuid(), 'host_username',
                              host_username)
    elif (itchat.originInstance.loginInfo):
        log.info(f"从itchat.originInstance.loginInfo中获取登录用户信息")
        host_nickname = dict(itchat.originInstance.loginInfo['User'])['NickName']
        host_username = dict(itchat.originInstance.loginInfo['User'])['UserName']
        log.info(f"函数《{sys._getframe().f_code.co_name}》中用户变量为：\t{(host_nickname, host_username)}")
        if len(host_username) > 0:
            setcfpoptionvalue('everwebchat', get_host_uuid, 'host_nickname',
                              host_username)
            setcfpoptionvalue('everwebchat', get_host_uuid, 'host_username',
                              host_username)
    else:
        log.info(f"函数《{sys._getframe().f_code.co_name}》中用户变量为：\t{(host_nickname, host_username)}")

    # notechat = newchatnote()
    # listchatrooms()
    # listfriends()
    itchat.run()
    # raise Exception


if __name__ == '__main__':
    if not_IPython():
        log.info(f'运行文件\t{__file__}')

    note_store = get_notestore()
    keepliverun()

    if not_IPython():
        log.info(f'{__file__}\t运行结束！')
