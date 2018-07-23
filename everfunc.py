#  encoding:utf-8

"""
import大集合
everwork的各种函数
"""

import time, datetime, calendar as cal, hashlib, binascii, re, os, socket, random, email, imaplib, subprocess, locale, \
    threading, html, struct, ssl, itertools, \
    logging as lg, logging.handlers as lgh, pandas as pd, sqlite3 as lite, matplotlib.pyplot as plt, \
    evernote.edam.type.ttypes as Ttypes, evernote.edam.error.ttypes as Etypes, \
    evernote.edam.userstore.constants as UserStoreConstants, \
    evernote.edam.notestore.NoteStore as NoteStore
from pylab import *
from configparser import ConfigParser
from matplotlib.ticker import MultipleLocator, FuncFormatter
from mpl_toolkits.mplot3d import Axes3D
from evernote.api.client import EvernoteClient
from pandas.tseries.offsets import *
from bs4 import BeautifulSoup
from os import listdir
from os.path import isfile, join
from odps.df import DataFrame
from threading import Timer
from multiprocessing import Process, Pool, Queue


def dirbuildfirst():
    """
    准备目录结构
    构建data、img、log等目录
    :returns
        null
    """
    if not os.path.exists('data'):
        os.mkdir('data')
    if not os.path.exists('data\\tmp'):
        os.mkdir('data\\tmp')
    if not os.path.exists('img'):
        os.mkdir('img')
    if not os.path.exists('img\\weather'):
        os.mkdir('img\\weather')
    if not os.path.exists('img\\pick'):
        os.mkdir('img\\pick')
    if not os.path.exists('img\\一部'):
        os.mkdir('img\\一部')
    if not os.path.exists('img\\二部'):
        os.mkdir('img\\二部')
    if not os.path.exists('img\\汉口'):
        os.mkdir('img\\汉口')
    if not os.path.exists('img\\汉阳'):
        os.mkdir('img\\汉阳')
    if not os.path.exists('img\\销售部'):
        os.mkdir('img\\销售部')
    if not os.path.exists('img\\终端客户'):
        os.mkdir('img\\终端客户')
    if not os.path.exists('img\\连锁客户'):
        os.mkdir('img\\连锁客户')
    if not os.path.exists('img\\渠道客户'):
        os.mkdir('img\\渠道客户')
    if not os.path.exists('img\\直销客户'):
        os.mkdir('img\\直销客户')
    if not os.path.exists('img\\公关客户'):
        os.mkdir('img\\公关客户')
    if not os.path.exists('img\\其他客户'):
        os.mkdir('img\\其他客户')
    if not os.path.exists('img\\全渠道'):
        os.mkdir('img\\全渠道')
    if not os.path.exists('img\\非终端'):
        os.mkdir('img\\非终端')
    if not os.path.exists('log'):
        os.mkdir('log')


def mylog():
    """
    日志函数，定义输出文件和格式等内容
    :returns    返回log对象
    """
    logew = lg.getLogger('ewer')
    loghandler = lgh.RotatingFileHandler('log\\everwork.log', encoding='utf-8',  # 此处指定log文件的编码方式，否则可能乱码
                                         maxBytes=2560 * 1024, backupCount=25)
    formats = lg.Formatter('%(asctime)s\t%(name)s\t%(filename)s - [%(funcName)s]'
                           '\t%(threadName)s - %(thread)d , %(processName)s - %(process)d'
                           '\t%(levelname)s: %(message)s',
                           datefmt='%Y-%m-%d %H:%M:%S')
    loghandler.setFormatter(formats)
    logew.setLevel(lg.DEBUG)
    logew.addHandler(loghandler)

    #################################################################################################
    # 定义一个StreamHandler，将INFO级别或更高的日志信息打印到标准错误，并将其添加到当前的日志处理对象#
    console = lg.StreamHandler()
    console.setLevel(lg.DEBUG)
    formatter = lg.Formatter('%(asctime)s\t%(threadName)s - %(thread)d , %(processName)s - %(process)d: '
                             '%(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    lg.getLogger('').addHandler(console)
    # logew.addHandler(console)
    #################################################################################################

    return logew


def getapitimesfromlog():
    """
    从log中提取API调用次数
    :return:
    """
    df = pd.read_csv('log\\everwork.log', sep='\t',  # index_col= False,
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
    global ENtimes, cfp, inifilepath
    # print(ENtimes)
    # print(str(datetime.datetime.now()))
    cfp.set('evernote', 'apicount', '%d' % ENtimes)
    cfp.set('evernote', 'apilasttime', '%s' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    cfp.write(open(inifilepath, 'w', encoding='utf-8'))
    log.info('Evernote API调用次数：%d，写入配置文件%s' % (ENtimes, inifilepath))


def evernoteapiclearatzero():
    """
    evernote API的调用次数过整点清零
    :rtype: None
    :return: 
    """
    global ENtimes, cfp, inifilepath, ENAPIlasttime
    apilasttimehouzhengdian = pd.to_datetime(
        (ENAPIlasttime + datetime.timedelta(hours=1)).strftime('%Y-%m-%d %H:00:00'))
    now = datetime.datetime.now()
    if now > apilasttimehouzhengdian:
        ENAPIlasttime = now
        # time.sleep(60)
        ENtimes = 0
        writeini()


# dirbuildfirst()
log = mylog()

cfp = ConfigParser()
inifilepath = 'data\\everwork.ini'
cfp.read(inifilepath, encoding='utf-8')
cfpdata = ConfigParser()
inidatanotefilepath = 'data\\everdatanote.ini'
cfpdata.read(inidatanotefilepath, encoding='utf-8')
cfplife = ConfigParser()
inilifepath = 'data\\everlife.ini'
cfplife.read(inilifepath, encoding='utf-8')
cfpzysm = ConfigParser()
inizysmpath = 'data\\everzysm.ini'
cfpzysm.read(inizysmpath, encoding='utf-8')
cfpworkplan = ConfigParser()
iniworkplanpath = 'data\\everworkplan.ini'
cfpworkplan.read(iniworkplanpath, encoding='utf-8')

ENtimes = int(cfp.get('evernote', 'apicount'))
ENAPIlasttime = pd.to_datetime(cfp.get('evernote', 'apilasttime'))
apitime = getapitimesfromlog()
if apitime:
    # 比较ini和log中API存档的时间，解决异常退出时调用次数无法准确反映的问题
    if ENAPIlasttime < apitime[0]:
        log.info('程序上次异常退出，调用log中的API数据[%s,%d]' % (str(apitime[0]), apitime[1]))
        ENAPIlasttime = apitime[0]
        ENtimes = apitime[1] + 1
YWanAnchor = 50000  # 纵轴标识万化锚点

evernoteapiclearatzero()


def evernoteapijiayi():
    """
    evernote API调用次数加一，如果达到限值则sleep后归零。又及，多次测试，限值应该是300次每个小时，整点清零重来。
    :return: 
    """
    global ENtimes, cfp, inifilepath
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


def myrndsleep(second=20):
    rnd = np.random.randint(0, second)
    time.sleep(rnd)
    log.debug('休息一哈！这次是' + str(rnd) + '秒……')


def use_logging(level='debug'):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if level == 'debug':
                log.debug("%s 启动运行" % func.__name__)
            return func(*args)
        return wrapper
    return decorator


def timestamp2str(timestamp):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))


def readinisection2df(cfpp: ConfigParser, section: object, biaoti: object):
    """
    读取ini中的section，返回df
    :param cfpp:
    :param section:
    :param biaoti:
    :return: ['guid','title']，index是fenbu，title是fenbu+标题
    """
    namelist = cfpp.options(section)
    valuelist = []
    for nameitem in namelist:
        valueitem = cfpp.get(section, nameitem)
        valuelist.append(valueitem)
    df = pd.DataFrame(valuelist, index=namelist)
    df.columns = ['guid']
    df['fenbu'] = df.index
    df['title'] = df['fenbu'].map(lambda x: x + biaoti)
    del df['fenbu']
    return df


def yingdacal(x, cnx):
    """
    :type x: datetime
    :type cnx: object
    """
    ii = (x + pd.DateOffset(days=1)).strftime('%Y-%m-%d')
    dfall = pd.read_sql_query('select tianshu from jiaqi where date =\'' + ii + '\'', cnx)
    # print(dfall.columns)
    # print(dfall['tianshu'])
    # print(len(dfall))
    print(int(x.strftime('%w')))
    if len(dfall) > 0:
        return x + pd.DateOffset(days=int(dfall['tianshu'][0]))
    elif int(x.strftime('%w')) == 6:
        return x + pd.DateOffset(days=2)
    else:
        return x + pd.DateOffset(days=1)


# @use_logging()
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

    # auth_token = token
    auth_token = cfp.get('evernote', 'token')   # 直接提取，唯一使用

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

    # errorstr = '连接Evernote服务器出现错误！'
    # try:
    #     userstore = client.get_user_store()
    #     version_ok = userstore.checkVersion(
    #         "Evernote EDAMTest (Python)",
    #         UserStoreConstants.EDAM_VERSION_MAJOR,
    #         UserStoreConstants.EDAM_VERSION_MINOR
    #     )
    #     if not version_ok:
    #         log.critical('Evernote API版本过时，请更新之！程序终止并退出！！！')
    #         exit(1)
    #     # print("Is my Evernote API version up to date? ", str(version_ok))
    #     note_store = client.get_note_store()
    #     evernoteapijiayi()
    #     # log.debug('成功连接Evernote服务器！构建notestore：%s' % note_store)
    #     return note_store
    # except socket.gaierror as sge:
    #     if sge.errno == 11001:
    #         log.critical('%s网络连接问题，无法寻址。%s' % (errorstr, str(sge)))
    #     else:
    #         log.critical('%s可能是网络连接问题。%s' % (errorstr, str(sge)))
    #     # exit(5)
    # except Etypes.EDAMUserException as usere:
    #     log.critical('%s出现EDAM用户相关错误，可能是口令有误。%s' % (errorstr, str(usere)))
    #     # exit(5)
    # except Etypes.EDAMSystemException as systeme:
    #     if systeme.errorCode == Etypes.EDAMErrorCode.RATE_LIMIT_REACHED:
    #         log.critical('%s出现EDAM系统错误，API使用超限，需要%d秒后重来。%s' % (errorstr, systeme.rateLimitDuration, str(systeme)))
    #     else:
    #         log.critical('%s出现EDAM系统错误。%s' % (errorstr, str(systeme)))
    # except WindowsError as we:
    #     if we.winerror == 10060:
    #         log.critical('%s出现Windows系统错误（WindowsError）。evernote服务器装死啊！%s' % (errorstr, str(we)))
    #     elif we.winerror == 10054:
    #         log.critical('%s出现Windows系统错误（WindowsError）。evernote服务器端主动关闭链接啦！%s' % (errorstr, str(we)))
    #     else:
    #         log.critical('%s出现Windows系统错误（WindowsError）。%s' % (errorstr, str(we)))
    #     raise we
    # except Exception as ee:
    #     print(ee)
    #     log.critical('%s出现未名系统错误。%s' % (errorstr, str(ee)))
    #     # exit(5)


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


# @use_logging()
def p_notebookattributeundertoken(notebook):
    """
    测试笔记本（notebook）数据结构每个属性的返回值,开发口令（token）的方式调用返回如下
    :param notebook:
    :return:
    """
    print('名称：' + notebook.name, end='\t')  # phone
    print('guid：' + notebook.guid, end='\t')  # f64c3076-60d1-4f0d-ac5c-f0e110f3a69a
    print('更新序列号：' + str(notebook.updateSequenceNum), end='\t')  # 8285
    print('默认笔记本：' + str(notebook.defaultNotebook), end='\t')  # False
    print('创建时间：' + timestamp2str(int(notebook.serviceCreated / 1000)), end='\t')  # 2010-09-15 11:37:43
    print('更新时间：' + timestamp2str(int(notebook.serviceUpdated / 1000)), end='\t')  # 2016-08-29 19:38:24
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
    print('内容\t' + note.content)  # 这种权限的调用没有返回这个值，报错；NoteStore.getNoteContent()也无法解析
    print('内容哈希值\t%s' % note.contentHash)  # 8285
    print('创建时间\t%s' % timestamp2str(int(note.created / 1000)))  # 2017-09-04 22:39:51
    print('更新时间\t%s' % timestamp2str(int(note.updated / 1000)))  # 2017-09-07 06:38:47
    print('删除时间\t%s' % note.deleted)  # 这种权限的调用返回None
    print('活跃\t%s' % note.active)  # True
    print('更新序列号\t%d' % note.updateSequenceNum)  # 173514
    print('所在笔记本的guid\t%s' % note.notebookGuid)  # 2c8e97b5-421f-461c-8e35-0f0b1a33e91c
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


def p_userattributeundertoken(user):
    """
    # 测试用户（user）数据结构每个属性的返回值,开发口令（token）的方式调用返回如下
    :param user:
    :return:
    """
    print('id\t' + str(user.id))  # 返回3884191
    print('名称\t' + str(user.username))  # 返回heart5
    print('用户名\t' + str(user.name))  # 返回白晔峰
    # print '电子邮箱\t', str(user.email)  #这种权限的调用返回None
    print('时区\t' + str(user.timezone))  # 返回Asia/Harbin
    # print '服务级别\t',user.serviceLevel #这种权限的调用没有返回这个值，报错
    # print '启用时间\t', str(user.created), '\t', timestamp2str(user.created)  #这种权限的调用返回None
    # print '更新时间\t', str(user.updated), '\t', timestamp2str(user.updated)  #这种权限的调用返回None
    # print '删除时间\t', str(user.deleted), '\t', timestamp2str(user.deleted)  #这种权限的调用返回None
    print('活跃状态\t' + str(user.active))  # 返回True
    print('分享id\t' + str(user.shardId))  # 返回s37
    # print '用户属性\t', str(user.attributes)  #这种权限的调用返回None
    print('账户\t' + str(user.accounting))
    # 返回Accounting(businessRole=None, currency=None, uploadLimitNextMonth=10737418240L, premiumOrderNumber=None,
    # lastRequestedCharge=None, nextPaymentDue=None, unitDiscount=None, premiumCommerceService=None,
    # nextChargeDate=None, premiumServiceStart=None, premiumSubscriptionNumber=None, lastFailedCharge=None,
    # updated=None, businessId=None, uploadLimitEnd=1504854000000L, uploadLimit=10737418240L,
    # lastSuccessfulCharge=None, premiumServiceStatus=2, unitPrice=None, premiumServiceSKU=None,
    # premiumLockUntil=None, businessName=None, lastFailedChargeReason=None)
    print('活跃状态\t' + str(user.active))  # 返回True
    # print '商用用户信息\t', str(user.businessUserInfo)  #这种权限的调用返回None
    # print '头像url\t', str(user.photoUrl)  #这种权限的调用没有返回这个值，报错
    # print '头像最近更新\t', str(user.photoLastUpdated)  #这种权限的调用没有返回这个值，报错
    # print '账户限制\t', str(user.accountLimits)  #这种权限的调用没有返回这个值，报错


def findnotebookfromevernote():
    # 列出账户中的全部笔记本
    note_store = get_notestore()
    notebooks = note_store.listNotebooks()
    # p_notebookattributeundertoken(notebooks[-1])

    for x in notebooks:
        p_notebookattributeundertoken(x)


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


def updatesection(cfpp, fromsection, tosection, inifile, token, note_store, zhuti='销售业绩图表'):
    """
    根据fromsection中的值构建新的tosection，fenbu、guid
    :param cfpp:
    :param fromsection:
    :param tosection:
    :param inifile:
    :param token:
    :param note_store:
    :param zhuti:
    :return:
    """
    if not cfpp.has_section(tosection):
        cfpp.add_section(tosection)
    nbfbdf = readinisection2df(cfpp, fromsection, zhuti)
    # print(nbfbdf)
    for aa in nbfbdf.index:
        try:
            guid = cfpp.get(tosection, aa)
            if len(guid) > 0:
                # print('笔记《' + str(aa) + zhuti + '》已存在，guid为：' + guid)
                continue
        except Exception as ee:
            log.info('笔记《' + str(aa) + zhuti + '》不存在，将被创建……%s' % str(ee))
        note = Ttypes.Note()
        note.title = nbfbdf.loc[aa]['title']
        # print(aa + '\t\t' + note.title, end='\t\t')
        parentnotebook = note_store.getNotebook(nbfbdf.loc[aa]['guid'])
        evernoteapijiayi()
        note = makenote(token, note_store, note.title, parentnotebook=parentnotebook)
        # print(note.guid + '\t\t' + note.title)
        cfpp.set(tosection, aa, note.guid)
    cfpp.write(open(inifile, 'w', encoding='utf-8'))


def gengxinfou(filename, conn, tablename='fileread'):
    try:
        create_tb_cmd = "CREATE TABLE IF NOT EXISTS %s " \
                        "('文件名' TEXT," \
                        "'绝对路径' TEXT, " \
                        "'修改时间' TIMESTAMP," \
                        "'设备编号' INTEGER," \
                        "'文件大小' INTEGER," \
                        "'登录时间' TIMESTAMP); " % tablename
        conn.execute(create_tb_cmd)
    except Exception as eee:
        log.critical("创建数据表%s失败！" % tablename)
        return False

    fna = os.path.abspath(filename)
    fn = os.path.basename(fna)
    fstat = os.stat(filename)
    # print(fn)

    # sql = "delete from %s where 文件大小 > 0" %tablename
    # print(sql)
    # result = conn.cursor().execute(sql)
    # conn.commit()
    # print(('共删除了'+str(result.fetchone())[0])+'条记录')

    c = conn.cursor()
    sql = "select count(*) from %s where 文件名 = \'%s\'" % (tablename, fn)
    result = c.execute(sql)
    # print(result.lastrowid)
    # conn.commit()
    fncount = (result.fetchone())[0]
    if fncount == 0:
        print("文件《" + fn + "》无记录，录入信息！\t", end='\t')
        result = c.execute("insert into %s values(?,?,?,?,?,?)"
                           % tablename, (fn, fna,
                                         time.strftime('%Y-%m-%d %H:%M:%S',
                                                       time.localtime(fstat.st_mtime)),
                                         str(fstat.st_dev), str(fstat.st_size),
                                         time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())))
        print('添加成功。')
        log.info('文件《%s》无记录，录入信息。' % fn)
        rt = True
    else:
        print("文件《" + fn + "》已有 " + str(fncount) + " 条记录，看是否最新？\t", end='\t')
        sql = "select max(修改时间) as xg from %s where 文件名 = \'%s\'" % (tablename, fn)
        result = c.execute(sql)
        if time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(fstat.st_mtime)) > (result.fetchone())[0]:
            result = c.execute("insert into %s values(?,?,?,?,?,?)" % tablename, (
                fn, fna, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(fstat.st_mtime)), str(fstat.st_dev),
                str(fstat.st_size), time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())))
            print('更新成功！')
            log.info('文件《%s》已有%d条记录，有新文件，更新之。' % (fn, fncount))
            rt = True
        else:
            print('无需更新。')
            rt = False
    conn.commit()

    return rt


def dataokay(cnx):
    if gengxinfou('data\\系统表.xlsx', cnx, 'fileread'):  # or True:
        df = pd.read_excel('data\\系统表.xlsx', sheetname='区域')
        df['区域'] = pd.DataFrame(df['区域']).apply(lambda r: '%02d' % r, axis=1)
        # print(df)
        df = df.loc[:, ['区域', '区域名称', '分部']]
        df.to_sql(name='quyu', con=cnx, if_exists='replace')

        df = pd.read_excel('data\\系统表.xlsx', sheetname='小区')
        df['小区'] = pd.DataFrame(df['小区']).apply(lambda r: '%03d' % r, axis=1)
        # print(df)
        df.to_sql(name='xiaoqu', con=cnx, if_exists='replace')

        df = pd.read_excel('data\\系统表.xlsx', sheetname='终端类型')
        # print(df)
        df.to_sql(name='leixing', con=cnx, if_exists='replace')

        df = pd.read_excel('data\\系统表.xlsx', sheetname='产品档案', )
        # print(df)
        df.to_sql(name='product', con=cnx, if_exists='replace')

        df = pd.read_excel('data\\系统表.xlsx', sheetname='客户档案')
        df = df.loc[:, ['往来单位', '往来单位编号', '地址']]
        # print(df)
        df.to_sql(name='customer', con=cnx, if_exists='replace')

    if gengxinfou('data\\2018年全单统计管理.xlsm', cnx, 'fileread'):  # or True:
        df = pd.read_excel('data\\2018年全单统计管理.xlsm', sheetname='全单统计管理', na_values=[0])
        # descdb(df)
        df = df.loc[:, ['订单日期', '单号', '配货人', '配货准确', '业务主管', '终端编码', '终端名称', '积欠', '送货金额',
                        '实收金额', '收款方式', '优惠', '退货金额', '客户拒收', '无货金额', '少配金额', '配错未要',
                        '送达日期', '车辆', '送货人', '收款日期', '收款人', '拒收品项', '少配明细']]
        df_dh = df.pop('单号')
        df.insert(1, '订单编号', df_dh)
        df['订单编号'] = df['订单编号'].apply(lambda x: str.strip(x) if type(x) == str else x)
        df['配货人'] = df['配货人'].apply(lambda x: str.strip(x) if type(x) == str else x)
        df['业务主管'] = df['业务主管'].apply(lambda x: str.strip(x) if type(x) == str else x)
        df['终端编码'] = df['终端编码'].apply(lambda x: str.strip(x) if type(x) == str else x)
        df['收款方式'] = df['收款方式'].apply(lambda x: str.strip(x) if type(x) == str else x)
        df['车辆'] = df['车辆'].apply(lambda x: str.strip(x) if type(x) == str else x)
        df['送货人'] = df['送货人'].apply(lambda x: str.strip(x) if type(x) == str else x)
        df['收款人'] = df['收款人'].apply(lambda x: str.strip(x) if type(x) == str else x)
        df['拒收品项'] = df['拒收品项'].apply(lambda x: str.strip(x) if type(x) == str else x)
        df['少配明细'] = df['少配明细'].apply(lambda x: str.strip(x) if type(x) == str else x)
        # df['无货金额'] = df['无货金额'].astype(int)
        # df = df.apply(lambda x:str.strip(x) if type(x) == str else x)
        df.to_sql(name='quandan', con=cnx, if_exists='replace', chunksize=100000)

    if gengxinfou('data\\jiaqi.txt', cnx, 'fileread'):
        df = pd.read_csv('data\\jiaqi.txt', sep=',', header=None)
        dfjiaqi = []
        for ii in df[0]:
            slist = ii.split('，')
            slist[0] = pd.to_datetime(slist[0])
            slist[2] = int(slist[2])
            dfjiaqi.append(slist)
        df = pd.DataFrame(dfjiaqi)
        df.sort_values(by=[0], ascending=[1], inplace=True)
        df.columns = ['日期', '假休', '天数']
        # df.index = df['日期']
        # descdb(df)
        sql_df = df.loc[:, df.columns]
        df.to_sql(name='jiaqi', con=cnx, schema=sql_df, if_exists='replace')


def dfin2imglist(dfin, cum, leixingset='', fenbuset='', pinpai='', imgmonthcount=1):
    # print(dfin.tail())
    imglists = []
    for cln in dfin.columns:
        imglist = []
        dfmoban = dfin[cln]
        dfmoban = dfmoban.dropna()  # 除去空值，避免折线中断，fillna(0)在reindex的时候再上
        if dfmoban.shape[0] == 0:  # 跳过空列，新品推广还没有退货发生时这种样子的数据可能出现，再就是数据起始日前放弃的产品，只有退货了
            continue
        # print(dfmoban)
        dangqianyueri = dfmoban.index.max()
        if (datetime.datetime.now() - dangqianyueri).days < 60:  # 近两个月还有数据的才做日累计分析
            for k in range(dangqianyueri.month):
                if k == 0:
                    riqiendwith = dangqianyueri
                else:
                    riqiendwith = dangqianyueri + MonthEnd(k * (-1))
                # print(riqiendwith)
                chuturizhexian(dfmoban, riqiendwith, cln, cum=cum, leixing=leixingset, imglist=imglist, quyu=fenbuset,
                               pinpai=pinpai, imgpath='img\\' + fenbuset + '\\')
            if len(imglist) >= imgmonthcount:
                imglist = imglist[:imgmonthcount]
        nianshu = dfmoban.index.max().year - dfmoban.index.min().year + 1
        chutuyuezhexian(dfmoban, dangqianyueri, cln, cum=cum, leixing=leixingset, imglist=imglist, quyu=fenbuset,
                        pinpai=pinpai, nianshu=nianshu, imgpath='img\\' + fenbuset + '\\')
        imglists.append(imglist)
    imglistreturn = []
    for i in range(len(imglists)):
        imglistreturn += imglists[i]
    return imglistreturn


def biaozhukedu(dfc, weibiao):
    if weibiao == dfc.index.max():
        kedus = [dfc.loc[weibiao]]
    else:
        kedus = [dfc.loc[weibiao], dfc.loc[dfc.index.max()]]
    # print(type(kedus[0]))
    for ii in range(len(kedus)):
        kedu = kedus[ii]
        if (len(dfc.index)) > 12:
            idx = kedu.name
        else:
            idx = list(dfc.index).index(kedu.name)
        if not np.isnan(kedu.iloc[0]):
            plt.plot([idx, idx], [0, kedu.iloc[0]], 'c--')
            plt.annotate(str(kedu.name), xy=(idx, 0), xycoords='data', xytext=(-20, -20),
                         textcoords='offset points', color='r',
                         arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"))
        for i in range(len(kedu)):
            if np.isnan(kedu.iloc[i]):
                # print(kedu.iloc[i])
                # print(type(kedu.iloc[i]))
                continue
            plt.scatter([idx, ], [kedu.iloc[i]], 50, color='Wheat')
            global YWanAnchor
            if kedu.map(lambda x: abs(x)).max() >= YWanAnchor:
                kedubiaozhi = "%.1f万" % (kedu.iloc[i] / 10000)
                plt.gca().yaxis.set_major_formatter(
                    FuncFormatter(lambda x, pos: "%d万" % int(x / 10000)))  # 纵轴主刻度文本用y_formatter函数计算
            else:
                kedubiaozhi = "%d" % kedu.iloc[i]
            fontsize = 8
            if (i % 2) == 0:
                zhengfu = -1
            else:
                zhengfu = 0.4
            plt.annotate(kedubiaozhi, xy=(idx, kedu.iloc[i]), xycoords='data',
                         xytext=(
                             len(kedubiaozhi) * fontsize * zhengfu,
                             int(len(kedubiaozhi) * fontsize * (-1) * zhengfu / 2)),
                         textcoords='offset points', fontsize=fontsize,
                         arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2", color='Purple'))


def chutuyuezhexian(ds, riqienddate, xiangmu, cum=False, imglist=list(), quyu='', leixing='', pinpai='', nianshu=3,
                    imgpath='img\\'):
    """
    月度（全年，自然年度）累积对比图，自最早日期起，默认3年
    :param ds: 数据表，必须用DateTime做index
    :param riqienddate: 数据记录的最近日期，可以是DateTIme的各种形式，只要pd能识别成功，形如2017-10-06
    :param xiangmu: 主题，画图时写入标题
    :param cum:
    :param imglist: 输出图片路径list
    :param quyu: 销售区域或区域聚合（分部）
    :param leixing: 终端类型
    :param pinpai:
    :param nianshu: 用来对比的年份数，从当前年份向回数
    :param imgpath: 图片存储路径
    :return:
    """
    # print(df.tail(10))
    # monthcur = riqienddate + MonthBegin(-1) # 2017-10-01
    nianshushiji = ds.index.max().year - ds.index.min().year + 1
    if nianshushiji > nianshu:
        nianshushiji = nianshu
    nianlist = []
    for i in range(nianshushiji):
        nianlist.append(riqienddate + YearBegin(-(i + 1)))  # 2017-01-01,2016-01-01,2015-01-01

    # if xiangmu == '退货客户数' :
    #     print(df)
    dfn = pd.DataFrame(ds)  # 取出日期索引的数据列

    # 分年份生成按照每天日期重新索引的数据列
    dslist = []
    for i in range(nianshushiji):
        dfnian = pd.DataFrame()
        if i == 0:
            periods = int(riqienddate.strftime('%j'))
        else:
            periods = 365
        dstmp = dfn.reindex(pd.date_range((riqienddate + YearBegin(-1 - (1 * i))), periods=periods, freq='D'),
                            fill_value=0)
        # if xiangmu == '退货客户数':
        #     print(dstmp.tail(30))
        if cum:
            dfnian = dstmp.resample('M').sum()
        else:
            dfnian = dstmp.resample('M').max()
        dfnian.columns = ['%04d' % (nianlist[i].year)]
        dfnian.index = range(len(dfnian.index))
        dslist.append(dfnian)
    # 连接年份DataFrame
    if len(dslist) == 0:
        log.info('年度对比数据为空！')
        return None
    dfy = pd.DataFrame(dslist[0])  # 0,0 1 2 3 4
    for i in range(1, len(dslist)):  # 1 2 3 4
        dfy = dfy.join(dslist[i], how='outer')  # 0 1 2 3 4

    # print(dfy)
    zuobiao = pd.Series(range(1, len(dfy.index) + 1))  # 从1开始生成序列，配合月份，日期的话是自动从1开始的，不用特别处理
    dfy.index = zuobiao.apply(lambda x: '%02d' % (x))

    nianyue = '%04d年' % riqienddate.year
    biaoti = leixing + quyu + pinpai + nianyue + xiangmu
    dslistmax = []
    dslistabs = [abs(x) for x in dslist]
    dfyabs = dfy.apply(lambda x: abs(x))
    # print(dfyabs.max())
    for clname in dfyabs.columns:
        dslistmax.append(dfyabs[clname].max())  # 取绝对值的最大，涵盖退货的负值金额
    # print(type(dslistmax))
    # print(dslistmax)
    global YWanAnchor
    if cum:
        cumstr = '月累积'
        dfjieguo = dfy.cumsum()
        dfjieguo.plot(title=biaoti + cumstr)
        if max(map(abs, dslistmax)) > YWanAnchor:
            plt.gca().yaxis.set_major_formatter(
                FuncFormatter(lambda x, pos: "%d万" % int(x / 10000)))  # 纵轴主刻度文本用y_formatter函数计算
        biaozhukedu(dfjieguo, '%02d' % riqienddate.month)
        if not os.path.exists(imgpath):
            os.mkdir(imgpath)
            log.info('%s不存在，将被创建' % imgpath)

        plt.savefig(imgpath + '%s%s.png' % (biaoti, cumstr))
        imglist.append(imgpath + '%s%s.png' % (biaoti, cumstr))
        plt.close()
    cumstr = '月折线'
    dfy.plot(title='%s%s' % (biaoti, cumstr))
    if max(map(abs, dslistmax)) > YWanAnchor:
        plt.gca().yaxis.set_major_formatter(
            FuncFormatter(lambda x, pos: "%d万" % int(x / 10000)))  # 纵轴主刻度文本用y_formatter函数计算
    biaozhukedu(dfy, '%02d' % (riqienddate.month))
    plt.savefig(imgpath + '%s%s.png' % (biaoti, cumstr))
    imglist.append(imgpath + '%s%s.png' % (biaoti, cumstr))
    plt.close()


def chuturizhexian(df, riqienddate, xiangmu, cum=False,
                   imglist=list(), quyu='', leixing='', pinpai='', imgpath='img\\'):
    """
    日数据（月份）累积对比图，当月、环比、同期比
    riqienddate形如2017-12-08，代表数据结束点的日期
    :param df:
    :param riqienddate:
    :param xiangmu:
    :param cum:
    :param imglist:
    :param quyu:
    :param leixing:
    :param pinpai:
    :param imgpath:
    :return:
    """
    riqicurmonthfirst = riqienddate + MonthBegin(-1)  # 日期格式的当月1日
    riqibeforemonthfirst = riqienddate + MonthBegin(-2)  # 日期格式的上月1日
    riqilastmonthfirst = riqienddate + MonthBegin(-13)  # 日期格式的去年当月1日
    tianshu = (riqienddate + MonthEnd(-1)).day  # 当月的天数

    # print(df)
    ds = pd.DataFrame(df)
    datesb = pd.date_range(riqibeforemonthfirst, periods=tianshu, freq='D')  # 上月日期全集，截止到当月最后一天为止
    if ds.index.min() <= datesb.max():  # 存在有效数据则生成按全月每天索引的DataFrame，否则置空
        ds1 = ds.reindex(datesb, fill_value=0)  # 重新索引，补全所有日期，空值用0填充
        ds1.index = (range(1, len(datesb) + 1))  # 索引天日化
        ds1.columns = f'{riqibeforemonthfirst.year:04d}{riqibeforemonthfirst.month:02d}' + ds1.columns  # 列命名，形如201709
    else:
        ds1 = pd.DataFrame()

    datesl = pd.date_range(riqilastmonthfirst, periods=tianshu, freq='D')  # 处理去年当月数据
    if ds.index.min() <= datesl.max():  # 存在有效数据则生成按全月每天索引的DataFrame，否则置空
        ds3 = ds.reindex(datesl, fill_value=0)
        ds3.index = range(1, len(datesl) + 1)
        ds3.columns = ('%04d%02d' % (riqilastmonthfirst.year, riqilastmonthfirst.month)) + ds3.columns
    else:
        ds3 = pd.DataFrame()

    datesc = pd.date_range(riqicurmonthfirst, periods=riqienddate.day, freq='D')  # 处理当月数据，至截止日期
    if ds.index.min() <= datesc.max():  # 存在有效数据则生成按按照每天索引的DataFrame，否则置空并退出，避免空转
        ds2 = ds.reindex(datesc, fill_value=0)
        ds2.index = range(1, len(datesc) + 1)
        ds2.columns = ('%04d%02d' % (riqicurmonthfirst.year, riqicurmonthfirst.month)) + ds2.columns
    else:
        return

    dff = ds2.join(ds1, how='outer').join(ds3, how='outer')

    nianyue = '%04d%02d' % (riqicurmonthfirst.year, riqicurmonthfirst.month)
    biaoti = leixing + quyu + pinpai + nianyue + xiangmu
    # clnames = []
    # for ct in range(0, len(dff.columns), 2):
    #     clnames.append(dff.columns[ct])
    dfc = dff
    if cum:
        dfc = dfc.cumsum()  # 数据累积求和
        biaoti = biaoti + '日累积'
    # print(dfc)
    dfc.plot(title=biaoti)
    # plt.ylim(0) #设定纵轴从0开始

    biaozhukedu(dfc, riqienddate.day)
    imgsavepath = imgpath + biaoti + '（日累积月）.png'
    plt.savefig(imgsavepath)
    imglist.append(imgsavepath)
    plt.close()

    # return imgsavepath


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
            evernoteapijiayi()
            log.info('成功更新了笔记《%s》，guid：%s。' % (updated_note.title, updated_note.guid))
            break
        except Exception as eee:
            log.critical("第%d次（最多尝试%d次）更新笔记《%s》时失败，将于%d秒后重试。%s"
                         % (i + 1, trytimes, note.title, sleeptime, eee))
            if i == (trytimes - 1):
                log.critical(f'更新笔记《{note.title}》失败，只好无功而返。')
                raise eee
            time.sleep(sleeptime)

    # try:
    #     updated_note = notestore.updateNote(note)
    #     evernoteapijiayi()
    #     log.info('成功更新了笔记《%s》，guid：%s。' % (updated_note.title, updated_note.guid))
    # except Etypes.EDAMUserException as eue:
    #     # EDAMUserException(errorCode=11,
    #     # parameter='The element type "br" must be terminated by the matching end-tag "《/br》".')
    #     if eue.errorCode == 11:
    #         log.critical('更新guid为%s的笔记时出现“EDAM用户异常-》语法”！%s' % (noteguid, str(eue.parameter)))
    #     else:
    #         log.critical('更新guid为%s的笔记时出现“EDAM用户异常”！%s' % (noteguid, str(eue)))
    #     raise eue
    # except struct.error as se:
    #     log.critical('更新guid为%s的笔记时出现“数据结构解析错误”！%s' % (noteguid, str(se)))
    #     print(nbody[300])
    #     raise se
    # except Exception as eee:
    #     log.critical('更新guid为%s的笔记时出现未名错误！%s' % (noteguid, str(eee)))
    #     raise eee


def isnoteupdate(token, noteguid):

    if cfp.has_option('noteupdatenum', noteguid):
        usnold = cfp.getint('noteupdatenum', noteguid)
    else:
        usnold = 0
    usn = 0
    try:
        note = get_notestore().getNote(token, noteguid, False, False, False, False)
        usn = note.updateSequenceNum
        evernoteapijiayi()
        log.info('成功读取笔记《%s》，guid：%s。' % (note.title, note.guid))
    except Exception as e:
        log.critical('读取guid为%s的笔记查看更新序列号时出现错误。%s' % (noteguid, str(e)))

    if usn > usnold:
        cfp.set('noteupdatenum', noteguid, '%d' % usn)
        cfp.write(open(inifilepath, 'w', encoding='utf-8'))
        return usn
    else:
        return False


def tablehtml2evernote(dataframe, tabeltitle, withindex=True):
    pd.set_option('max_colwidth', 200)
    df = pd.DataFrame(dataframe)
    outstr = df.to_html(justify='center', index=withindex).replace('class="dataframe">', 'align="center">'). \
        replace('<table', '\n<h3 align="center">%s</h3>\n<table' % tabeltitle).replace('<th></th>', '<th>&nbsp;</th>')
    # print(outstr)
    return outstr


def getmail(hostmail, usernamemail, passwordmail, port=993, debug=False, mailnum=100000, dirtarget='Inbox', unseen=False,
            topicloc='subject', topic='', datadir='data\\work\\'):
    def parseheader(message):
        headermsg = []

        """ 解析邮件首部 """
        # 发件人
        # mailfrom = email.utils.parseaddr(message.get('from'))[1]
        # print('From:', mailfrom)

        # 时间
        datestr = message.get('date')
        if datestr is None:
            log.error('从邮件头部提取时间失败，只好从邮件内容中寻找时间信息。')
            pattern = re.compile(r'(?:X-smssync-backup-time: )(?P<date>\d{1,2} \w{3} \d{4} \d{2}:\d{2}:\d{2})', re.I)
            items = re.split(pattern, str(message))
            if len(items) > 1:
                print(items[1])
                datemail = datetime.datetime.strptime(items[1], '%d %b %Y %H:%M:%S')
            else:
                log.critical("从邮件内容中也没有找到有效的时间信息。")
                datemail = None
                # print(message)
        else:
            datemail = email.utils.parsedate_to_datetime(message.get('date'))

        localdate = datemail.astimezone(datetime.timezone(datetime.timedelta(hours=8)))
        # print('Date:', localdate)
        headermsg.append(localdate)
        # if mailfrom.startswith('baiyefeng@gmail.com'):
        #     headermsg.append(str(localdate) + '\t发出\t')
        # else:
        #     headermsg.append(str(localdate) + '\t收到\t')

        # 主题
        subject = message.get('subject')
        # print(subject)
        subjectdecoded = str(email.header.make_header(email.header.decode_header(subject)))
        # print(subjectdecoded)
        headermsg.append(subjectdecoded)

        # 发件人
        mailfrom = email.utils.parseaddr(message.get('from'))[1]
        # print('From:', mailfrom)
        headermsg.append(mailfrom)

        # 收件人
        # print(message.get('to'))
        mailto = email.utils.parseaddr(message.get('to'))[1]
        # print('To:', mailto)
        headermsg.append(mailto)
        # print('To:', message.get('to'))
        # 抄送人
        # print('Cc:', email.utils.parseaddr(message.get_all('cc'))[1])

        return headermsg

    def parsebody(message, msgencoding):
        bodymsg = []
        """ 解析邮件/信体 """
        # 循环信件中的每一个mime的数据块
        for part in message.walk():
            partitem = []
            # 这里要判断是否是multipart，是的话，里面的数据是一个message 列表
            if not part.is_multipart():
                charset = part.get_charset()
                # print('charset: ', charset)
                contenttype = part.get_content_type()
                # print('content-type', contenttype)
                namepart = part.get_param("name")  # 如果是附件，这里就会取出附件的文件名
                if namepart:
                    # 有附件
                    # 下面的三行代码只是为了解码象=?gbk?Q?=CF=E0=C6=AC.rar?=这样的文件名
                    fh = email.header.Header(namepart)  # =?gb18030?B?tbyz9sr9vt0ueGxz?=
                    # print(fh)
                    fdh = email.header.decode_header(fh)  # [(b'=?gb18030?B?tbyz9sr9vt0ueGxz?=', 'us-ascii')]
                    # print(fdh)
                    fnamestr = fdh[0][0].decode(fdh[0][1])  # bytes to str with it's encoding
                    fname = email.header.make_header(email.header.decode_header(fnamestr))  # Header类型的数据，内容为“导出数据.xls”
                    fname = str(fname)  # 字符串格式的“导出数据.xls”
                    # print('附件名:', fname)
                    attach_data = part.get_payload(decode=True)  # 解码出附件数据，然后存储到文件中

                    pointat = fname.rfind('.')
                    timenowstr = datetime.datetime.now().strftime('__%Y%m%d%H%M%S_%f')
                    datadiri = datadir
                    if fname.startswith('销售订单'):
                        # print(fname)
                        datadiri = datadiri + '销售订单\\'
                    elif fname.startswith('订单明细'):
                        # print(fname)
                        datadiri = datadiri + '订单明细\\'

                    attachfile = datadiri + fname[:pointat] + timenowstr + fname[pointat:]
                    try:
                        fattach = open(attachfile, 'wb')  # 注意一定要用wb来打开文件，因为附件一般都是二进制文件
                    except Exception as eeee:
                        print(eeee)
                        attachfile = datadiri + '未名文件' + timenowstr
                        fattach = open(attachfile, 'wb')
                    fattach.write(attach_data)
                    fattach.close()
                    partitem.append('attach')
                    partitem.append(attachfile)
                else:
                    # 不是附件，是文本内容
                    # print(part)
                    if not contenttype == 'text/plain':  # 只要plain文本部分
                        continue
                    partdecode = part.get_payload(decode=True)
                    # print(partdecode)
                    bodystr = partdecode.decode(msgencoding)  # 解码出文本内容
                    # print(bodystr)
                    bodystr = BeautifulSoup(bodystr, "html.parser"). \
                        get_text().replace('\r', '').replace('\n', '').replace('\t', '')  # 文本化后去掉回车、换行符等
                    # print(bodystr)
                    partitem.append('text')
                    partitem.append(bodystr)
                # pass
                # print '+'*60 # 用来区别各个部分的输出
            if len(partitem) > 0:
                bodymsg.append(partitem)

        return bodymsg

    trytimes = 3
    serv = None
    for i in range(trytimes):
        try:
            serv = imaplib.IMAP4_SSL(hostmail, port)
            serv.login(usernamemail, passwordmail)
            break
        except Exception as eee:
            log.critical("第%d次（最多尝试%d次）连接登录邮件服务器获取目标邮件编号列表时失败。%s" % (i + 1, trytimes, eee))
            if i == (trytimes - 1):
                log.critical('邮件服务器连接失败，只好无功而返。')
                raise eee
            time.sleep(20)

    # if debug:
    #     serv.debug = 4
    if debug:
        typ, dirs = serv.list()
        # print(dirs)
        for itemdirs in dirs:
            print(itemdirs.decode('ascii').split(') \"/\" \"')[1][:-1], end='\t')
        print()
    typ, dirs = serv.list(directory=dirtarget)
    # print(dirs)
    if unseen:
        statutuplestr = '(unseen)'
    else:
        statutuplestr = '(messages)'
    # print(statutuplestr)
    # print(serv.status(dirtarget,statutuplestr))
    # print(serv.status('"[Gmail]/All Mail"','(messages)'))
    # print(serv.status('Ifttt/Notification','(UIDVALIDITY)'))
    # print(serv.status('Ifttt/SmsLog','(UIDNEXT)'))
    # print(serv.select('"&TgCCLH9RU8s-"'))
    mailstatus = list()
    typess, data = serv.select(dirtarget)
    mailstatus.append(int(data[0].decode('ascii')))
    if len(topic) > 0:
        # 搜索邮件内容
        # typ, data = serv.search(None, '(TO "heart5.4ab86@m.evernote.com" subject "sms")' )
        # typ, data = serv.search(None, '(from "baiyefeng@gmail.com")' )
        # typ, data = serv.search(None, '(subject "%s" since "01-Jan-2017")' %zhuti)
        # typ, data = serv.search(None, '(unseen subject "Status")')
        zhuti = topic
        serv.literal = zhuti.encode('utf-8')
        # typ, data = serv.uid('SEARCH', 'CHARSET', 'UTF-8',  'Since','22-Jan-2018', 'text')
        # typ, data = serv.search('utf-8', 'Since','01-Feb-2018','text')
        if unseen:
            typ, data = serv.search('utf-8', 'unseen', topicloc)
        else:
            typ, data = serv.search('utf-8', topicloc)

        # typ, data = serv.search(None, 'text "Android"')
    else:
        if unseen:
            typ, data = serv.search(None, 'unseen')
        else:
            typ, data = serv.search(None, 'ALL')

    serv.close()
    serv.logout()

    mailstatus.append(len(data[0].split()))
    if debug:
        print(data[0].decode('ascii').split()[::-1])
        print(mailstatus)

    numlist = data[0].decode('ascii').split()[::-1]

    if len(numlist) == 0:  # 无新邮件则返回False
        newstr = '新' if unseen else ''
        topicstr = '主题为“%s”的' % topic if len(topic) > 0 else ''
        log.info('邮箱目录《%s》中没有%s%s邮件' % (dirtarget, topicstr, newstr))
        return False

    if len(numlist) > mailnum:
        numlist = numlist[:mailnum]

    def getnummail(numlistinside, mailitemsinside):
        countstart = len(mailitemsinside)
        counttarget = len(numlistinside)
        log.info('已有%d封邮件，准备处理%d封邮件……' % (countstart, counttarget))

        servinner = None
        for iii in range(trytimes):
            try:
                servinner = imaplib.IMAP4_SSL(hostmail, port)
                servinner.login(usernamemail, passwordmail)
                type, data = servinner.select(dirtarget)
                break
            except ssl.SSLEOFError as ssleof:
                log.critical("第%d次（最多尝试%d次）连接登录邮件服务器获取邮件内容时失败。%s" % (i + 1, trytimes, ssleof))
                if iii == (trytimes - 1):
                    log.critical('邮件服务器连接失败，只好无功而返。')
                    log.info('此列表中的邮件未能被正常处理：%s' % str(numlistinside))
                    raise ssleof
                timesleep = 25
                time.sleep(timesleep)
                log.info('暂停%d秒后返回' % timesleep)
            except Exception as eeee:
                log.critical("第%d次（最多尝试%d次）连接登录邮件服务器时失败。%s" % (i + 1, trytimes, eeee))
                if iii == (trytimes - 1):
                    log.critical('邮件服务器连接失败，只好无功而返。')
                    log.info('此列表中的邮件未能被正常处理：%s' % str(numlistinside))
                    raise eeee
                timesleep = 25
                time.sleep(timesleep)
                log.info('暂停%d秒后返回' % timesleep)

        count = 0
        totalcount = 0
        for num in numlistinside:
            # print(num)
            if (totalcount - count) >= 20:
                log.critical('无法正确处理的邮件超过%d封，此邮件编码列表跳过正常处理流程。%s' % (totalcount - count, numlistinside))
                log.info('实际处理邮件%d封，该邮件编码列表总数量为%d。' % (count, len(numlistinside)))
                return numlistinside

            totalcount += 1
            mailitem = []
            try:
                typ, data = servinner.fetch(num, '(RFC822)')
                # print(data)
                text = data[0][1]
                # text = text.replace('gb-2312','gb2312')
                message = email.message_from_bytes(text)  # 转换为email.message对象
                # print(message)
                pattern = re.compile(r"(UTF-8)|(gb2312)|(gbk)|(gb18030)|(cp936)", re.I)
                subject = message.get('subject')
                resultre = re.search(pattern, str(subject))
                if resultre:
                    mailencodings = resultre.group()
                    if mailencodings.lower().startswith('gb'):  # gb18030是最大的字符集，向下兼容gb2312和gbk
                        mailencodings = 'gb18030'
                else:
                    mailencodings = 'UTF-8'
                # print(mailencodings)
                # print(message)
                mailitem.append(parseheader(message))
                mailitem.append(parsebody(message, mailencodings))
                # print(mailitem)
                mailitemsinside.append(mailitem)
                count = count + 1
            except ConnectionAbortedError as cae:
                log.critical("获取邮件[%s,%d/%d]时出现ConnectionAbortedError错误。%s" % (num, count, totalcount, str(cae)))
            except WindowsError as we:
                if we.errno == 10053:
                    log.critical("获取邮件[%s,%d/%d]时出现操作系统错误，和服务器的连接被强行终止。%s" % (num, count, totalcount, str(we)))
                else:
                    log.critical("获取邮件[%s,%d/%d]时出现操作系统错误。%s" % (num, count, totalcount, str(we)))
            except imaplib.IMAP4.error as iie:
                log.critical("获取邮件[%s,%d/%d]时出现imaplib.IMAP4.error错误。%s" % (num, count, totalcount, str(iie)))
            except imaplib.IMAP4.abort as iia:
                log.critical(
                    "获取邮件[%s,%d/%d]时出现imaplib.IMAP4.abort错误，和服务器的连接被强行终止。%s" % (num, count, totalcount, str(iia)))
            except UnicodeDecodeError as ude:
                log.critical("处理邮件[%s,%d/%d]内容时出现UnicodeDecodeError错误。%s" % (num, count, totalcount, str(ude)))
            except AttributeError as abe:
                log.critical("处理邮件[%s,%d/%d]时出现AttributeError错误。%s" % (num, count, totalcount, str(abe)))
            except TypeError as te:
                log.critical("处理邮件[%s,%d/%d]时出现TypeError错误。%s" % (num, count, totalcount, str(te)))
                print(message)
            except Exception as eeefetch:
                log.critical("处理邮件[%s,%d/%d]时出现未名错误。%s" % (num, count, totalcount, str(eeefetch)))
        servinner.close()
        servinner.logout()
        # print(mailitemsinside)
        log.info('实际处理邮件%d封，该邮件编码列表总数量为%d。' % (count, len(numlistinside)))

    mailitemsresult = list()
    kelidu = 200
    fenjie = int((len(numlist)) / kelidu)
    threadlist = []
    for i in range(fenjie + 1):
        inputnumlist = numlist[(i * kelidu):(i + 1) * kelidu]
        # print(inputnumlist)
        t = threading.Thread(target=getnummail, args=(inputnumlist, mailitemsresult,))
        threadlist.append(t)

    log.info('处理邮箱目录%s，共计有%d个线程准备运行。' % (dirtarget, len(threadlist)))
    threadnum = 8
    threadzushu = int(len(threadlist) / threadnum)
    for i in range(threadzushu + 1):
        threadxiaozu = threadlist[(i * threadnum):(i + 1) * threadnum]
        # if i > 0:
        #     break
        # threadxiaozu = threadlist[140:141]
        log.info('此批次启动%d个线程：' % len(threadxiaozu))
        for t in threadxiaozu:
            t.start()
        # log.info('%d个线程全部启动……' % len(threadxiaozu))
        for t in threadxiaozu:
            t.join()
        log.info('累积有[%d/%d]个线程执行完毕。' % (i * threadnum + len(threadxiaozu), len(threadlist)))
    log.info('总计的%d个线程全部执行完毕！' % len(threadlist))

    return mailitemsresult


def jilugmail(direc, mingmu, fenleistr='', topic='', bodyonly=True):
    """
    从指定邮件目录读取包含关键字的新邮件并更新至txt文件
    :param direc: 待处理的邮件目录
    :param mingmu: 名目，txt文件命名使用
    :param fenleistr: 分类，txt文件命名使用
    :param topic: 搜索邮件的关键字，默认置空
    :param bodyonly: 只要邮件body，默认为真
    :return: 带换行的规范字符串列表
    """

    def readfromtxt(fn):
        if not os.path.exists(fn):
            newfile = open(fn, 'w', encoding='utf-8')
            newfile.close()
        with open(fn, 'r', encoding='utf-8') as fff:
            itemsr = [line.strip() for line in fff if len(line.strip()) > 0]
            # for line in f:
            #     print(line)
        log.info("《%s-%s》现有%d条记录。" % (mingmu, fenleistr, len(itemsr)))
        return itemsr

    hostg = cfp.get('gmail', 'host')
    usernameg = cfp.get('gmail', 'username')
    passwordg = cfp.get('gmail', 'password')
    mailitemsjilu = []
    try:
        mailitemsjilu = getmail(hostg, usernameg, passwordg, debug=False, dirtarget=direc, unseen=True, topic=topic)
    except socket.error as se:
        log.critical("构建socket连接时出错。%s" % str(se))
    except Exception as e:
        log.critical('处理邮件时出现严重错误。%s' % str(e))

    itemslst = []
    if mailitemsjilu is False:
        log.info('%s-%s没有新的邮件记录' % (mingmu, fenleistr))
    else:
        for headerjilu, bodyjilu in mailitemsjilu:
            for textjilu, textstrjilu in bodyjilu:
                if textjilu.startswith('text'):  # 只取用纯文本部分
                    if bodyonly:  # 只要邮件body文本，否则增加邮件标题部分内容
                        itemslst.append(textstrjilu)
                    elif headerjilu[1].startswith('SMS with') or headerjilu[1].endswith('的短信记录') \
                            or headerjilu[1].endswith(
                            '的通话记录'):  # 对特别记录增补时间戳
                        itemslst.append(headerjilu[1] + '\t' + str(headerjilu[0]) + '，' + textstrjilu)
                    else:
                        itemslst.append(headerjilu[1] + '\t' + textstrjilu)

    txtfilename = 'data\\ifttt\\' + '%s_gmail_%s.txt' % (mingmu, fenleistr)
    if len(itemslst) > 0:  # or True:
        items = itemslst + readfromtxt(txtfilename)
        fb = open(txtfilename, 'w', encoding='utf-8')
        for item in items:
            fb.write(item + '\n')
        fb.close()
    else:
        items = readfromtxt(txtfilename)
    log.info("《%s-%s》共有%d条记录。" % (mingmu, fenleistr, len(items)))
    return items


def isworkday(dlist: list, person: str = '全体', fromthen=False):
    if fromthen and (len(dlist) == 1):
        dlist = pd.date_range(dlist[0], datetime.datetime.today(), freq='D')
    cnxp = lite.connect('data\\workplan.db')
    dfholiday = pd.read_sql('select distinct * from holiday', cnxp, index_col='date', parse_dates=['date'])
    del dfholiday['index']
    # print(dfholiday)
    dfleave = pd.read_sql('select distinct date,mingmu,xingzhi,tianshu from leave', cnxp, parse_dates=['date'])
    # print(dfleave)
    resultlist = list()
    for dt in dlist:
        item = list()
        dtdate = pd.to_datetime(dt)
        item.append(dtdate)
        if person != '全体':
            item.append(person)
            dfperson = dfleave[dfleave.mingmu == person]
            dfperson.index = dfperson['date']
            if dtdate in dfperson[dfperson.xingzhi == '上班'].index:
                item.append(True)
                item.append('上班')
                item.append(dfperson.loc[dtdate, ['tianshu']][0])
                resultlist.append(item)
                continue
            if dtdate in dfperson[dfperson.xingzhi != '上班'].index:
                item.append(False)
                item.append(dfperson.loc[dtdate, ['xingzhi']][0])
                item.append(dfperson.loc[dtdate, ['tianshu']][0])
                resultlist.append(item)
                continue
            pass
        else:
            item.append('全体')
        if dtdate in dfholiday[dfholiday.mingmu == '上班'].index:
            item.append(True)
            item.append('上班')
            item.append(dfholiday.loc[dtdate, ['tianshu']][0])
            resultlist.append(item)
            continue
        if dtdate in dfholiday[dfholiday.mingmu != '上班'].index:
            item.append(False)
            item.append(dfholiday.loc[dtdate, ['mingmu']][0])
            item.append(dfholiday.loc[dtdate, ['tianshu']][0])
            resultlist.append(item)
            continue
        if int(dtdate.strftime('%w')) == 0:
            item.append(False)
            item.append('周日')
            item.append(1)
            resultlist.append(item)
            continue
        item.append(True)
        item.append('上班')
        item.append(1)
        resultlist.append(item)
    dfout = pd.DataFrame(resultlist, columns=['date', 'name', 'work', 'xingzhi', 'tianshu'])
    dfout.sort_values(['date'], ascending=[False], inplace=True)
    return dfout


def dftotal2top(df: pd.DataFrame):
    """
    给DataFrame增加汇总行，并将汇总行置顶
    :param df: pd.DataFrame
    :return: pd.DataFrame
    """
    # print(df.dtypes)
    dfslicesingle = df.loc[:, :]
    # print(dfslicesingle.dtypes)
    numtypelist = [float, float64, int, int64]
    # dfslicesingle.loc['汇总'] = dfslicesingle.apply(lambda x: x.sum() if dtype(x) in numtypelist else None)
    dfslicesingle.loc['汇总'] = dfslicesingle.apply(lambda x: x.sum() if x.name.find('日期') < 0 else None)
    # print(list(dfslicesingle.columns))
    # print(list(dfslicesingle.loc['汇总']))
    firstcltotal = False
    hasjun = False
    cls = dfslicesingle.columns
    # print(df.dtypes)
    for cl in cls:
        # print(cl)
        if cl.find('日期') >= 0:
            continue
        if cl.find('有效月均') >= 0:
            hasjun = True
        if dtype(dfslicesingle[cl]) in numtypelist:
            # dfslicesingle.loc['汇总', cl] = dfslicesingle[cl].sum()
            continue
        else:
            if firstcltotal:
                dfslicesingle.loc['汇总', cl] = len(set(list(dfslicesingle[cl]))) - 1
            else:
                firstcltotal = True
                dfslicesingle.loc['汇总', cl] = '汇总'
    # print(list(dfslicesingle.loc['汇总']))
    if hasjun:
        first = start = end = -1
        for i in range(len(cls)):
            if (cls[i].find('有效月均') >= 0) or (cls[i].find('总金额') >= 0):
                break
            if dtype(dfslicesingle[cls[i]]) in numtypelist:
                if first < 0:
                    first = i
                if dfslicesingle.loc['汇总', cls[i]] > 0:
                    if start < 0:
                        start = i
                    end = i
        # print(f'{first}\t{start}\t{end}')
        # print(list(dfslicesingle.loc['汇总'])[start:(end + 1)])
        dfslicesingle.loc['汇总', '有效月均'] = int(sum(list(dfslicesingle.loc['汇总'])[start:(end + 1)]) / (end - start))
        pass
    idxnew = list(dfslicesingle.index)
    idxnew = [idxnew[-1]] + idxnew[:-1]
    dfout = dfslicesingle.loc[idxnew]
    return dfout


if __name__ == '__main__':
    # host = cfp.get('gmail', 'host')
    # username = cfp.get('gmail', 'username')
    # password = cfp.get('gmail', 'password')
    # mailitems = getmail(host, username, password, dirtarget='Ifttt/Location', debug=True, topic='进出记录')
    # print(len(mailitems))
    # for header, body in mailitems:
    #     for text, textstr in body:
    #         print(textstr)

    pass
