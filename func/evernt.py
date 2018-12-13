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
import numpy as np
import pandas as pd
from evernote.api.client import EvernoteClient
from evernote.edam.error.ttypes import EDAMNotFoundException, EDAMSystemException, EDAMUserException, EDAMErrorCode
from evernote.edam.notestore.NoteStore import NoteFilter, NotesMetadataResultSpec
from evernote.edam.type.ttypes import Note, Resource, Data
from evernote.edam.userstore.constants import EDAM_VERSION_MAJOR, EDAM_VERSION_MINOR

import pathmagic

with pathmagic.context():
    from func.configpr import cfp, inifilepath
    from func.first import dirlog
    from func.logme import log
    from func.nettools import trycounttimes2


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

    @trycounttimes2('evernote服务器', maxtimes = 60, maxsecs = 60)
    def getnotestore():
        global note_store
        if note_store is not None:
            # log.info(f'note_store健壮存在：{note_store}')
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
    # global log
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
                nbody += "<en-media type=\"%s\" hash=\"%s\" align=\"center\" /><br />" % (resource.mime, str1)
    nbody += neirong
    nbody += "</en-note>"

    note.content = nbody
    # print (note.content)

    # Finally, send the new note to Evernote using the updateNote method
    # The new Note object that is returned will contain server-generated
    # attributes such as the new note's unique GUID.
    @trycounttimes2('evernote服务器')
    def updatenote(notesrc):
        updated_note = get_notestore().updateNote(notesrc)
        evernoteapijiayi()
        log.info('成功更新了笔记《%s》，guid：%s。' % (updated_note.title, updated_note.guid))

    updatenote(note)
    # trytimes = 3
    # sleeptime = 20
    # for i in range(trytimes):
    #     try:
    #         if notestore is None:
    #             log.info(f'notestore失效，重新构建evernote服务器连接以便进行笔记《{note.title}》的内容更新操作。')
    #             updated_note = get_notestore().updateNote(note)
    #         else:
    #             updated_note = notestore.updateNote(note)
    #         evernoteapijiayi()
    #         log.info('成功更新了笔记《%s》，guid：%s。' % (updated_note.title, updated_note.guid))
    #         break
    #     except Exception as eee:
    #         log.critical("第%d次（最多尝试%d次）更新笔记《%s》时失败，将于%d秒后重试。%s"
    #                      % (i + 1, trytimes, note.title, sleeptime, eee))
    #         if i == (trytimes - 1):
    #             log.critical(f'更新笔记《{note.title}》失败，只好无功而返。')
    #             raise eee
    #         time.sleep(sleeptime)


def tablehtml2evernote(dataframe, tabeltitle='表格标题', withindex=True):
    pd.set_option('max_colwidth', 200)
    df = pd.DataFrame(dataframe)
    outstr = df.to_html(justify='center', index=withindex).replace('class="dataframe">', 'align="center">'). \
        replace('<table', '\n<h3 align="center">%s</h3>\n<table' % tabeltitle).replace('<th></th>', '<th>&nbsp;</th>')
    # print(outstr)
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
        notelist = note_store.findNotesMetadata(tokenfnfn, notefilter, 0, notecount, notemetaspec)
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
        log.info('笔记《' + notetitle + '》在笔记本《' + parentnotebook.name + '》中创建成功。')
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
                     header=None, usecols=[0, 1, 2, 3, 4],
                     names=['asctime', 'name', 'filenamefuncName', 'threadNamethreadprocess', 'levelnamemessage'],
                     na_filter=True, parse_dates=[0],
                     skip_blank_lines=True, skipinitialspace=True)
    # print(df.describe())
    # print(df.shape[0])
    # dfapi2 = df[df.levelnamemessage.str.contains('动用了Evernote API')][['asctime', 'levelnamemessage']]
    dfapi2 = df[df.levelnamemessage.str.contains('动用了Evernote API').values == True][['asctime', 'levelnamemessage']]
    # print(dfapi2.shape[0])
    # print(dfapi2.head(50))
    if dfapi2.shape[0] == 0:
        log.info('日志文件中还没有API的调用记录')
        return False
    dfapi2['asctime'] = dfapi2['asctime'].apply(lambda x : pd.to_datetime(x))
    dfapi2['counts'] = dfapi2['levelnamemessage'].apply(lambda x: int(re.findall('(?P<counts>\d+)', x)[0]))
    # del dfapi2['levelnamemessage']
    # print(dfapi2.tail())
    jj = dfapi2[dfapi2.asctime == dfapi2.asctime.max()]['counts'].iloc[-1]
    # print(type(jj))
    # print(jj)
    result = [dfapi2.asctime.max(), int(jj)]
    # print(dfapi2[dfapi2.asctime == dfapi2.asctime.max()])
    print(result)
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
    cfp.set('evernote', 'apilasttime', '%s' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    cfp.write(open(inifilepath, 'w', encoding='utf-8'))
    log.info('Evernote API调用次数：%d，写入配置文件%s' % (ENtimes, os.path.split(inifilepath)[1]))


def evernoteapiclearatzero():
    """
    evernote API的调用次数过整点清零
    :rtype: None
    :return:
    """
    global ENAPIlasttime, ENtimes
    apilasttimehouzhengdian = pd.to_datetime(
        (ENAPIlasttime + datetime.timedelta(hours=1)).strftime('%Y-%m-%d %H:00:00'))
    now = datetime.datetime.now()
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
    evernoteapiclearatzero()
    if (ENtimes >= 290) or (note_store is None):
        now = datetime.datetime.now()
        # 强制小时数加一在零点的时候会出错，采用timedelta解决问题
        nexthour = now + datetime.timedelta(hours=1)
        # zhengdian = pd.to_datetime(
        #     '%04d-%02d-%02d %02d:00:00' % (nexthour.year, nexthour.month, nexthour.day, nexthour.hour))
        zhengdian = nexthour.replace(minute=0, second=0,microsecond=0)
        secondsaferzhengdian = np.random.randint(0, 50)
        sleep_seconds = (zhengdian - now).seconds + secondsaferzhengdian
        starttimeafterzhengdian = pd.to_datetime(zhengdian + datetime.timedelta(seconds=secondsaferzhengdian))
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


# print('我是evernt啊')
# global cfp
token = cfp.get('evernote', 'token')
ENtimes = cfp.getint('evernote', 'apicount')
ENAPIlasttime = pd.to_datetime(cfp.get('evernote', 'apilasttime'))
apitime = getapitimesfromlog()
# print(ENAPIlasttime, apitime)
if apitime:
    # 比较ini和log中API存档的时间，解决异常退出时调用次数无法准确反映的问题
    if apitime[0] > ENAPIlasttime:
        diff = apitime[0] - ENAPIlasttime
    else:
        diff = ENAPIlasttime - apitime[0]
    # print(diff.seconds)
    if diff.seconds > 60:
        log.info('程序上次异常退出，调用log中的API数据[%s,%d]' % (str(apitime[0]), apitime[1]))
        ENAPIlasttime = apitime[0]
        ENtimes = apitime[1] + 1
evernoteapiclearatzero()

# writeini()

if __name__ == '__main__':
    print(f'开始测试文件\t{__file__}')
    nost = get_notestore()
    print(nost)
    writeini()
    print('Done.')
