# encoding:utf-8
"""
印象笔记相关功能函数
"""

import os, re, datetime, time, hashlib, binascii, \
    evernote.edam.type.ttypes as Ttypes, evernote.edam.error.ttypes as Etypes, \
    evernote.edam.userstore.constants as UserStoreConstants, \
    evernote.edam.notestore.NoteStore as NoteStore, pandas as pd, numpy as np
from evernote.api.client import EvernoteClient
from func.configpr import getcfp, cfp, inifilepath
from func.logme import log
from func.first import dirlog


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

    global log
    # auth_token = token
    cfp, inipath = getcfp('everwork')
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

    trytimes = 3
    sleeptime = 20
    for i in range(trytimes):
        try:
            userstore = client.get_user_store()
            evernoteapijiayi()
            version_ok = userstore.checkVersion(
                "Evernote EDAMTest (Python)",
                UserStoreConstants.EDAM_VERSION_MAJOR,
                UserStoreConstants.EDAM_VERSION_MINOR
            )
            if not version_ok:
                log.critical('Evernote API版本过时，请更新之！程序终止并退出！！！')
                exit(1)
            # print("Is my Evernote API version up to date? ", str(version_ok))
            note_store = client.get_note_store()
            evernoteapijiayi()
            # log.debug('成功连接Evernote服务器！构建notestore：%s' % note_store)
            return note_store
        except Exception as eee:
            log.critical("第%d次（最多尝试%d次）连接evernote服务器时失败，将于%d秒后重试。%s"
                         % (i + 1, trytimes, sleeptime, eee))
            if i == (trytimes - 1):
                log.critical('evernote服务器连接失败，只好无功而返。')
                raise eee
            time.sleep(sleeptime)


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
    global log
    note = Ttypes.Note()
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
        data = Ttypes.Data()  # 必须要重新构建一个Data（），否则内容不会变化
        data.size = len(image)
        data.bodyHash = imghash
        data.body = image
        resource = Ttypes.Resource()
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
    trytimes = 3
    sleeptime = 20
    for i in range(trytimes):
        try:
            if notestore is None:
                log.info(f'notestore失效，重新构建evernote服务器连接以便进行笔记《{note.title}》的内容更新操作。')
                updated_note = get_notestore().updateNote(note)
            else:
                updated_note = notestore.updateNote(note)
            # evernoteapijiayi()
            log.info('成功更新了笔记《%s》，guid：%s。' % (updated_note.title, updated_note.guid))
            break
        except Exception as eee:
            log.critical("第%d次（最多尝试%d次）更新笔记《%s》时失败，将于%d秒后重试。%s"
                         % (i + 1, trytimes, note.title, sleeptime, eee))
            if i == (trytimes - 1):
                log.critical(f'更新笔记《{note.title}》失败，只好无功而返。')
                raise eee
            time.sleep(sleeptime)


def tablehtml2evernote(dataframe, tabeltitle, withindex=True):
    pd.set_option('max_colwidth', 200)
    df = pd.DataFrame(dataframe)
    outstr = df.to_html(justify='center', index=withindex).replace('class="dataframe">', 'align="center">'). \
        replace('<table', '\n<h3 align="center">%s</h3>\n<table' % tabeltitle).replace('<th></th>', '<th>&nbsp;</th>')
    # print(outstr)
    return outstr


def findnotefromnotebook(token, notebookguid, titlefind, notecount=10000):
    """
    列出笔记本中的笔记信息
    :param note_store:
    :param token:
    :param notebookguid:
    :param titlefind:
    :param notecount:
    :return:
    """
    note_store = get_notestore()
    notefilter = NoteStore.NoteFilter()
    notefilter.notebookGuid = notebookguid
    notemetaspec = NoteStore.NotesMetadataResultSpec(includeTitle=True, includeContentLength=True, includeCreated=True,
                                                     includeUpdated=True, includeDeleted=True,
                                                     includeUpdateSequenceNum=True,
                                                     includeNotebookGuid=True, includeTagGuids=True,
                                                     includeAttributes=True,
                                                     includeLargestResourceMime=True, includeLargestResourceSize=True)
    ournotelist = note_store.findNotesMetadata(token, notefilter, 0, notecount, notemetaspec)
    evernoteapijiayi()

    # print ourNoteList.notes[-1].title  #测试打印指定note的标题
    # print note_store.getNoteContent(ourNoteList.notes[-1].guid)  #测试打印指定note的内容
    # note = note_store.getNote(auth_token, ourNoteList.notes[9].guid, True, True, True, True)  #获得Note并打印其中的值
    # p_noteattributeundertoken(note)
    # print ourNoteList.notes[5] #打印NoteMetadata

    items = []
    for note in ournotelist.notes:
        if note.title.find(titlefind) >= 0:
            item = list()
            item.append(note.guid)
            item.append(note.title)
            # print(note.guid, note.title)
            # p_noteattributeundertoken(note)
            items.append(item)

    return items


def timestamp2str(timestamp):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))


def getapitimesfromlog():
    """
    从log中提取API调用次数
    :return:
    """
    global dirlog, log
    df = pd.read_csv(dirlog, sep='\t',  # index_col= False,
                     header=None, usecols=[0, 1, 2, 3, 4],
                     names=['asctime', 'name', 'filenamefuncName', 'threadNamethreadprocess', 'levelnamemessage'],
                     na_filter=True, parse_dates=[0],
                     skip_blank_lines=True, skipinitialspace=True)
    dfapi2 = df[df.levelnamemessage.str.contains('动用了Evernote API').values == True][['asctime', 'levelnamemessage']]
    if dfapi2.shape[0] == 0:
        log.info('log文进中还没有API的调用记录')
        return False
    # print(dfapi2.tail())
    dfapi2['counts'] = dfapi2['levelnamemessage'].apply(lambda x: int(re.findall('(?P<counts>\d+)', x)[0]))
    # del dfapi2['levelnamemessage']
    # print(dfapi2.tail())
    jj = dfapi2[dfapi2.asctime == dfapi2.asctime.max()]['counts'].iloc[-1]
    # print(type(jj))
    # print(jj)
    result = [dfapi2.asctime.max(), int(jj)]
    print(dfapi2[dfapi2.asctime == dfapi2.asctime.max()])
    # print(result)
    return result


def writeini():
    """
    evernote API调用次数写入配置文件以备调用。又及，函数写在这里还有个原因是global全局变量无法跨文件传递。
    :return:
    """
    global ENtimes, cfp, inifilepath, log
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
    global ENAPIlasttime
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
    global ENtimes, cfp, inifilepath, log
    log.debug('动用了Evernote API %s 次……' % ENtimes)
    ENtimes += 1
    evernoteapiclearatzero()
    if ENtimes >= 290:
        now = datetime.datetime.now()
        # 强制小时数加一在零点的时候会出错，采用timedelta解决问题
        nexthour = now + datetime.timedelta(hours=1)
        zhengdian = pd.to_datetime(
            '%4d-%2d-%2d %2d:00:00' % (nexthour.year, nexthour.month, nexthour.day, nexthour.hour))
        secondsaferzhengdian = np.random.randint(0, 300)
        sleep_seconds = (zhengdian - now).seconds + secondsaferzhengdian
        starttimeafterzhengdian = pd.to_datetime(zhengdian + datetime.timedelta(seconds=secondsaferzhengdian))
        log.info(f'Evernote API 调用已达{ENtimes:d}次，休息{sleep_seconds:d}秒，待{str(starttimeafterzhengdian)}再开干……')
        writeini()
        time.sleep(sleep_seconds)
        ENtimes = 0


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


def makenote(token, notestore, notetitle, notebody='真元商贸——休闲食品经营专家', parentnotebook=None):
    """
    创建一个note
    :param token:
    :param notestore:
    :param notetitle:
    :param notebody:
    :param parentnotebook:
    :return:
    """
    global log
    nbody = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
    nbody += "<!DOCTYPE en-note SYSTEM \"http://xml.evernote.com/pub/enml2.dtd\">"
    nbody += "<en-note>%s</en-note>" % notebody

    # Create note object
    ournote = Ttypes.Note()
    ournote.title = notetitle
    ournote.content = nbody

    # parentNotebook is optional; if omitted, default notebook is used
    if parentnotebook and hasattr(parentnotebook, 'guid'):
        ournote.notebookGuid = parentnotebook.guid

    # Attempt to create note in Evernote account
    try:
        note = notestore.createNote(token, ournote)
        evernoteapijiayi()
        log.info('笔记《' + notetitle + '》在笔记本《' + parentnotebook.name + '》中创建成功。')
        return note
    except Etypes.EDAMUserException as usere:
        # Something was wrong with the note data
        # See EDAMErrorCode enumeration for error code explanation
        # http://dev.evernote.com/documentation/reference/Errors.html#Enum_EDAMErrorCode
        log.critical("用户错误！%s" % str(usere))
    except Etypes.EDAMNotFoundException as notfounde:
        # Parent Notebook GUID doesn't correspond to an actual notebook
        print("无效的笔记本guid（识别符）！%s" % str(notfounde))
    except Etypes.EDAMSystemException as systeme:
        if systeme.errorCode == Etypes.EDAMErrorCode.RATE_LIMIT_REACHED:
            log.critical("API达到调用极限，需要 %d 秒后重来" % systeme.rateLimitDuration)
            exit(1)
        else:
            log.critical('创建笔记时出现严重错误：' + str(systeme))
            exit(2)


# writeini()

if __name__ == '__main__':
    log.info('测试evernt')
    get_notestore()
    writeini()
