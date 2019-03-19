# coding=utf8
import time
import datetime
import requests
import itchat
from pathlib import Path
from itchat.content import *

import pathmagic
with pathmagic.context():
    from func.first import touchfilepath2depth, getdirmain
    from func.logme import log
    from func.nettools import trycounttimes2
"""
"""


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
                    print(f'\t\t{childmsg[:10]}')
                else:
                    print(f'\t\t{childmsg}')

        else:
            print(msg[item])


# 这里是我们在“1. 实现微信消息的获取”中已经用到过的同样的注册方法
# @itchat.msg_register([TEXT, MAP, CARD, NOTE, SHARING, PICTURE, RECORDING,
    # ATTACHMENT, VIDEO, FRIENDS, SYSTEM])
@itchat.msg_register([TEXT, MAP, CARD, NOTE, SHARING, PICTURE, RECORDING,
    ATTACHMENT, VIDEO, FRIENDS], isFriendChat=True, isGroupChat=True,
    isMpChat=True)
def tuling_reply(msg):
    if msg['Type'].upper() in [
            # 'TEXT', 
            'MAP',
            'CARD',
            'NOTE',
            'SHARING',
            # 'PICTURE',
            # 'RECORDING',
            # 'ATTACHMENT', 
            # 'VIDEO',
            'FRIENDS'
            ]:
        showmsg(msg)
    timetuple = time.localtime(msg['CreateTime'])
    # print(timetuple)
    timestr = time.strftime("%m-%d %H:%M:%S", timetuple)
    owner = itchat.web_init()
    send = (msg['FromUserName'] == owner['User']['UserName'])
    showname = msg['User']['NickName']
    if len(msg['User']['RemarkName']) > 0:
        showname = msg['User']['RemarkName']
    print(f"{timestr}\t{showname}", end='')
    # if type(msg['User']) == itchat.storage.templates.Chatroom:
    if msg['FromUserName'].startswith('@@'):
        print(f"（群)\t{msg['ActualNickName']}", end='')
        showname += f"_{msg['ActualNickName']}"
    elif msg['ToUserName'].startswith('@@'):
        print(f"（群）\t{msg['User']['Self']['NickName']}", end='')
        showname += f"_{msg['User']['Self']['NickName']}"
    # print(f"\t{msg['Type']}\t{msg['MsgType']}\t{msg['Text']}")
    print(f"\t{send}\t{msg['Type']}\t{msg['Text']}")
    if msg['Type'].upper() in ['PICTURE', 'RECORDING', 'VIDEO', 'ATTACHMENT']:
        if send:
            showname = owner['User']['NickName']
        filepath = getdirmain() / "img" / "webchat" / time.strftime("%Y%m%d",
            timetuple) / f"{showname}_{msg['FileName']}"
        touchfilepath2depth(filepath)
        log.info(f"保存{msg['Type']}类型文件：\t{str(filepath)}")
        msg['Text'](str(filepath))
    # 为了保证在图灵Key出现问题的时候仍旧可以回复，这里设置一个默认回复
    # defaultReply = 'I received: ' + msg['Text']
    # if msg['User']['NickName'] == '小元宝':
        # print(f'收到小元宝的信息:\t{msg["Text"]}')
    reply = get_response(msg['Text'])
    # a or b的意思是，如果a有内容，那么返回a，否则返回b
    # 有内容一般就是指非空或者非None，你可以用`if a: print('True')`来测试
    # return reply or defaultReply
    return

# @itchat.msg_register([PICTURE, RECORDING, VIDEO, ATTACHMENT], isFriendChat=True, isGroupChat=True,
    # isMpChat=True)
# def download_files(msg):
    # msg['Text'](msg['FileName'])

# 为了让实验过程更加方便（修改程序不用多次扫码），我们使用热启动
itchat.auto_login(hotReload=True)

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

@trycounttimes2('微信服务器')
def keepliverun():
    log.info("启动微信信息处理服务")
    # getowner()
    itchat.run()

# listchatrooms()
# listfriends()
keepliverun()
