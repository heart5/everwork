# encoding:utf-8
# # evernote相关功能函数集

"""
evernote或印象笔记相关功能函数
"""

# ## 引入重要库

import os
import sys
import binascii
import datetime
import hashlib
import mimetypes
import re
import time
import traceback
import inspect
import numpy as np
import pandas as pd
import http
import ssl
from bs4 import BeautifulSoup
from evernote.api.client import EvernoteClient
from evernote.edam.error.ttypes import EDAMNotFoundException, EDAMSystemException, EDAMUserException, EDAMErrorCode
from evernote.edam.notestore.NoteStore import NoteFilter, NotesMetadataResultSpec
from evernote.edam.type.ttypes import Note, NoteAttributes, Resource, ResourceAttributes, Data, Notebook
from evernote.edam.userstore.constants import EDAM_VERSION_MAJOR, EDAM_VERSION_MINOR

import pathmagic

with pathmagic.context():
    from func.configpr import getcfpoptionvalue, setcfpoptionvalue, removesection
    from func.first import dirlog, dirmainpath
    from func.logme import log
    from func.nettools import trycounttimes2
    from func.sysfunc import convertframe2dic, not_IPython, extract_traceback4exception, set_timeout, after_timeout
    from func.datetimetools import timestamp2str
    # from etc.getid import getid

# print(f"{__file__} is loading now...")

# ## 函数集合

# ### def gettoken():

def gettoken():
    if (china := getcfpoptionvalue('everwork', 'evernote', 'china')):
        # print(f"china value:\t{china}")
        auth_token = getcfpoptionvalue('everwork', 'evernote', 'tokenchina')  # 直接提取，唯一使用
    else:
        # print(f"china value:\t{china}")
        auth_token = getcfpoptionvalue('everwork', 'evernote', 'token')  # 直接提取，唯一使用

    return auth_token


# ### def get_notestore(forcenew=False):

def get_notestore(forcenew=False):
    """
    获取notestore实例以供使用
    :return: NS实例
    """
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
    # auth_token = cfp.get('evernote', 'token')  # 直接提取，唯一使用
    # print("start debugging for evernttest")
    auth_token = gettoken()
    # print(auth_token)

    if auth_token == "your developer token":
        print("Please fill in your developer token\nTo get a developer token, visit "
              "https://www.evernote.com/api/DeveloperToken.action")
        log.critical('请填入从evernote官方网站申请的有效token！程序终止并退出！！！')
        exit(1)

    # To access Sandbox service, set sandbox to True
    # To access production (International) service, set both sandbox and china to False
    # To access production (China) service, set sandbox to False and china to True
    sandbox = False
    # china = False

    # Initial development is performed on our sandbox server. To use the production
    # service, change sandbox=False and replace your
    # developer token above with a token from
    # https://www.evernote.com/api/DeveloperToken.action

    china = getcfpoptionvalue('everwork', 'evernote', 'china')
    client = EvernoteClient(token=auth_token, sandbox=sandbox, china=china)

    servname = ("印象笔记", 'evernote')[china is False]
    #     print(china, servname)
    @trycounttimes2(f'{servname}服务器')
    def getnotestore(forcenewinner):
        global note_store
        # print(note_store)
        if (note_store is not None) and (not forcenewinner):
            # log.info(f'note_store已健壮存在：{note_store}')
            return note_store
        userstore = client.get_user_store()
        # print(userstore)
        # evernoteapijiayi()
        # print("I'm here now.")
        # print(EDAM_VERSION_MAJOR, EDAM_VERSION_MINOR)
        version_ok = userstore.checkVersion(
            # "Evernote EDAMTest (Python)",
            "Evernote EDAMTest (Python)",
            EDAM_VERSION_MAJOR,
            EDAM_VERSION_MINOR)
        # print("I'm here second.")
        # print(version_ok)
        if not version_ok:
            log.critical('Evernote API版本过时，请更新之！程序终止并退出！！！')
            exit(1)
        # print("Is my Evernote API version up to date? ", str(version_ok))
        global en_username
        myuser = userstore.getUser()
        en_username = myuser.username
#         print(en_username)
        note_store = client.get_note_store()
        # print(note_store)
        evernoteapijiayi()
        log.info(f'成功连接Evernote服务器！构建notestore：{note_store}')
        return note_store

    try:
        outns = getnotestore(forcenew)
    except Exception as eeee:
        log.critical(f"百般尝试，不得而入。再来一次，不行就算了。{eeee}")
        outns = getnotestore(True)

    return outns


note_store = None
en_username = None


# ###  def imglist2note(notestore, reslist, noteguid, notetitle, neirong=''):

def imglist2note(notestore, reslist, noteguid, notetitle, neirong=''):
    """
    更新note内容，可以包含图片等资源类文件列表
    :param notestore:
    :param reslist:
    :param noteguid:
    :param notetitle:
    :param neirong:object
    :return:
    """
    note = Note()
    noteattrib = NoteAttributes()
    global en_username
    if en_username is not None:
        noteattrib.author = en_username
        print(f"I'm here while creating the note, for evernote user {en_username}")
    note.attributes = noteattrib
    note.guid = noteguid.lower()
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
    for res in reslist:
        """
        必须要重新构建一个Data（），否则内容不会变化
        Data只有三个域：bodyHash（用MD5进行hash得到的值）、size（body的字节长度）和body（字节形式的内容本身）
        """
        resactual = open(res, 'rb').read()
        md5 = hashlib.md5()
        md5.update(resactual)
        reshash = md5.digest()
        data = Data()
        data.size = len(resactual)
        data.bodyHash = reshash
        data.body = resactual
        """
        Resource需要常用的域：guid、noteGuid、data（指定上面的Data）、mime（需要设定）、attributes（可以设定附件的原文件名）
        """
        resource = Resource()
#         resource.mime = 'image/png'
        if (mtype := mimetypes.guess_type(res)[0]) is None:
            logstr = f"文件《{res}》的类型无法判断"
            log.critical(logstr)
            print(logstr)
            mtype = 'file/unkonwn'
#             continue
        resource.mime = mtype
#         print(mtype)
        resource.data = data
        """
        NoteAttributes常用的域：sourceURL、fileName和经纬度、照相机等信息
        """
        resattrib = ResourceAttributes()
        resattrib.fileName = res
        resource.attributes = resattrib
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
            #             print(resource.guid)
            if resource.mime.startswith('image') or True:
                hexhash = binascii.hexlify(resource.data.bodyHash)
                str1 = "%s" % hexhash  # b'cd34b4b6c8d9279217b03c396ca913df'
                # print (str1)
                str1 = str1[2:-1]  # cd34b4b6c8d9279217b03c396ca913df
                # print (str1)
                nbody += "<en-media type=\"%s\" hash=\"%s\" align=\"center\" longdesc=\"%s\" /><br />%s<hr />" % (
                    resource.mime, str1, resource.attributes.fileName, resource.attributes.fileName)
    # neirong= "<pre>" + neirong + "</pre>"

    # 去除控制符
    neirong = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f]', '', neirong)
    neirong = re.sub('&', 'and连接符', neirong)

    nbody += neirong
    nbody += "</en-note>"

    # ！！！严重错误，过滤\x14时把回车等符号都杀了！！！
    # nbodynotasciilst = [hex(ord(x)) for x in nbody if ord(x) < 32]
    # print(f"存在不可显示字符串：{''.join(nbodynotasciilst)}")
    # nbodylst = [x for x in nbody if ord(x) >= 32]
    # nbody = ''.join(nbodylst)
    note.content = nbody
    # log.info(f"新构笔记文字部分长度为：\t{len(nbody)}")
    # print(note.content[:100])

    # Finally, send the new note to Evernote using the updateNote method
    # The new Note object that is returned will contain server-generated
    # attributes such as the new note's unique GUID.
    @trycounttimes2('evernote服务器，更新笔记。')
    def updatenote(notesrc):
        nsinner = get_notestore()
        token = gettoken()
        updated_note = nsinner.updateNote(token, notesrc)
        evernoteapijiayi()
        log.info('成功更新了笔记《%s》，guid：%s。' %
                 (updated_note.title, updated_note.guid))

    updatenote(note)


# ###  def tablehtml2evernote(dataframe, tabeltitle='表格标题', withindex=True, setwidth=True):

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


# ###  def findnotefromnotebook(notebookguid, titlefind='', notecount=10000):

def findnotefromnotebook(notebookguid, titlefind='', notecount=10000):
    """
    列出笔记本中包含某关键词的笔记信息
    :param tokenfnfn: token
    :param notebookguid: 笔记本的guid
    :param titlefind: 关键词
    :param notecount: 搜索结果数量限值
    :return: 列表，包含形如[noteguid, notetitle, note.updateSequenceNum]的list
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
    def findnote(startnum: int = 0, maxnum: int = 250):
        tokenfnfn = gettoken()
        # log.info("I'm here now too.")
        notelist = note_store.findNotesMetadata(
            tokenfnfn, notefilter, startnum, maxnum, notemetaspec)
        # log.info("I'm here now three.")
        evernoteapijiayi()
        return notelist

    width = 250
    items = list()
    ournotelist = findnote()
    print(ournotelist.totalNotes)
    items.extend([[note.guid, note.title, note.updateSequenceNum] for note in ournotelist.notes if
         note.title.find(titlefind) >= 0])

    if ournotelist.totalNotes > notecount:
        numtobesplit = notecount
    else:
        numtobesplit = ournotelist.totalNotes

    spllst = [(i * width, (width, numtobesplit - width * i)[numtobesplit - width * (i + 1) < 0], numtobesplit) for i in range((numtobesplit // width) + 1)]
    if len(spllst) >= 1:
        print(spllst)
        for numbt in spllst[1:]:
            print(numbt)
            ournotelist = findnote(numbt[0], numbt[1])
            items.extend([[note.guid, note.title, note.updateSequenceNum] for note in ournotelist.notes if
                 note.title.find(titlefind) >= 0])

    return items


# ###  def getnotecontent(guid: str):

def getnotecontent(guid: str):
    """
    获取笔记内容
    :param guid:
    :return:
    """
    ns = get_notestore()
    soup = BeautifulSoup(ns.getNoteContent(guid), "html.parser")
    # print(soup)

    return soup


# ###  def getnoteresource(guid: str):

def getnoteresource(guid: str):
    """
    获取笔记附件
    :param guid:
    :return:
    """
    ns = get_notestore()
    note = ns.getNote(gettoken(), guid, True, True, False, False)
    evernoteapijiayi()
    resultlst = list()
    for resitem in note1.resources:
        sonlst = list()
        sonlst.append(resitem.attributes.fileName)
        sonlst.append(resitem.data.body.decode())
        resultlst.append(sonlst)
    # print(soup)

    return resultlst


# ###  def createnotebook(nbname: str, stack='fresh'):

def createnotebook(nbname: str, stack='fresh'):
    notebook = Notebook()
    notebook.name = nbname
    notebook.stack = stack

    return get_notestore().createNotebook(gettoken(), notebook)


# ###  def makenote(tokenmn, notestore, notetitle, notebody='真元商贸——休闲食品经营专家', parentnotebook=None):

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
    if type(parentnotebook) is str:
        parentnotebook = notestore.getNotebook(gettoken(), parentnotebook)
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


# ### def makenote2(notetitle, notebody='真元商贸——休闲食品经营专家', parentnotebook=None):

def makenote2(notetitle, notebody='真元商贸——休闲食品经营专家', parentnotebook=None):
    """
    创建note，封装token和notestore
    :param notetitle:
    :param notebody:
    :param parentnotebook:
    :return:
    """

    notestore = get_notestore()
    nbody = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
    nbody += "<!DOCTYPE en-note SYSTEM \"http://xml.evernote.com/pub/enml2.dtd\">"
    nbody += "<en-note>%s</en-note>" % notebody

    # Create note object
    ournote = Note()
    ournote.title = notetitle
    ournote.content = nbody

    # parentNotebook is optional; if omitted, default notebook is used
    if type(parentnotebook) is str:
        try:
            parentnotebook = notestore.getNotebook(gettoken(), parentnotebook)
        except:
            log.critical(f"新建笔记的笔记本guid属性无效，设置为默认")
            parentnotebook = None
    if parentnotebook and hasattr(parentnotebook, 'guid'):
        ournote.notebookGuid = parentnotebook.guid

    # Attempt to create note in Evernote account
    try:
        note = notestore.createNote(gettoken(), ournote)
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


# ### def evernoteapijiayi():

def evernoteapijiayi():
    """
    evernote api调用次数加一。结合api调用限制，整点或达到限值（貌似是300次每小时）则重构一个继续干。
    """
    cfpapiname = 'everapi'
    nssectionname = 'notestore'
    note_store = get_notestore()
    nsstr4ini = hex(id(note_store))
    nowtime = datetime.datetime.now()
    nowmin = nowtime.minute
    try:
        nowhourini = getcfpoptionvalue(cfpapiname, 'apitimes', "hour")
        # ns首次启动和整点重启（用小时判断）
        if (not (apitimes := getcfpoptionvalue(cfpapiname, nssectionname, nsstr4ini)) or ((nowmin == 0) and (nowhourini != nowtime.hour))):
            if nowmin == 0:
                log.info(f"Evernote API\t{nsstr4ini} 调用次数整点重启^_^")
            else:
                log.info(f"Evernote API\t{nsstr4ini} 新生^_^{inspect.stack()[-1]}")
            #             log.critical(f"Evernote API\t{nsstr4ini} 新生^_^{inspect.stack()[-1]}")
            apitimes = 0
            #         print(nowhourini, nowtime.hour)
        if nowhourini != nowtime.hour:
            setcfpoptionvalue(cfpapiname, 'apitimes', "hour", str(nowtime.hour))
        apitimes += 1
        log.debug(f'动用Evernote API({note_store})次数：\t {apitimes} ')
        setcfpoptionvalue(cfpapiname, nssectionname, nsstr4ini, str(apitimes))
    except Exception as e:
        log.critical(f'{cfpapiname}配置文件存取出现严重错误，试图清除《{nssectionname}》小节下的所有内容。跳过一次api调用计数！')
        log.critical(e)
        removesection(cfpapiname, nssectionname)
        return
    if apitimes >= 290:
        sleepsecs = np.random.randint(0, 50)
        time.sleep(sleepsecs)
        note_store = None
        note_store = get_notestore(forcenew=True)
        log.critical(f'休息{sleepsecs:d}秒，重新构造了一个服务器连接{note_store}继续干……')


# ### def evernoteapijiayi_test():

def evernoteapijiayi_test():
    calllink = [re.findall("^<FrameSummary file (.+), line (\d+) in (.+)>$", str(line)) for line in traceback.extract_stack()]
    if len(calllink) > 0:
        calllinks = str(calllink[-1])
#         print(calllinks)
    else:
        calllinks = ""
    note_store = get_notestore()
    nsstr4ini = str(id(note_store))
    nowtime = datetime.datetime.now()
    nowmin = nowtime.minute
    nowhourini = getcfpoptionvalue('everapi', 'apitimes', "hour")
    # ns首次启动和整点重启（用小时判断）
    if (not (apitimes := getcfpoptionvalue('everapi', 'apitimes', nsstr4ini)) or ((nowmin == 0) and (nowhourini != nowtime.hour))):
        if nowmin == 0:
            log.critical(f"Evernote API\t{nsstr4ini} 调用次数整点重启^_^{calllinks}")
        else:
            log.critical(f"Evernote API\t{nsstr4ini} 新生^_^{calllinks}")
        apitimes = 0
    if nowhourini != nowtime.hour:
        setcfpoptionvalue('everapi', 'apitimes', "hour", str(nowtime.hour))
    apitimes += 1
    log.debug(f'动用Evernote API({note_store})次数：\t {apitimes} ')
    setcfpoptionvalue('everapi', 'apitimes', nsstr4ini, str(apitimes))
    if apitimes >= 290:
        sleepsecs = np.random.randint(0, 50)
        time.sleep(sleepsecs)
        note_store = None
        note_store = get_notestore(forcenew=True)
        log.critical(f'休息{sleepsecs:d}秒，重新构造了一个服务器连接{note_store}继续干……{calllinks}')


# ### def p_notebookattributeundertoken(notebook):

# @use_logging()
def p_notebookattributeundertoken(notebook):
    """
    测试笔记本（notebook）数据结构每个属性的返回值,开发口令（token）的方式调用返回如下
    :param notebook:
    :return:dict
    """
    rstdict = dict()
    rstdict['名称'] = notebook.name  # phone
    rstdict['guid'] = notebook.guid  # f64c3076-60d1-4f0d-ac5c-f0e110f3a69a
    rstdict['更新序列号'] = notebook.updateSequenceNum  # 8285
    rstdict['默认笔记本']: bool = notebook.defaultNotebook  # False
    # print(type(rstdict['默认笔记本']), rstdict['默认笔记本'])
    if (china := getcfpoptionvalue('everwork', 'evernote', 'china')):
        shijianchushu = 1
    else:
        shijianchushu = 1000
    ntsct = notebook.serviceCreated /1000
    ntsut = notebook.serviceUpdated /1000
    # print(ntsct, ntsut, timestamp2str(ntsct), timestamp2str(ntsut))
    rstdict['创建时间'] = pd.to_datetime(timestamp2str(ntsct))  # 2010-09-15 11:37:43
    rstdict['更新时间'] = pd.to_datetime(timestamp2str(ntsut))  # 2016-08-29 19:38:24
    rstdict['笔记本组'] = notebook.stack  # 手机平板

    # print('发布中\t', notebook.publishing)     # 这种权限的调用返回None
    # print('发布过\t', notebook.published)      # 这种权限的调用返回None

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

    # print(rstdict)

    return rstdict


# ### def p_noteattributeundertoken(note):

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


# ### def findnotebookfromevernote():

def findnotebookfromevernote():
    """
    列出所有笔记本
    :return: rstdf，
    DataFrame格式，dtypes
    创建时间     datetime64[ns]
    名称               object
    更新序列号           float64
    更新时间     datetime64[ns]
    笔记本组             object
    默认笔记本              bool
    dtype: object
    """
    global note_store
    note_store = get_notestore()
    notebooks = note_store.listNotebooks()
    # p_notebookattributeundertoken(notebooks[-1])

    rstdf = pd.DataFrame()
    for x in notebooks:
        rstdf = rstdf.append(pd.Series(p_notebookattributeundertoken(x)), ignore_index=True)

    # print(rstdf)

    rstdf['默认笔记本'] = rstdf['默认笔记本'].astype(bool)
    rstdf.set_index('guid', inplace=True)

    return rstdf


# ### def readinifromnote():

@set_timeout(180, after_timeout)
@trycounttimes2('evernote服务器', maxtimes=20, maxsecs=10)
def readinifromnote():
    """
    更新动态化配置到本地ini文件，确保数据新鲜
    :return:
    """
    # cfpeverwork, cfpeverworkpath = getcfp('everwork')
    # noteguid_inifromnote = cfpeverwork.get('evernote', 'ininoteguid')
    if not (ininoteupdatenum := getcfpoptionvalue('eversys', 'evernote', 'ininoteupdatenum')):
        ininoteupdatenum = 0
    note_store = get_notestore()
    # noteguid_inifromnote = 'e0565861-db9e-4efd-be00-cbce06d0cf98'
    noteguid_inifromnote = getcfpoptionvalue('everwork', 'evernote', 'ininoteguid')
    # print(noteguid_inifromnote)
    try:
        note = note_store.getNote(noteguid_inifromnote, True, True, False, False)
    except (http.client.RemoteDisconnected, TimeoutError, ssl.SSLEOFError) as e:
        eee_type, eee_value, eee_traceback = sys.exc_info()
        tbtuple = (eee_type, eee_value, [str(x) for x in traceback.extract_tb(eee_traceback)])
        sleeptime = 5
        print(extract_traceback4exception(tbtuple, "readinifromnote",
              sleeptime=sleeptime))
        # 避免log污染，只打印，不记录
        # log.critical(f"读取evernote笔记配置文件时出错。\t{e}")
        # 返回None，相当于跳过一次note参数获取；不采用raise
        # e，那样trycounttimes2生效，非获取有效值不可，耽搁事务推进
        return
    # print(note.updateSequenceNum)
    if int(note.updateSequenceNum) == ininoteupdatenum:
        # print(f'配置笔记无变化，不对本地化的ini配置文件做更新。')
        return
    soup = BeautifulSoup(note_store.getNoteContent(noteguid_inifromnote), "html.parser")
    # print(soup)
    ptn = u'<div>(.*?)</div>'
    # ptn = u'<div>'
    itemsource = re.findall(ptn, str(soup))
    # print(itemsource)
    items = [x for x in itemsource if not re.search('<.*?>', x)]
    print(items)
    fileobj = open(str(dirmainpath / 'data' / 'everinifromnote.ini'), 'w',
                   encoding='utf-8')
    for item in items:
        fileobj.write(item + '\n')
    fileobj.close()

    setcfpoptionvalue('eversys', 'evernote', 'ininoteupdatenum', str(note.updateSequenceNum))
    log.info(f'配置笔记内容有变化，更新本地化的ini配置文件。')


def getinivaluefromnote(section, option):
    readinifromnote()

    return getcfpoptionvalue('everinifromnote', section, option)


def writeini2note():
    pass

def findsomenotest2showornote(nbguid, keyword, newnote=False):
    """
    获取指定笔记本中主题包含某关键词的笔记
    :param nbguid: 笔记本guid
    :param keyword: 关键词
    :param newnote: 是否生成新的笔记来存储显示查询结果
    :return: list，包含[guid, title, updatenum]的list
    """
    notesfind = findnotefromnotebook(nbguid, keyword)
    if newnote:
        tokenfst = getcfpoptionvalue('everwork', 'evernote', 'token')
        makenote(tokenfst, get_notestore(), f"“《{keyword}》”笔记列表", str(notesfind))
    else:
        print(notesfind)

    return notesfind


def getsampledffromdatahouse(keyword: str, notebookstr='datahouse', firstcolumn=True):
    """
    封装出直接获取示例数据集的函数
    :param keyword: 关键词
    :param notebookstr: 笔记本名称，默认是“datahouse”
    :param firstcolumn: 首行是否包含标题
    :return: DataFrame
    """
    ntsdf = findnotebookfromevernote()
    ntguid = ntsdf.loc[ntsdf.名称 == notebookstr].index.values[-1]
    noteguid = findsomenotest2showornote(ntguid, keyword)[0][0]
    soup = getnotecontent(noteguid)
    soupstrlst = [item.text.split(',') for item in soup.find_all('div') if len(item.text) > 0]
    if firstcolumn:
        return pd.DataFrame(soupstrlst[1:], columns=soupstrlst[0])
    else:
        return pd.DataFrame(soupstrlst)

# token = getcfpoptionvalue('everwork', 'evernote', 'token')
# print(token)
# ENtimes, ENAPIlasttime = enapistartlog()
# evernoteapiclearatzero()


# # 主函数

if __name__ == '__main__':
    if not_IPython():
        log.info(f'开始运行文件\t{__file__}……')
    nost = get_notestore()
    print(nost)
    evernoteapijiayi_test()
    # readinifromnote()
    # writeini()
    # ntdf = findnotebookfromevernote()
    # print(ntdf)
    # print(getsampledffromdatahouse('火界'))

    # 查找主题包含关键词的笔记
    notification_guid =  '4524187f-c131-4d7d-b6cc-a1af20474a7f'
#     shenghuo_guid =  '7b00ceb7-1762-4e25-9ba9-d7e952d57d8b'
#     smsnbguid = "25f718c1-cb76-47f6-bdd7-b7b5ee09e445"
    findnoteguidlst = findnotefromnotebook(notification_guid, titlefind='tmux.conf', notecount=1433)
    print(len(findnoteguidlst))
    print(findnoteguidlst)
#     findnoteguidlst = findsomenotest2showornote(notification_guid, 'data')
#     print(findnoteguidlst)

    # 测试包含文件资源的笔记更新
#     samplenoteguid = "962f0358-7c7a-4dfd-968d-14dd161a3a39"
#     pylst = [fn for fn in os.listdir() if fn.endswith(".py") or fn.endswith('.txt')]
#     imglist2note(nost, pylst, samplenoteguid, "包含附件的笔记", neirong='仅仅为了存在')

    # 显示笔记内容，源码方式
    # '39c0d815-df23-4fcc-928d-d9193d5fff93' 转账
    # 'ba9dcaa7-9a8f-4ee8-86a6-fd788b71d411' 微信号
    # findnotecontent = getnotecontent('39c0d815-df23-4fcc-928d-d9193d5fff93' )
    # print(f"{findnotecontent}")

    # # 将notebooklst.txt内容更新至新建的笔记中
    # filetitle = '笔记本列表'
    # filepath = dirmainpath / 'notebooklst.txt'
    # dffile = open(filepath)
    # neirong = dffile.read()
    # dffile.close()
    # makenote(token, nost,filetitle, neirong)

    # # makenote(token, nost, '转账记录笔记guid', str(notefind))
    if not_IPython():
        log.info(f"完成文件{__file__}\t的运行")

