# coding=utf8
"""
微信大观园，工作优先，娱乐生活
"""

import time
import datetime
import itchat
import itchat.storage
import re
import os
import math
from itchat.content import *
from bs4 import BeautifulSoup

import pathmagic
with pathmagic.context():
    from func.first import touchfilepath2depth, getdirmain, dirmainpath
    from func.configpr import getcfp
    from func.logme import log
    from func.nettools import trycounttimes2
    from func.evernttest import token, get_notestore, makenote, imglist2note, \
        evernoteapijiayi, getinivaluefromnote
    from func.datatools import readfromtxt, write2txt
    from func.termuxtools import termux_sms_send
    from work.weixinzhang import showjinzhang, showshoukuan
    import evernote.edam.type.ttypes as ttypes
    from work.zymessage import searchcustomer, searchqiankuan, searchpinxiang
    from etc.getid import getdeviceid
    from muse.majjianghuojie import updateurllst, zhanjidesc


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
    # print(timetuple)
    timestr = time.strftime("%Y-%m-%d %H:%M:%S", timetuple)
    # owner = itchat.web_init()
    global meu_wc
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


def showfmmsg(inputformatmsg):
    msgcontent = ""
    for item in inputformatmsg:
        if item == "fmId":
            continue
        msgcontent += f"{inputformatmsg[item]}\t"
    msgcontent = msgcontent[:-1]
    print(f"{msgcontent}")

    global men_wc
    # me = getowner()['User']['NickName']
    chattxtfilename = str(getdirmain() / 'data' / 'webchat' / f'chatitems({men_wc}).txt')
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
    # print(f"{men_wc}")
    # if len(men_wc) ==0 :
        # log.critical(f"登录名为空！！！")
    chatnoteguid = getinivaluefromnote('webchat', men_wc).lower()
    updatefre = getinivaluefromnote('webchat', 'updatefre')
    showitemscount = getinivaluefromnote('webchat', 'showitems')
    # print(f"{type(showitemscount)}\t{showitemscount}")
    neirong = "\n".join(chatitems[:showitemscount])
    neirongplain = neirong.replace('<', '《').replace('>', '》') \
        .replace('=', '等于').replace('&', '并或')
    if (len(chatitems) % updatefre) == 0:
        neirongplain = "<pre>" + neirongplain + "</pre>"
        imglist2note(note_store, [], chatnoteguid, f"微信（{men_wc}）记录更新笔记",
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
        innermsg['fmText'] = innermsg['fmText']+f"[{pay}]"
    if msg["FileName"].find('红包') >= 0:
        showmsg(msg)
    showfmmsg(innermsg)


@itchat.msg_register([MAP], isFriendChat=True, isGroupChat=True, isMpChat=True)
def map_reply(msg):
    # showmsg(msg)
    innermsg = formatmsg(msg)
    gps = msg['Url'].split('=')[1]
    # print(f"[{gps}]")
    innermsg['fmText'] = innermsg['fmText']+f"[{gps}]"
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



@itchat.msg_register([SHARING], isFriendChat=True, isGroupChat=True,
                     isMpChat=True)
def sharing_reply(msg):
    innermsg = formatmsg(msg)
    soup, items = soupclean2item(msg['Content'])

    # 过滤掉已经研究过属性公众号信息，对于尚未研究过的显示详细信息
    impimlst = re.split('[，,]', getinivaluefromnote('webchat', 'impmplist'))

    cleansender = re.split("\\(群\\)", innermsg['fmSender'])[0]

    if cleansender in impimlst:
        if cleansender == '微信支付' and innermsg["fmText"].endswith("转账收款汇总通知"):
            itms = soup.opitems.find_all('opitem')
            userfre = [f'{x.weapp_username.string}\t{x.hint_word.string}' for x in itms if x.word.string.find(
                '收款记录') >= 0][0]
            innermsg['fmText'] = innermsg['fmText'] + \
                f"[{soup.des.string}\n[{userfre}]]"
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
            innermsg['fmText'] = innermsg['fmText']+f"[{pay}]"
        elif soup.des or soup.digest:
            valuepart = soup.des or soup.digest
            innermsg['fmText'] = innermsg['fmText']+f"[{valuepart.string}]"
        else:
            showmsg(msg)
    elif len(items) > 0:
        itemstr = '\n'
        for item in items:
            itemstr += item.title.string + '\n'
        # 去掉尾行的回车
        itemstr = itemstr[:-1]
        innermsg['fmText'] = innermsg['fmText']+itemstr
    elif type(msg['User']) == itchat.storage.MassivePlatform:
        showmsg(msg)

    showfmmsg(innermsg)


@itchat.msg_register([TEXT], isFriendChat=True, isGroupChat=True, isMpChat=True)
def text_reply(msg):
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

    # 处理火界麻将战绩网页
    ptn = re.compile("h5_whmj_qp/zhanji/index.php\?id=")
    msgtxt = msg['Text']
    if re.findall(ptn, msgtxt):
        if msgtxt.startswith('http'):
            updateurllst(msgtxt)
        outstr = f"发现新的火界麻将战绩网页链接并处理\t{msgtxt}"
        log.info(outstr)
        # itchat.send_msg(outstr)
        itchat.send_msg(f"{zhanjidesc()}", toUserName=msg['FromUserName'])

    # 特定指令则退出
    if msg['Text'] == '退出小元宝系统':
        log.info(f"根据指令退出小元宝系统")
        itchat.logout()

    # 如何不是指定的数据分析中心，则不进行语义分析
    thisid = getdeviceid()
    # print(f"type:{type(thisid)}\t{thisid}")
    houseid = getinivaluefromnote('webchat', 'datahouse')
    # print(f"type:{type(houseid)}\t{houseid}")
    if thisid != str(houseid) :
        print(f"不是数据分析中心，咱不管哦")
        return

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
                    rstfile , rst = searchcustomer()
                else:
                    qrystr = qrylst[1].strip()
                    rstfile, rst = searchcustomer(qrystr.split())
            elif diyihang[1] == '欠款':
                qrystr = qrylst[1].strip()
                rstfile, rst = searchqiankuan(qrystr.split())
            elif diyihang[1] == '品项':
                qrystr = qrylst[1].strip()
                rstfile, rst = searchpinxiang(qrystr.split())

            itchat.send_msg(rst, toUserName=msg['FromUserName'])
            nowtuple = time.time()
            nowdatetime = datetime.datetime.fromtimestamp(nowtuple)
            finnalmsg = {'fmId': math.floor(nowtuple),
                         'fmTime': nowdatetime.strftime("%Y-%m-%d %H:%M:%S"),
                         'fmSend': True, 'fmSender': innermsg['fmSender'],
                         'fmType': 'Text',
                         # 'fmText': os.path.split(rstfile)[1]
                         'fmText': rst
                        }
            showfmmsg(finnalmsg)

            if rstfile:
                # rstfile必须是绝对路径，并且不能包含中文字符
                itchat.send_file(rstfile, toUserName=msg['FromUserName'])
                # 发给自己一份存档
                nowtuple = time.time()
                nowdatetime = datetime.datetime.fromtimestamp(nowtuple)
                finnalmsg = {'fmId': math.floor(nowtuple),
                             'fmTime': nowdatetime.strftime("%Y-%m-%d %H:%M:%S"),
                             'fmSend': True, 'fmSender': innermsg['fmSender'],
                             'fmType': 'File',
                             # 'fmText': os.path.split(rstfile)[1]
                             'fmText':
                             rstfile.replace(os.path.abspath(dirmainpath), '')[1:]
                            }
                showfmmsg(finnalmsg)
                itchat.send_file(rstfile)
                infostr = f"成功发送查询结果文件：{os.path.split(rstfile)[1]}给{innermsg['fmSender']}"
                itchat.send_msg(infostr)
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


def getowner():
    owner = itchat.web_init()
    # showmsg(owner)
    return owner


def after_login():
    owner = getowner()
    # print(owner)
    loginname = owner['User']['NickName']
    log.info(f"登入《{loginname}》的微信服务")


def after_logout():
    global men_wc
    try:
        termux_sms_send(f"微信({men_wc})登录已退出，如有必要请重新启动")
    except Exception as e:
        log.critical(f"尝试发送退出提醒短信失败。{e}")
        pass
    log.critical(f'退出微信({men_wc})登录')


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

    global men_wc, meu_wc
    owner = getowner()
    # showmsg(owner)
    men_wc = owner['User']['NickName']
    meu_wc = owner['User']['UserName']
    # getowner()
    # notechat = newchatnote()
    # listchatrooms()
    # listfriends()
    itchat.run()
    # raise Exception


if __name__ == '__main__':
    log.info(f'运行文件\t{__file__}')

    note_store = get_notestore()
    men_wc = ''
    meu_wc = ''
    keepliverun()

    log.info(f'{__file__}\t运行结束！')
