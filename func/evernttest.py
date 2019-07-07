# encoding:utf-8
"""
印象笔记相关功能函数
"""
import binascii
import datetime
import hashlib
import os
import re
import time
# import nltk
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from evernote.api.client import EvernoteClient
from evernote.edam.error.ttypes import EDAMNotFoundException, EDAMSystemException, EDAMUserException, EDAMErrorCode
from evernote.edam.notestore.NoteStore import NoteFilter, NotesMetadataResultSpec
from evernote.edam.type.ttypes import Note, Resource, Data
from evernote.edam.userstore.constants import EDAM_VERSION_MAJOR, EDAM_VERSION_MINOR

import pathmagic

with pathmagic.context():
    from func.configpr import cfp, inifilepath, getcfp, getcfpoptionvalue
    from func.first import dirlog, dirmainpath
    from func.logme import log
    from func.nettools import trycounttimes2

print(f"{__file__} is loading now...")

def get_notestore():
    # Real applications authenticate with Evernote using OAuth, but for the
    # purpose of exploring the API, you can get a developer token that allows
    # you to access your own Evernote account. To get a developer token, visit
    # https://SERVICE_HOST/api/DeveloperToken.action
    #
    # There are three Evernote services:
    #
    # Sandbox: https://sandbox.evernote.com/
    # Production (International): https://www.evernote.com/
    # Production (China): https://app.yinxiang.com/
    #
    # For more information about Sandbox and Evernote China services, please
    # refer to https://dev.evernote.com/doc/articles/testing.php
    # and https://dev.evernote.com/doc/articles/bootstrap.php

    # global log
    # auth_token = token
    # cfp, inipath = getcfp('everwork')
    auth_token = cfp.get('evernote', 'token')  # 直接提取，唯一使用

    if auth_token == "your developer token":
        print("Please fill in your developer token\nTo get a developer token, visit "
              "https://sandbox.evernote.com/api/DeveloperToken.action")
        log.critical('请填入从evernote官方网站申请的有效token！程序终止并退出！！！')
        exit(1)

    # To access Sandbox service, set sandbox to True
    # To access production (International) service, set both sandbox and china to False
    # To access production (China) service, set sandbox to False and china to True
    sandbox = False
    china = False

    # Initial development is performed on our sandbox server. To use the production
    # service, change sandbox=False and replace your
    # developer token above with a token from
    # https://www.evernote.com/api/DeveloperToken.action

    client = EvernoteClient(token=auth_token, sandbox=sandbox, china=china)

    @trycounttimes2('evernote服务器')
    def getnotestore():
        global note_store
        if note_store is not None:
            # log.info(f'note_store已健壮存在：{note_store}')
            return note_store
        userstore = client.get_user_store()
        # evernoteapijiayi()
        version_ok = userstore.checkVersion(
            "Evernote EDAMTest (Python)",
            EDAM_VERSION_MAJOR,
            EDAM_VERSION_MINOR
        )
        if not version_ok:
            log.critical('Evernote API版本过时，请更新之！程序终止并退出！！！')
            exit(1)
        # print("Is my Evernote API version up to date? ", str(version_ok))
        note_store = client.get_note_store()
        evernoteapijiayi()
        log.info(f'成功连接Evernote服务器！构建notestore：{note_store}')
        return note_store

    return getnotestore()


note_store = None


def imglist2note(notestore, imglist, noteguid, notetitle, neirong=''):
    """
    更新note内容为图片列表
    :param notestore:
    :param imglist:
    :param noteguid:
    :param notetitle:
    :param neirong:object
    :return:
    """
    note = Note()
    # print(type(note))
    note.guid = noteguid
    note.title = notetitle

    # To include an attachment such as an image in a note, first create a Resource
    # for the attachment. At a minimum, the Resource contains the binary attachment
    # data, an MD5 hash of the binary data, and the attachment MIME type.
    # It can also include attributes such as filename and location.

    # Now, add the new Resource to the note's list of resources
    # print(len(note.resources))
    # print(noteguid)
    # note.resources = notestore.getNote(token, noteguid, True, True, True,True).resources
    # evernoteapijiayi()
    # if not note.resources:
    #     note.resources = []

    note.resources = []
    # print(len(note.resources))
    # for img, imgtitle in imglist:
    for img in imglist:
        image = open(img, 'rb').read()
        md5 = hashlib.md5()
        md5.update(image)
        imghash = md5.digest()
        data = Data()  # 必须要重新构建一个Data（），否则内容不会变化
        data.size = len(image)
        data.bodyHash = imghash
        data.body = image
        resource = Resource()
        resource.mime = 'image/png'
        resource.data = data
        note.resources.append(resource)

    # The content of an Evernote note is represented using Evernote Markup Language
    # (ENML). The full ENML specification can be found in the Evernote API Overview
    # at http://dev.evernote.com/documentation/cloud/chapters/ENML.php
    nbody = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
    nbody += "<!DOCTYPE en-note SYSTEM \"http://xml.evernote.com/pub/enml2.dtd\">"
    nbody += "<en-note>"
    if note.resources:
        # To display the Resource as part of the note's content, include an <en-media>
        # tag in the note's ENML content. The en-media tag identifies the corresponding
        # Resource using the MD5 hash.
        # nBody += "<br />" * 2
        for resource in note.resources:
            if resource.guid or True:
                hexhash = binascii.hexlify(resource.data.bodyHash)
                str1 = "%s" % hexhash  # b'cd34b4b6c8d9279217b03c396ca913df'
                # print (str1)
                str1 = str1[2:-1]  # cd34b4b6c8d9279217b03c396ca913df
                # print (str1)
                nbody += "<en-media type=\"%s\" hash=\"%s\" align=\"center\" /><br />" % (
                    resource.mime, str1)
    # neirong= "<pre>" + neirong + "</pre>"

    # 去除控制符
    neirong = re.sub('[\x00-\x08|\x0b-\x0c|\x0e-\x1f]', '', neirong)

    nbody += neirong
    nbody += "</en-note>"

    # ！！！严重错误，过滤\x14时把回车等符号都杀了！！！
    # nbodynotasciilst = [hex(ord(x)) for x in nbody if ord(x) < 32]
    # print(f"存在不可显示字符串：{''.join(nbodynotasciilst)}")
    # nbodylst = [x for x in nbody if ord(x) >= 32]
    # nbody = ''.join(nbodylst)
    note.content = nbody
    # print (note.content)

    # Finally, send the new note to Evernote using the updateNote method
    # The new Note object that is returned will contain server-generated
    # attributes such as the new note's unique GUID.
    @trycounttimes2('evernote服务器。更新笔记。')
    def updatenote(notesrc):
        updated_note = get_notestore().updateNote(notesrc)
        evernoteapijiayi()
        log.info('成功更新了笔记《%s》，guid：%s。' %
                 (updated_note.title, updated_note.guid))

    updatenote(note)


def tablehtml2evernote(dataframe, tabeltitle='表格标题', withindex=True,
                       setwidth=True):
    colwidth = pd.get_option('max_colwidth')
    if setwidth:
        pd.set_option('max_colwidth', 200)
    else:
        # print(colwidth)
        pass
    df = pd.DataFrame(dataframe)
    outstr = df.to_html(justify='center', index=withindex).replace('class="dataframe">', 'align="center">'). \
        replace('<table', '\n<h3 align="center">%s</h3>\n<table' %
                tabeltitle).replace('<th></th>', '<th>&nbsp;</th>')
    # print(outstr)
    if setwidth:
        pd.set_option('max_colwidth', colwidth)
    return outstr


def findnotefromnotebook(tokenfnfn, notebookguid, titlefind='', notecount=10000):
    """
    列出笔记本中包含某关键词的笔记信息
    :param tokenfnfn: token
    :param notebookguid: 笔记本的guid
    :param titlefind: 关键词
    :param notecount: 搜索结果数量限值
    :return: 列表，包含形如[noteguid, notetitle]的list
    """
    global note_store
    note_store = get_notestore()
    notefilter = NoteFilter()
    notefilter.notebookGuid = notebookguid
    notemetaspec = NotesMetadataResultSpec(includeTitle=True, includeContentLength=True, includeCreated=True,
                                           includeUpdated=True, includeDeleted=True,
                                           includeUpdateSequenceNum=True,
                                           includeNotebookGuid=True, includeTagGuids=True,
                                           includeAttributes=True,
                                           includeLargestResourceMime=True, includeLargestResourceSize=True)

    @trycounttimes2('evernote服务器')
    def findnote():
        notelist = note_store.findNotesMetadata(
            tokenfnfn, notefilter, 0, notecount, notemetaspec)
        evernoteapijiayi()
        return notelist

    ournotelist = findnote()

    # print ourNoteList.notes[-1].title  #测试打印指定note的标题
    # print note_store.getNoteContent(ourNoteList.notes[-1].guid)  #测试打印指定note的内容
    # note = note_store.getNote(auth_token, ourNoteList.notes[9].guid, True, True, True, True)  #获得Note并打印其中的值
    # p_noteattributeundertoken(note)
    # print ourNoteList.notes[5] #打印NoteMetadata

    items = [[note.guid, note.title, note.updateSequenceNum] for note in ournotelist.notes if
             note.title.find(titlefind) >= 0]
    # for note in ournotelist.notes:
    #     if note.title.find(titlefind) >= 0:
    #         item = list()
    #         item.append(note.guid)
    #         item.append(note.title)
    #         # print(note.guid, note.title)
    #         # p_noteattributeundertoken(note)
    #         items.append(item)

    return items


def getnotecontent(guid:str):
    note_store = get_notestore()
    soup = BeautifulSoup(note_store.getNoteContent(guid), "html.parser")
    # print(soup)
    
    return soup

def makenote(tokenmn, notestore, notetitle, notebody='真元商贸——休闲食品经营专家', parentnotebook=None):
    """
    创建一个note
    :param tokenmn:
    :param notestore:
    :param notetitle:
    :param notebody:
    :param parentnotebook:
    :return:
    """
    # global log
    nbody = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
    nbody += "<!DOCTYPE en-note SYSTEM \"http://xml.evernote.com/pub/enml2.dtd\">"
    nbody += "<en-note>%s</en-note>" % notebody

    # Create note object
    ournote = Note()
    ournote.title = notetitle
    ournote.content = nbody

    # parentNotebook is optional; if omitted, default notebook is used
    if parentnotebook and hasattr(parentnotebook, 'guid'):
        ournote.notebookGuid = parentnotebook.guid

    # Attempt to create note in Evernote account
    try:
        note = notestore.createNote(tokenmn, ournote)
        evernoteapijiayi()
        if parentnotebook and hasattr(parentnotebook, 'name'):
            bkname = f"<{parentnotebook.name}>"
        else:
            bkname = '默认'
        log.info(f'笔记《{notetitle}》在\t{bkname}\t笔记本中创建成功。')
        return note
    except EDAMUserException as usere:
        # Something was wrong with the note data
        # See EDAMErrorCode enumeration for error code explanation
        # http://dev.evernote.com/documentation/reference/Errors.html#Enum_EDAMErrorCode
        log.critical("用户错误！%s" % str(usere))
    except EDAMNotFoundException as notfounde:
        # Parent Notebook GUID doesn't correspond to an actual notebook
        print("无效的笔记本guid（识别符）！%s" % str(notfounde))
    except EDAMSystemException as systeme:
        if systeme.errorCode == EDAMErrorCode.RATE_LIMIT_REACHED:
            log.critical("API达到调用极限，需要 %d 秒后重来" % systeme.rateLimitDuration)
            exit(1)
        else:
            log.critical('创建笔记时出现严重错误：' + str(systeme))
            exit(2)


def timestamp2str(timestamp):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))


def getapitimesfromlog():
    """
    从log中提取API调用次数
    :return:
    """
    # global dirlog, log
    df = pd.read_csv(dirlog, sep='\t',  # index_col= False,
                     header=None, usecols=[0, 1, 2],
                     names=['asctime', 'filenamefuncName', 'levelnamemessage'],
                     na_filter=True, parse_dates=[0],
                     skip_blank_lines=True, skipinitialspace=True)
    # print(df.describe())
    # print(df.shape[0])
    # dfapi2 = df[df.levelnamemessage.str.contains('动用了Evernote API')][['asctime', 'levelnamemessage']]
    dfapi2 = df[df.levelnamemessage.str.contains('动用了Evernote API').values == True][[
        'asctime', 'levelnamemessage']]
    # print(dfapi2.shape[0])
    # print(dfapi2.head(50))
    if dfapi2.shape[0] == 0:
        log.info('日志文件中还没有API的调用记录')
        return False
    dfapi2['asctime'] = dfapi2['asctime'].apply(lambda x: pd.to_datetime(x))
    dfapi2['counts'] = dfapi2['levelnamemessage'].apply(
        lambda x: int(re.findall('(?P<counts>\d+)', x)[-1]))
    # del dfapi2['levelnamemessage']
    # print(dfapi2.tail())
    jj = dfapi2[dfapi2.asctime == dfapi2.asctime.max()]['counts'].iloc[-1]
    # print(type(jj))
    # print(jj)
    result = [dfapi2.asctime.max(), int(jj)]
    # print(dfapi2[dfapi2.asctime == dfapi2.asctime.max()])
    # print(result)
    return result


def writeini():
    """
    evernote API调用次数写入配置文件以备调用。又及，函数写在这里还有个原因是global全局变量无法跨文件传递。
    :return:
    """
    global ENtimes
    # print(ENtimes)
    # print(str(datetime.datetime.now()))
    cfp.set('evernote', 'apicount', '%d' % ENtimes)
    cfp.set('evernote', 'apilasttime', '%s' %
            datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    cfp.write(open(inifilepath, 'w', encoding='utf-8'))
    # log.info('Evernote API调用次数：%d，写入配置文件%s' % (ENtimes, os.path.split(inifilepath)[1]))


def evernoteapiclearatzero():
    """
    evernote API的调用次数过整点清零
    :rtype: None
    :return:
    """
    global ENAPIlasttime, ENtimes
    apilasttimehouzhengdian = pd.to_datetime(
        (ENAPIlasttime + datetime.timedelta(hours=1)).strftime('%Y-%m-%d %H:00:00'))
    # print(apilasttimehouzhengdian)
    now = datetime.datetime.now()
    # print(now)
    if now > apilasttimehouzhengdian:
        ENAPIlasttime = now
        # time.sleep(60)
        ENtimes = 0
        writeini()


def evernoteapijiayi():
    """
    evernote API调用次数加一，如果达到限值则sleep后归零。又及，多次测试，限值应该是300次每个小时，整点清零重来。
    :return:
    """
    global ENtimes, note_store
    log.debug(f'动用了Evernote API({note_store}) {ENtimes} 次……')
    ENtimes += 1
    writeini()
    evernoteapiclearatzero()
    if (ENtimes >= 290) or (note_store is None):
        now = datetime.datetime.now()
        # 强制小时数加一在零点的时候会出错，采用timedelta解决问题
        nexthour = now + datetime.timedelta(hours=1)
        # zhengdian = pd.to_datetime(
        #     '%04d-%02d-%02d %02d:00:00' % (nexthour.year, nexthour.month, nexthour.day, nexthour.hour))
        zhengdian = nexthour.replace(minute=0, second=0, microsecond=0)
        secondsaferzhengdian = np.random.randint(0, 50)
        sleep_seconds = (zhengdian - now).seconds + secondsaferzhengdian
        starttimeafterzhengdian = pd.to_datetime(
            zhengdian + datetime.timedelta(seconds=secondsaferzhengdian))
        print(f'{sleep_seconds}\t{starttimeafterzhengdian}')
        # note_store = None
        log.info(f'Evernote API{note_store} 调用已达{ENtimes:d}次，'
                 f'休息{secondsaferzhengdian:d}秒，重新构造一个服务器连接再开干……')
        time.sleep(secondsaferzhengdian)
        note_store = get_notestore()
        while note_store is None:
            log.info(f'休息{secondsaferzhengdian:d}秒，重新构造一个服务器连接再开干……')
            time.sleep(np.random.randint(0, 50))
            note_store = get_notestore()
            log.info(f'构建新的evernote服务器连接：{note_store}')
            ENtimes = 0
            writeini()


# @use_logging()
def p_notebookattributeundertoken(notebook):
    """
    测试笔记本（notebook）数据结构每个属性的返回值,开发口令（token）的方式调用返回如下
    :param notebook:
    :return:
    """
    print('名称：' + notebook.name, end='\t')  # phone
    # f64c3076-60d1-4f0d-ac5c-f0e110f3a69a
    print('guid：' + notebook.guid, end='\t')
    print('更新序列号：' + str(notebook.updateSequenceNum), end='\t')  # 8285
    print('默认笔记本：' + str(notebook.defaultNotebook), end='\t')  # False
    print('创建时间：' + timestamp2str(int(notebook.serviceCreated / 1000)),
          end='\t')  # 2010-09-15 11:37:43
    print('更新时间：' + timestamp2str(int(notebook.serviceUpdated / 1000)),
          end='\t')  # 2016-08-29 19:38:24
    # print '发布中\t', notebook.publishing  #这种权限的调用返回None
    # print '发布过\t', notebook.published  #这种权限的调用返回None
    print('笔记本组：' + str(notebook.stack))  # 手机平板
    # print '共享笔记本id\t', notebook.sharedNotebookIds  #这种权限的调用返回None
    # print '共享笔记本\t', notebook.sharedNotebooks  #这种权限的调用返回None
    # print '商务笔记本\t', notebook.businessNotebook  #这种权限的调用返回None
    # print '联系人\t', notebook.contact  #这种权限的调用返回None
    # print '限定\t', notebook.restrictions  #NotebookRestrictions(noSetDefaultNotebook=None,
    # noPublishToBusinessLibrary=True, noCreateTags=None, noUpdateNotes=None,
    # expungeWhichSharedNotebookRestrictions=None,
    # noExpungeTags=None, noSetNotebookStack=None, noCreateSharedNotebooks=None, noExpungeNotebook=None,
    # noUpdateTags=None, noPublishToPublic=None, noUpdateNotebook=None, updateWhichSharedNotebookRestrictions=None,
    # noSetParentTag=None, noCreateNotes=None, noEmailNotes=True, noReadNotes=None, noExpungeNotes=None,
    # noShareNotes=None, noSendMessageToRecipients=None)
    # print '接受人设定\t', notebook.recipientSettings  #这种权限的调用没有返回这个值，报错


def p_noteattributeundertoken(note):
    """
    测试笔记（note）数据结构每个属性的返回值,通过findNotesMetadata函数获取，开发口令（token）的方式调用返回如下:
    :param note:
    :return:
    """
    print('guid\t%s' % note.guid)  #
    print('标题\t%s' % note.title)  #
    print('内容长度\t%d' % note.contentLength)  # 762
    # 这种权限的调用没有返回这个值，报错；NoteStore.getNoteContent()也无法解析
    print('内容\t' + note.content)
    print('内容哈希值\t%s' % note.contentHash)  # 8285
    # 2017-09-04 22:39:51
    print('创建时间\t%s' % timestamp2str(int(note.created / 1000)))
    # 2017-09-07 06:38:47
    print('更新时间\t%s' % timestamp2str(int(note.updated / 1000)))
    print('删除时间\t%s' % note.deleted)  # 这种权限的调用返回None
    print('活跃\t%s' % note.active)  # True
    print('更新序列号\t%d' % note.updateSequenceNum)  # 173514
    # 2c8e97b5-421f-461c-8e35-0f0b1a33e91c
    print('所在笔记本的guid\t%s' % note.notebookGuid)
    print('标签的guid表\t%s' % note.tagGuids)  # 这种权限的调用返回None
    print('资源表\t%s' % note.resources)  # 这种权限的调用返回None
    print('属性\t%s' % note.attributes)
    # NoteAttributes(lastEditorId=139947593, placeName=None, sourceURL=None, classifications=None,
    # creatorId=139947593, author=None, reminderTime=None, altitude=0.0, reminderOrder=None, shareDate=None,
    # reminderDoneTime=None, longitude=114.293, lastEditedBy='\xe5\x91\xa8\xe8\x8e\x89 <305664756@qq.com>',
    # source='mobile.android', applicationData=None, sourceApplication=None, latitude=30.4722, contentClass=None,
    # subjectDate=None)
    print('标签名称表\t%s' % note.tagNames)  # 这种权限的调用返回None
    # print ('共享的笔记表\t%s' % note.sharedNotes)
    # 这种权限的调用没有返回这个值，报错AttributeError: 'Note' object has no attribute 'sharedNotes'
    # print ('限定\t%s' % note.restrictions)
    # 这种权限的调用没有返回这个值，报错AttributeError: 'Note' object has no attribute 'restrictions'
    # print ('范围\t%s' % note.limits) #这种权限的调用没有返回这个值，报错AttributeError: 'Note' object has no attribute 'limits'


def findnotebookfromevernote():
    # 列出账户中的全部笔记本
    global note_store
    note_store = get_notestore()
    notebooks = note_store.listNotebooks()
    # p_notebookattributeundertoken(notebooks[-1])

    for x in notebooks:
        p_notebookattributeundertoken(x)


@trycounttimes2('evernote服务器')
def readinifromnote():
    cfpeverwork, cfpeverworkpath = getcfp('everwork')
    noteguid_inifromnote = cfpeverwork.get('evernote', 'ininoteguid')
    # noteguid_inifromnote = 'e0565861-db9e-4efd-be00-cbce06d0cf98'
    global note_store
    note_store = get_notestore()
    if cfpeverwork.has_option('evernote', 'ininoteupdatenum'):
        ininoteupdatenum = cfpeverwork.getint('evernote', 'ininoteupdatenum')
    else:
        ininoteupdatenum = 0
    note = note_store.getNote(noteguid_inifromnote, True, True, False, False)
    if note.updateSequenceNum == ininoteupdatenum:
        # print(f'配置笔记无变化，不对本地化的ini配置文件做更新。')
        return
    else:
        cfpeverwork.set('evernote', 'ininoteupdatenum', str(note.updateSequenceNum))
        cfpeverwork.write(open(cfpeverworkpath, 'w', encoding='utf-8'))
        log.info(f'配置笔记内容有变化，更新本地化的ini配置文件。')
    soup = BeautifulSoup(note_store.getNoteContent( noteguid_inifromnote), "html.parser")
    # print(soup)
    ptn = u'<div>(.*?)</div>'
    # ptn = u'<div>'
    itemsource = re.findall(ptn, str(soup))
    print(itemsource)
    items = [x for x in itemsource if not re.search('<.*?>', x)]
    print(items)
    fileobj = open(str(dirmainpath / 'data' / 'everinifromnote.ini'), 'w',
                   encoding='utf-8')
    for item in items:
        fileobj.write(item + '\n')
    fileobj.close()


def getinivaluefromnote(section, option):
    readinifromnote()

    return getcfpoptionvalue('everinifromnote', section, option)


def writeini2note():
    pass


def findsomenotest2showornote(nbguid, keyword, newnote=False):
    global token
    nost = get_notestore()
    notesfind = findnotefromnotebook(token, nbguid, keyword)
    if newnote:
        makenote(token, nost, f"“{keyword}》”记列表", str(notesfind))
    else:
        print(notesfind)


# print('我是evernt啊')
# global cfp
token = cfp.get('evernote', 'token')
ENtimes = cfp.getint('evernote', 'apicount')
ENAPIlasttime = pd.to_datetime(cfp.get('evernote', 'apilasttime'))
apitime = getapitimesfromlog()
print(ENAPIlasttime, apitime)
if apitime:
    # 比较ini和log中API存档的时间，解决异常退出时调用次数无法准确反映的问题
    if apitime[0] > ENAPIlasttime:
        diff = apitime[0] - ENAPIlasttime
    else:
        diff = ENAPIlasttime - apitime[0]
    # print(diff.seconds)
    if diff.seconds > 60:
        log.info('程序上次异常退出，调用log中的API数据[%s,%d]' %
                 (str(apitime[0]), apitime[1]))
        ENAPIlasttime = apitime[0]
        ENtimes = apitime[1] + 1
evernoteapiclearatzero()

# writeini()

if __name__ == '__main__':
    log.info(f'开始运行文件\t{__file__}')
    nost = get_notestore()
    print(nost)
    # readinifromnote()
    # writeini()
    # findnotebookfromevernote()

    # 查找主题包含关键词的笔记
    notification_guid =  '4524187f-c131-4d7d-b6cc-a1af20474a7f'
    shenghuo_guid =  '7b00ceb7-1762-4e25-9ba9-d7e952d57d8b'
    # findsomenotest2showornote(notification_guid, '补')

    # 显示笔记内容，源码方式
    # '39c0d815-df23-4fcc-928d-d9193d5fff93' 转账
    # 'ba9dcaa7-9a8f-4ee8-86a6-fd788b71d411' 微信号
    findnotecontent = getnotecontent('39c0d815-df23-4fcc-928d-d9193d5fff93' )
    print(f"{findnotecontent}")

    # # 将notebooklst.txt内容更新至新建的笔记中
    # filetitle = '笔记本列表'
    # filepath = dirmainpath / 'notebooklst.txt'
    # dffile = open(filepath)
    # neirong = dffile.read()
    # dffile.close()
    # makenote(token, nost,filetitle, neirong)

    # # makenote(token, nost, '转账记录笔记guid', str(notefind))
    log.info(f"完成文件{__file__}\t的运行")
