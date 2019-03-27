# coding=utf8
"""
微信大观园，工作优先，娱乐生活
"""
import time
import datetime
import requests
import itchat
import re
from pathlib import Path
from itchat.content import *

import pathmagic
with pathmagic.context():
    from func.first import touchfilepath2depth, getdirmain
    from func.configpr import getcfp
    from func.logme import log
    from func.nettools import trycounttimes2
    from func.evernttest import token, get_notestore, makenote, imglist2note, evernoteapijiayi, readinifromnote
    from func.datatools import readfromtxt, write2txt
    import evernote.edam.type.ttypes as ttypes

def newchatnote():
    global note_store
    parentnotebook = note_store.getNotebook('4524187f-c131-4d7d-b6cc-a1af20474a7f')
    evernoteapijiayi()
    note = ttypes.Note()
    note.title = f"微信记录:{time.strftime('%Y-%m-%d_%H:%M:%S',time.localtime(time.time()))}"
    print(note.title)
    notechat= makenote(token, note_store, note.title, notebody='', parentnotebook=parentnotebook)

    return notechat


def get_response(msg):
    try:
        txt = msg['Text']
        # print(msg)
        return txt
    # 为了防止服务器没有正常响应导致程序异常退出，这里用try-except捕获了异常
    # 如果服务器没能正常交互（返回非json或无法连接），那么就会进入下面的return
    except:
        # 将会返回一个None
        return


def showmsg(msg):
    # print(msg)
    for item in msg:
        # print(item)
        # if item.lower().find('name') < 0:
            # continue
        print(f'{item}\t{type(msg[item])}', end='\t')
        if type(msg[item]) in [dict,
                itchat.storage.templates.Chatroom,
                itchat.storage.templates.User]:
            print(len(msg[item]))
            for child in msg[item]:
                childmsg = msg[item][child]
                print(f'\t{child}\t{type(childmsg)}', end='\t')
                if type(childmsg) in [dict,
                        itchat.storage.templates.User,
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

    # print(f"{timestr}\t{showname}", end='')
    # if type(msg['User']) == itchat.storage.templates.Chatroom:
    if msg['FromUserName'].startswith('@@'):
        # print(f"（群)\t{msg['ActualNickName']}", end='')
        showname += f"(群){msg['ActualNickName']}"
    elif msg['ToUserName'].startswith('@@'):
        # print(f"（群）\t{msg['User']['Self']['NickName']}", end='')
        # showmsg(msg)
        showname += f"(群){msg['User']['Self']['NickName']}"
    # print(f"\t{msg['Type']}\t{msg['MsgType']}\t{msg['Text']}")
    # print(f"\t{send}\t{msg['Type']}\t{msg['Text']}")
    fmtext = msg['Text']

    formatMsg = {'fmId': msg['MsgId'], 'fmTime': timestr, 'fmSend': send, 'fmSender': showname,
                 'fmType': msg['Type'], 'fmText': fmtext}

    return formatMsg


def showfmmsg(formatmsg):
    msgcontent = ""
    for item in formatmsg:
        if item == "fmId":
            continue
        msgcontent += f"{formatmsg[item]}\t"
    msgcontent = msgcontent[:-1]
    print(f"{msgcontent}")

    chattxtfilename = str(getdirmain() / 'data' / 'webchat' / 'chatitems.txt')
    chatitems = readfromtxt(chattxtfilename)
    global note_store
    # webchats.append(chatmsg)
    chatitems.insert(0, msgcontent)
    write2txt(chattxtfilename, chatitems)
    readinifromnote()
    cfpfromnote, cfpfromnotepath = getcfp('everinifromnote') 
    chatnoteguid = cfpfromnote.get('webchat', 'noteguid').lower()
    updatefre = cfpfromnote.getint('webchat', 'updatefre')
    showitemscount= cfpfromnote.getint('webchat', 'showitems')
    neirong = "\n".join(chatitems[:showitemscount])
    neirongplain = neirong.replace('<', '《').replace('>',
        '》').replace('=', '等于').replace('&', '并或')                
    if (len(chatitems) % updatefre) == 0:
        imglist2note(note_store, [], chatnoteguid, "微信记录更新笔记",
                neirongplain)
    # print(webchats)

@itchat.msg_register([CARD, FRIENDS],
        isFriendChat=True, isGroupChat=True, isMpChat=True)
def tuling_reply(msg):
    showmsg(msg)
    showfmmsg(formatmsg(msg))

@itchat.msg_register([NOTE], isFriendChat=True, isGroupChat=True, isMpChat=True)
def tuling_reply(msg):
    # showmsg(msg)
    innermsg = formatmsg(msg)
    if msg["FileName"] == "微信转账":
        ptn = re.compile("<pay_memo><!\[CDATA\[(.*)\]\]></pay_memo>")
        pay = re.search(ptn, msg["Content"])[1]
        innermsg['fmText'] = innermsg['fmText']+f"[{pay}]"
    else:
        showmsg(msg)
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
    owner = itchat.web_init()
    # if innermsg['fmSend']:
    # innermsg['fmSender'] = owner['User']['NickName']
    filepath = getdirmain() / "img" / "webchat" / time.strftime("%Y%m%d", time.localtime(msg['CreateTime'])) / f"{innermsg['fmSender']}_{msg['FileName']}"
    touchfilepath2depth(filepath)
    log.info(f"保存{innermsg['fmType']}类型文件：\t{str(filepath)}")
    msg['Text'](str(filepath))
    innermsg['fmText'] = str(filepath)

    showfmmsg(innermsg)


@itchat.msg_register([SHARING], isFriendChat=True, isGroupChat=True, isMpChat=True)
def tuling_reply(msg):
    showmsg(msg)
    innermsg = formatmsg(msg)
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
