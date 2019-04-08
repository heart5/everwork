# coding=utf8
"""
微信大观园，工作优先，娱乐生活
"""

import time
import itchat
import itchat.storage
import re
from itchat.content import *
from bs4 import BeautifulSoup

import pathmagic
with pathmagic.context():
    from func.first import touchfilepath2depth, getdirmain
    from func.configpr import getcfp
    from func.logme import log
    from func.nettools import trycounttimes2
    from func.evernttest import token, get_notestore, makenote, imglist2note, \
        evernoteapijiayi, getinivaluefromnote
    from func.datatools import readfromtxt, write2txt
    from func.termuxtools import termux_sms_send
    import evernote.edam.type.ttypes as ttypes


def newchatnote():
    global note_store
    # parentnotebook = \
        # note_store.getNotebook('4524187f-c131-4d7d-b6cc-a1af20474a7f')
    parentnotebook = \
        note_store.getNotebook(getinivaluefromnote('notebookguid', 'notification'))
    evernoteapijiayi()
    note = ttypes.Note()
    note.title = f"微信记录:" \
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
                    # print(f'\t\t{childmsg[:10]}')
                    print(f'\t\t{childmsg}')
                else:
                    print(f'\t\t{childmsg}')

        else:
            print(msg[item])


def formatmsg(msg):
    timetuple = time.localtime(msg['CreateTime'])
    # print(timetuple)
    timestr = time.strftime("%m-%d %H:%M:%S", timetuple)
    owner = itchat.web_init()
    send = (msg['FromUserName'] == owner['User']['UserName'])
    if 'NickName' in msg["User"].keys():
        showname = msg['User']['NickName']
        if len(msg['User']['RemarkName']) > 0:
            showname = msg['User']['RemarkName']       
    elif 'UserName' in msg['User'].keys():
        showname = msg['User']['UserName']
    else:
        showname = ""
        log.warning(f"NickName键值不存在哦")
        showmsg(msg)

    # 过滤掉已经研究过属性的群或公众号信息，对于尚未研究过的显示详细信息
    ignoredmplist = getinivaluefromnote('webchat', 'ignoredmplist')
    imlst = re.split('[，,]', ignoredmplist)
    isfromqun = msg['FromUserName'].startswith('@@')
    istoqun = msg['ToUserName'].startswith('@@')
    if (isfromqun or istoqun) and (showname not in imlst):
        showmsg(msg)
        print(f"{showname}\t{imlst}")

    # if type(msg['User']) == itchat.storage.templates.Chatroom:
    if isfromqun:
        # print(f"（群)\t{msg['ActualNickName']}", end='')
        showname += f"(群){msg['ActualNickName']}"
    elif istoqun:
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

    chattxtfilename = str(getdirmain() / 'data' / 'webchat' / 'chatitems.txt')
    chatitems = readfromtxt(chattxtfilename)
    global note_store
    # webchats.append(chatmsg)
    chatitems.insert(0, msgcontent)
    write2txt(chattxtfilename, chatitems)
    # readinifromnote()
    # cfpfromnote, cfpfromnotepath = getcfp('everinifromnote') 
    chatnoteguid = getinivaluefromnote('webchat', 'noteguid').lower()
    updatefre = getinivaluefromnote('webchat', 'updatefre')
    showitemscount = getinivaluefromnote('webchat', 'showitems')
    # print(f"{type(showitemscount)}\t{showitemscount}")
    neirong = "\n".join(chatitems[:showitemscount])
    neirongplain = neirong.replace('<', '《').replace('>', '》') \
        .replace('=', '等于').replace('&', '并或')
    if (len(chatitems) % updatefre) == 0:
        imglist2note(note_store, [], chatnoteguid, "微信记录更新笔记",
                     neirongplain)
    # print(webchats)


@itchat.msg_register([CARD, FRIENDS], isFriendChat=True, isGroupChat=True,
                     isMpChat=True)
def tuling_reply(msg):
    # showmsg(msg)
    showfmmsg(formatmsg(msg))


@itchat.msg_register([NOTE], isFriendChat=True, isGroupChat=True, isMpChat=True)
def tuling_reply(msg):
    # showmsg(msg)
    innermsg = formatmsg(msg)
    if msg["FileName"] == "微信转账":
        ptn = re.compile("<pay_memo><!\\[CDATA\\[(.*)\\]\\]></pay_memo>")
        pay = re.search(ptn, msg["Content"])[1]
        innermsg['fmText'] = innermsg['fmText']+f"[{pay}]"
    showfmmsg(innermsg)


@itchat.msg_register([MAP], isFriendChat=True, isGroupChat=True, isMpChat=True)
def tuling_reply(msg):
    # showmsg(msg)
    innermsg = formatmsg(msg)
    gps = msg['Url'].split('=')[1]
    # print(f"[{gps}]")
    innermsg['fmText'] = innermsg['fmText']+f"[{gps}]"
    showfmmsg(innermsg)


@itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO],
                     isFriendChat=True, isGroupChat=True, isMpChat=True)
def tuling_reply(msg):
    innermsg = formatmsg(msg)
    # owner = itchat.web_init()
    # if innermsg['fmSend']:
    # innermsg['fmSender'] = owner['User']['NickName']
    createtimestr = time.strftime("%Y%m%d", time.localtime(msg['CreateTime']))
    filepath = getdirmain() / "img" / "webchat" / createtimestr
    filepath = filepath / f"{innermsg['fmSender']}_{msg['FileName']}"
    touchfilepath2depth(filepath)
    log.info(f"保存{innermsg['fmType']}类型文件：\t{str(filepath)}")
    msg['Text'](str(filepath))
    innermsg['fmText'] = str(filepath)

    showfmmsg(innermsg)


@itchat.msg_register([SHARING], isFriendChat=True, isGroupChat=True,
                     isMpChat=True)
def sharing_reply(msg):
    # readinifromnote()
    # cfpfromnote, cfpfromnotepath = getcfp('everinifromnote') 
    # showmsg(msg)
    innermsg = formatmsg(msg)
    rpcontent = msg['Content'].replace('<![CDATA[', '').replace(']]>', '')
    soup = BeautifulSoup(rpcontent, 'lxml')
    category = soup.category
    if category:
        items = category.find_all('item')
        if not items:
            items = []
    else:
        items = []
    cleansender = re.split("\\(群\\)", innermsg['fmSender'])[0]
    if (cleansender == "创米科技") and (innermsg["fmText"] == "监控被触发提醒"):
        # print(f"小米监控发现情况")
        ptn = re.compile("<des><!\\[CDATA\\[(.*)\\]\\]></des>", re.DOTALL)
        pay = re.search(ptn, msg["Content"])[1]
        innermsg['fmText'] = innermsg['fmText']+f"[{pay}]"
    elif (cleansender == "腾讯理财通") and (innermsg["fmText"] == "取出到账通知"):
        # print(f"小米监控发现情况")
        ptn = re.compile("<des><!\\[CDATA\\[(.*)\\]\\]></des>", re.DOTALL)
        pay = re.search(ptn, msg["Content"])[1]
        innermsg['fmText'] = innermsg['fmText']+f"[{pay}]"
    elif (cleansender == "微信运动") and innermsg["fmText"].endswith("刚刚赞了你"):
        ptn = re.compile("<rankid><!\\[CDATA\\[(.*)\\]\\]></rankid>", re.DOTALL)
        pay = re.search(ptn, msg["Content"])[1]
        innermsg['fmText'] = innermsg['fmText']+f"[{pay}]"
    elif (cleansender == "微信运动") and innermsg["fmText"].endswith("排行榜冠军"):
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
    elif len(items) > 0:
        itemstr = '\n'
        for item in items:
            itemstr += item.title.string + '\n'
        innermsg['fmText'] = innermsg['fmText']+itemstr
    # else:
        # showmsg(msg)

    showfmmsg(innermsg)


@itchat.msg_register([TEXT], isFriendChat=True, isGroupChat=True, isMpChat=True)
def tuling_reply(msg):
    showfmmsg(formatmsg(msg))


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
    showmsg(owner)
    return owner


def after_login():
    log.info(f"登入《{itchat.web_init()['User']['NickName']}》的微信服务")


def after_logout():
    termux_sms_send(f"微信登录已退出，如有必要请重新启动")
    log.info(f'退出微信登录')


@trycounttimes2('微信服务器')
def keepliverun():
    # 为了让实验过程更加方便（修改程序不用多次扫码），我们使用热启动
    status4login = itchat.check_login()
    if status4login == '200':
        log.info(f'已成功登录，自动退出避免重复登录')
        itchat.logout()
    itchat.auto_login(hotReload=True,
                      loginCallback=after_login, exitCallback=after_logout)
    # getowner()
    itchat.run()
    # raise Exception


# listchatrooms()
# listfriends()
note_store = get_notestore()
# notechat = newchatnote()
keepliverun()
