#  encoding:utf-8

'''
everwork的各种函数
import大集合
'''

import time, calendar as cal, hashlib, binascii, re, os, socket, random, logging, pandas as pd, sqlite3 as lite,\
    matplotlib.pyplot as plt, \
    evernote.edam.type.ttypes as Ttypes, evernote.edam.error.ttypes as Etypes, \
    evernote.edam.userstore.constants as UserStoreConstants, \
    evernote.edam.notestore.NoteStore as NoteStore
from pylab import *
from configparser import ConfigParser
from matplotlib.ticker import MultipleLocator, FuncFormatter
from evernote.api.client import EvernoteClient
from bs4 import BeautifulSoup


def workbefore():
    '''准备目录结构

    构建data、img、log

    :returns
        null
    '''
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
    '''日志函数，定义输出文件和格式等内容
    
    :returns    返回log对象
    '''''
    log = logging.getLogger('ewer')
    logHandler = logging.FileHandler('log\\everwork.log',encoding='utf-8') #此处指定log文件的编码方式，否则可能乱码
    formats = logging.Formatter('%(asctime)s\t%(name)s\t%(filename)s - [%(funcName)s]\t%(threadName)s - %(thread)d - %(process)d\t%(levelname)s: %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')
    logHandler.setFormatter(formats)
    log.setLevel(logging.DEBUG)
    log.addHandler(logHandler)

    #################################################################################################
    # 定义一个StreamHandler，将INFO级别或更高的日志信息打印到标准错误，并将其添加到当前的日志处理对象#
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s\t%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    #################################################################################################

    return log


workbefore()
log = mylog()
cfp =ConfigParser()
inifilepath = 'data\\everwork.ini'
cfp.read(inifilepath,encoding='utf-8')
ENtimes = cfp.get('evernote','apicount')
apilasttime = pd.to_datetime(cfp.get('evernote','apilasttime'))
apilasttimehouzhengdian = pd.to_datetime((apilasttime+datetime.timedelta(hours=1)).strftime('%Y-%m-%d %H:02:00'))
if datetime.datetime.now() > apilasttimehouzhengdian:
    time.sleep(60)
    ENtimes = 0


def jiayi():
    global ENtimes, cfp, inifilepath
    ENtimes += 1
    log.debug('动用了Evernote API %d 次……' % ENtimes)
    if ENtimes > 180:
        now = datetime.datetime.now()
        zhengdian = pd.to_datetime('%4d-%2d-%2d %2d:00:00' % (now.year, now.month, now.day, now.hour+1))
        sleep_seconds = (zhengdian - now).seconds + 60
        log.info('Evernote API 调用已达%d次，休息%d秒，待%s再开干……' % (ENtimes, sleep_seconds, str(zhengdian)))
        time.sleep(sleep_seconds)
        ENtimes = 0


def myrndsleep(second=20):
    rnd = np.random.randint(0,second)
    time.sleep(rnd)
    log.debug('休息一哈！这次是'+str(rnd)+'秒……')


def use_logging(level='debug'):
    def decorator(func):
        def wrapper(*args,**kwargs):
            if level == 'debug':
                log.debug("%s 启动运行" %func.__name__)
            return func(*args)
        return wrapper
    return decorator


def timestamp2str(timestamp):
    return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(timestamp))


def readinisection2df(cfp,section,biaoti):
    dfsale = cfp.options(section)
    llist = []
    for oo in dfsale:
        str = cfp.get(section, oo)
        llist.append(str)
    df = pd.DataFrame(llist)
    df.columns = ['guid']
    df['fenbu'] = dfsale
    df.index = dfsale

    df = pd.DataFrame(df)
    df['title'] = df['fenbu'].map(lambda x: x + biaoti)
    del df['fenbu']
    return df


def yingdacal(x,cnx):
    ii = (x+pd.DateOffset(days=1)).strftime('%Y-%m-%d')
    dfall = pd.read_sql_query('select tianshu from jiaqi where date =\''+ii+'\'', cnx)
    # print(dfall.columns)
    # print(dfall['tianshu'])
    # print(len(dfall))
    print(int(x.strftime('%w')))
    if(len(dfall) > 0):
        return x+pd.DateOffset(days=int(dfall['tianshu'][0]))
    elif(int(x.strftime('%w')) == 6):
        return x+pd.DateOffset(days=2)
    else:
        return x + pd.DateOffset(days=1)


@use_logging()
def get_notestore(token='your developer token'):
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

    auth_token = token

    if auth_token == "your developer token":
        print("Please fill in your developer token\nTo get a developer token, visit " \
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

    errorstr = '连接Evernote服务器出现错误！'
    try:
        userstore = client.get_user_store()
        version_ok = userstore.checkVersion(
            "Evernote EDAMTest (Python)",
            UserStoreConstants.EDAM_VERSION_MAJOR,
            UserStoreConstants.EDAM_VERSION_MINOR
        )
        if not version_ok:
            log.critical('Evernote API版本过时，请更新之！程序终止并退出！！！')
            exit(1)
        print("Is my Evernote API version up to date? ", str(version_ok))
        note_store = client.get_note_store()
        jiayi()
        log.debug('成功连接Evernote服务器！')
        return note_store
    except socket.gaierror as e:
        log.critical('%s可能是网络连接问题。%s' % (errorstr, str(e)))
        exit(1)
    except Etypes.EDAMUserException as e:
        log.critical('%s可能口令有误。%s' % (errorstr, str(e)))
        exit(1)
    except Etypes.EDAMSystemException as e:
        if e.errorCode == Etypes.EDAMErrorCode.RATE_LIMIT_REACHED:
            log.critical('%sAPI使用超限，需要%d秒后重来。%s' % (errorstr, e.rateLimitDuration, str(e)))
        else:
            log.critical('%s出现系统错误。%s' % (errorstr, str(e)))
        exit(1)
    except Exception as e:
        log.critical('%s出现系统错误。%s' % (errorstr, str(e)))
        exit(2)


#列出笔记本中的笔记信息
def findnotefromnotebook( note_store, token, notebookguid, titlefind, notecount=10000):
    notefilter = NoteStore.NoteFilter()
    notefilter.notebookGuid = notebookguid
    notemetaspec = NoteStore.NotesMetadataResultSpec(includeTitle=True, includeContentLength=True, includeCreated=True,
                                              includeUpdated=True, includeDeleted=True, includeUpdateSequenceNum=True,
                                              includeNotebookGuid=True, includeTagGuids=True, includeAttributes=True,
                                              includeLargestResourceMime=True, includeLargestResourceSize=True)
    ourNoteList=note_store.findNotesMetadata(token, notefilter, 0, notecount, notemetaspec)
    jiayi()

    # print ourNoteList.notes[-1].title  #测试打印指定note的标题
    # print note_store.getNoteContent(ourNoteList.notes[-1].guid)  #测试打印指定note的内容
    # note = note_store.getNote(auth_token, ourNoteList.notes[9].guid, True, True, True, True)  #获得Note并打印其中的值
    # printnoteattributeundertoken(note)
    # print ourNoteList.notes[5] #打印NoteMetadata

    for note in ourNoteList.notes:
        if note.title.find(titlefind) >= 0:
            print (note.guid, note.title)
            return note

    return False


#测试笔记本（notebook）数据结构每个属性的返回值
#开发口令（token）的方式调用返回如下
# @use_logging()
def printnotebookattributeundertoken(notebook):
    print ('名称：'+ notebook.name,end='\t') #phone
    print ('guid：'+ notebook.guid,end='\t') #f64c3076-60d1-4f0d-ac5c-f0e110f3a69a
    print ('更新序列号：'+ str(notebook.updateSequenceNum),end='\t') ##8285
    print ('默认笔记本：'+ str(notebook.defaultNotebook),end='\t') ##False
    print ('创建时间：'+ timestamp2str(int(notebook.serviceCreated/1000)),end='\t')  #2010-09-15 11:37:43
    print ('更新时间：'+ timestamp2str(int(notebook.serviceUpdated/1000)),end='\t')  #2016-08-29 19:38:24
    # print '发布中\t', notebook.publishing  #这种权限的调用返回None
    # print '发布过\t', notebook.published  #这种权限的调用返回None
    print ('笔记本组：'+ str(notebook.stack)) #手机平板
    # print '共享笔记本id\t', notebook.sharedNotebookIds  #这种权限的调用返回None
    # print '共享笔记本\t', notebook.sharedNotebooks  #这种权限的调用返回None
    # print '商务笔记本\t', notebook.businessNotebook  #这种权限的调用返回None
    # print '联系人\t', notebook.contact  #这种权限的调用返回None
    # print '限定\t', notebook.restrictions  #NotebookRestrictions(noSetDefaultNotebook=None, noPublishToBusinessLibrary=True, noCreateTags=None, noUpdateNotes=None, expungeWhichSharedNotebookRestrictions=None, noExpungeTags=None, noSetNotebookStack=None, noCreateSharedNotebooks=None, noExpungeNotebook=None, noUpdateTags=None, noPublishToPublic=None, noUpdateNotebook=None, updateWhichSharedNotebookRestrictions=None, noSetParentTag=None, noCreateNotes=None, noEmailNotes=True, noReadNotes=None, noExpungeNotes=None, noShareNotes=None, noSendMessageToRecipients=None)
    # print '接受人设定\t', notebook.recipientSettings  #这种权限的调用没有返回这个值，报错


#测试笔记（note）数据结构每个属性的返回值
#开发口令（token）的方式调用返回如下
#findNotesMetadata函数获取
def printnoteattributeundertoken( note):
    print ('guid\t'+ note.guid)  #
    print ('标题\t'+ note.title)  #
    print ('内容长度\t'+ note.contentLength) #762
    print ('内容\t'+ note.content)  #这种权限的调用没有返回这个值，报错；NoteStore.getNoteContent()也无法解析
    print ('内容哈希值\t'+ str(note.contentHash)) ##8285
    print ('创建时间\t'+ timestamp2str(int(note.created/1000))) #2017-09-04 22:39:51
    print ('更新时间\t'+ timestamp2str(int(note.updated/1000))) #2017-09-07 06:38:47
    print ('删除时间\t'+ note.deleted)  #这种权限的调用返回None
    print ('活跃\t'+ note.active)  #True
    print ('更新序列号\t'+ note.updateSequenceNum)  #173514
    print ('所在笔记本的guid\t'+ note.notebookGuid) #2c8e97b5-421f-461c-8e35-0f0b1a33e91c
    print ('标签的guid表\t'+ note.tagGuids)  #这种权限的调用返回None
    print ('资源表\t'+ note.resources) #这种权限的调用返回None
    print ('属性\t'+ note.attributes) #NoteAttributes(lastEditorId=139947593, placeName=None, sourceURL=None, classifications=None, creatorId=139947593, author=None, reminderTime=None, altitude=0.0, reminderOrder=None, shareDate=None, reminderDoneTime=None, longitude=114.293, lastEditedBy='\xe5\x91\xa8\xe8\x8e\x89 <305664756@qq.com>', source='mobile.android', applicationData=None, sourceApplication=None, latitude=30.4722, contentClass=None, subjectDate=None)
    print ('标签名称表\t'+ note.tagNames) #这种权限的调用返回None
    # print '共享的笔记表\t', note.sharedNotes  #这种权限的调用没有返回这个值，报错
    # print '限定\t', note.restrictions  #这种权限的调用没有返回这个值，报错
    # print '范围\t', note.limits  #这种权限的调用没有返回这个值，报错


# 测试用户（user）数据结构每个属性的返回值
# 开发口令（token）的方式调用返回如下
def printuserattributeundertoken(user):
    print ('id\t'+ str(user.id))  #返回3884191
    print ('名称\t'+ str(user.username))  #返回heart5
    print ('用户名\t'+ str(user.name))  #返回白晔峰
    # print '电子邮箱\t', str(user.email)  #这种权限的调用返回None
    print ('时区\t'+ str(user.timezone)) #返回Asia/Harbin
    # print '服务级别\t',user.serviceLevel #这种权限的调用没有返回这个值，报错
    # print '启用时间\t', str(user.created), '\t', timestamp2str(user.created)  #这种权限的调用返回None
    # print '更新时间\t', str(user.updated), '\t', timestamp2str(user.updated)  #这种权限的调用返回None
    # print '删除时间\t', str(user.deleted), '\t', timestamp2str(user.deleted)  #这种权限的调用返回None
    print ('活跃状态\t'+ str(user.active)) #返回True
    print ('分享id\t'+ str(user.shardId)) #返回s37
    # print '用户属性\t', str(user.attributes)  #这种权限的调用返回None
    print ('账户\t'+ str(user.accounting)) #返回Accounting(businessRole=None, currency=None, uploadLimitNextMonth=10737418240L, premiumOrderNumber=None, lastRequestedCharge=None, nextPaymentDue=None, unitDiscount=None, premiumCommerceService=None, nextChargeDate=None, premiumServiceStart=None, premiumSubscriptionNumber=None, lastFailedCharge=None, updated=None, businessId=None, uploadLimitEnd=1504854000000L, uploadLimit=10737418240L, lastSuccessfulCharge=None, premiumServiceStatus=2, unitPrice=None, premiumServiceSKU=None, premiumLockUntil=None, businessName=None, lastFailedChargeReason=None)
    print ('活跃状态\t'+ str(user.active)) #返回True
    # print '商用用户信息\t', str(user.businessUserInfo)  #这种权限的调用返回None
    # print '头像url\t', str(user.photoUrl)  #这种权限的调用没有返回这个值，报错
    # print '头像最近更新\t', str(user.photoLastUpdated)  #这种权限的调用没有返回这个值，报错
    # print '账户限制\t', str(user.accountLimits)  #这种权限的调用没有返回这个值，报错


def makenote(token, notestore, notetitle, notebody='真元商贸——休闲食品经营专家', parentnotebook=None):
    nBody = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
    nBody += "<!DOCTYPE en-note SYSTEM \"http://xml.evernote.com/pub/enml2.dtd\">"
    nBody += "<en-note>%s</en-note>" % notebody

    # Create note object
    ourNote = Ttypes.Note()
    ourNote.title = notetitle
    ourNote.content = nBody

    # parentNotebook is optional; if omitted, default notebook is used
    if parentnotebook and hasattr(parentnotebook, 'guid'):
        ourNote.notebookGuid = parentnotebook.guid

    # note = findnotefromnotebook(notestore, token, parentnotebook.guid, notetitle)
    # if note:
    #     log.info('笔记《'+notetitle+'》已经在笔记本《'+parentnotebook.name+'》中存在。')
    #     return note

    # Attempt to create note in Evernote account
    try:
        note = notestore.createNote(token, ourNote)
        jiayi()
        log.info('笔记《' + notetitle + '》在笔记本《' + parentnotebook.name + '》中创建成功。')
        return note
    except Etypes.EDAMUserException as e:
        ## Something was wrong with the note data
        ## See EDAMErrorCode enumeration for error code explanation
        ## http://dev.evernote.com/documentation/reference/Errors.html#Enum_EDAMErrorCode
        log.critical("用户错误！%s" % str(e))
    except Etypes.EDAMNotFoundException as e:
        ## Parent Notebook GUID doesn't correspond to an actual notebook
        print("无效的笔记本guid（识别符）！%s" %str(e))
    except Etypes.EDAMSystemException as e:
        if e.errorCode == Etypes.EDAMErrorCode.RATE_LIMIT_REACHED:
            log.critical("API达到调用极限，需要 %d 秒后重来" % e.rateLimitDuration)
        else:
            log.critical('创建笔记时出现严重错误：'+str(e))
        exit(1)


def updatesection(cfp,fromsection,tosection,inifilepath,token,note_store,zhuti='销售业绩图表'):
    if not cfp.has_section(tosection):
        cfp.add_section(tosection)
    nbfbdf = readinisection2df(cfp, fromsection, zhuti)
    print(nbfbdf)
    for aa in nbfbdf.index:
        try:
            guid = cfp.get(tosection,aa)
            if len(guid) >0:
                print('笔记《'+str(aa)+zhuti+'》已存在，guid为：'+guid)
                continue
        except Exception as e:
            log.info('笔记《'+str(aa)+zhuti+'》不存在，将被创建……%s' % str(e))
        note = Ttypes.Note()
        note.title = nbfbdf.loc[aa]['title']
        # print(aa + '\t\t' + note.title, end='\t\t')
        note = makenote(token, note_store, note.title, parentnotebook=note_store.getNotebook(nbfbdf.loc[aa]['guid']))
        # print(note.guid + '\t\t' + note.title)
        cfp.set(tosection, aa, note.guid)
    cfp.write(open(inifilepath, 'w', encoding='utf-8'))


def gengxinfou(filename,conn,tablename='fileread'):
    rt = False
    try:
        create_tb_cmd = "CREATE TABLE IF NOT EXISTS %s " \
                        "('文件名' TEXT," \
                        "'绝对路径' TEXT, " \
                        "'修改时间' TIMESTAMP," \
                        "'设备编号' INTEGER," \
                        "'文件大小' INTEGER," \
                        "'登录时间' TIMESTAMP); " % tablename
        conn.execute(create_tb_cmd)
    except Exception:
        log.critical("创建数据表%s失败！" % tablename)
        return rt

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
    sql = "select count(*) from %s where 文件名 = \'%s\'" %(tablename,fn)
    result = c.execute(sql)
    # print(result.lastrowid)
    # conn.commit()
    fncount = (result.fetchone())[0]
    if fncount == 0:
        print("文件《"+fn+"》无记录，录入信息！\t", end='\t')
        result = c.execute("insert into %s values(?,?,?,?,?,?)"
                           % tablename, (fn, fna,
                                         time.strftime('%Y-%m-%d %H:%M:%S',
                                                       time.localtime(fstat.st_mtime)),
                                         str(fstat.st_dev), str(fstat.st_size),
                                         time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())))
        print('添加成功。')
        log.info('文件《%s》无记录，录入信息。' %fn)
        rt = True
    else:
        print("文件《"+fn+"》已有 "+str(fncount)+" 条记录，看是否最新？\t",end='\t')
        sql = "select max(修改时间) as xg from %s where 文件名 = \'%s\'" % (tablename,fn)
        result = c.execute(sql)
        if time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(fstat.st_mtime)) > (result.fetchone())[0]:
            result = c.execute("insert into %s values(?,?,?,?,?,?)" % tablename,(fn,fna,time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(fstat.st_mtime)),str(fstat.st_dev),str(fstat.st_size),time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())))
            print('更新成功！')
            log.info('文件《%s》已有%d条记录，有新文件，更新之。' %(fn,fncount))
            rt = True
        else:
            print('无需更新。')
            rt = False
    # print(fstat.st_mtime, '\t', time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(fstat.st_atime)),'\t', '\t', time.strftime('%Y-%m-%d %H:%M',time.localtime(fstat.st_mtime)),'\t', '\t', time.strftime('%Y-%m-%d %H:%M',time.localtime(fstat.st_ctime)),'\t', fstat.st_dev)
    conn.commit()

    return rt


def dataokay(cnx):
    if gengxinfou('data\\系统表.xlsx', cnx, 'fileread'):# or True:
        df = pd.read_excel('data\\系统表.xlsx', sheetname='区域')
        df['区域'] = pd.DataFrame(df['区域']).apply(lambda r: '%02d' %r, axis=1)
        print(df)
        df=df.loc[:,['区域','区域名称', '分部']]
        df.to_sql(name='quyu', con=cnx, if_exists='replace')

        df = pd.read_excel('data\\系统表.xlsx', sheetname='小区')
        df['小区'] = pd.DataFrame(df['小区']).apply(lambda r: '%03d' %r, axis=1)
        print(df)
        df.to_sql(name='xiaoqu', con=cnx, if_exists='replace')

        df = pd.read_excel('data\\系统表.xlsx', sheetname='终端类型')
        print(df)
        df.to_sql(name='leixing', con=cnx, if_exists='replace')

        df = pd.read_excel('data\\系统表.xlsx', sheetname='产品档案',)
        print(df)
        df.to_sql(name='product', con=cnx, if_exists='replace')

        df = pd.read_excel('data\\系统表.xlsx', sheetname='客户档案')
        df = df.loc[:,['往来单位','往来单位编号','地址']]
        print(df)
        df.to_sql(name='customer', con=cnx, if_exists='replace')

    if gengxinfou('data\\2017年全单统计管理.xlsm',cnx,'fileread') :#or True:
        df = pd.read_excel('data\\2017年全单统计管理.xlsm',sheetname='全单统计管理',na_values=[0])
        # descdb(df)
        df=df.loc[:,['订单日期','单号', '配货人', '配货准确', '业务主管', '终端编码', '终端名称', '积欠', '送货金额',
                         '实收金额', '收款方式','优惠','退货金额', '客户拒收', '无货金额', '少配金额', '配错未要',
                         '送达日期', '车辆', '送货人', '收款日期', '收款人', '拒收品项','少配明细']]
        df_dh = df.pop('单号')
        df.insert(1,'订单编号',df_dh)
        df['订单编号'] =df['订单编号'].apply(lambda x:str.strip(x) if type(x) == str else x)
        df['配货人'] =df['配货人'].apply(lambda x:str.strip(x) if type(x) == str else x)
        df['业务主管'] =df['业务主管'].apply(lambda x:str.strip(x) if type(x) == str else x)
        df['终端编码'] =df['终端编码'].apply(lambda x:str.strip(x) if type(x) == str else x)
        df['收款方式'] =df['收款方式'].apply(lambda x:str.strip(x) if type(x) == str else x)
        df['车辆'] =df['车辆'].apply(lambda x:str.strip(x) if type(x) == str else x)
        df['送货人'] =df['送货人'].apply(lambda x:str.strip(x) if type(x) == str else x)
        df['收款人'] =df['收款人'].apply(lambda x:str.strip(x) if type(x) == str else x)
        df['拒收品项'] =df['拒收品项'].apply(lambda x:str.strip(x) if type(x) == str else x)
        df['少配明细'] =df['少配明细'].apply(lambda x:str.strip(x) if type(x) == str else x)
        # df['无货金额'] = df['无货金额'].astype(int)
        # df = df.apply(lambda x:str.strip(x) if type(x) == str else x)
        df.to_sql(name='quandan', con=cnx, if_exists='replace', chunksize=100000)

    # if gengxinfou('data\\xiaoshoushujumingxi.txt',cnx,'fileread'):# or True:
    #     # df = pd.read_csv('data\\xiaoshoushujumingxi.txt',sep='\t',header=None,parse_dates=[0],dtype={'5':np.str,'8':np.str,'12':np.float64,'14':np.float64})
    #     df = pd.read_csv('data\\xiaoshoushujumingxi.txt',sep='\t',header=None,parse_dates=[0],dtype={4:object,5:object,10:object},low_memory=False,verbose=True)
    #     # descdb(df)
    #     df.columns = ['日期','单据编号','单据类型','职员名称','摘要','备注','商品备注','规格','商品编号','商品全名','型号','产地','单价','单位','数量','金额','含税单价','价税合计','成本金额','单位全名','毛利','毛利率','仓库全名','部门全名']
    #     # descdb(df)
    #     # sql_df=df.loc[:,['日期','单据编号','单据类型','职员名称','职员销售明细表','备注','商品备注','规格','商品编号','商品全名','单价','单位','数量','金额','成本金额','单位全名','毛利','毛利率','仓库全名','部门全名']]
    #     df=df.loc[:,['日期','单据编号','单据类型','职员名称','摘要','备注','商品备注','商品编号','商品全名','单价','单位','数量','金额','单位全名','仓库全名','部门全名']]
    #     df['单价'] = (df['单价']).fillna(0)
    #     df['金额'] = (df['金额']).fillna(0)
    #     descdb(df)
    #     df.to_sql(name='xiaoshoumingxi', con=cnx, if_exists='replace', chunksize=100000)

    if gengxinfou('data\\jiaqi.txt',cnx,'fileread'):
        df = pd.read_csv('data\\jiaqi.txt',sep=',',header=None)
        dfjiaqi = []
        for ii in df[0]:
            slist = ii.split('，')
            slist[0] = pd.to_datetime(slist[0])
            slist[2] = int(slist[2])
            dfjiaqi.append(slist)
        df = pd.DataFrame(dfjiaqi)
        df.sort_values(by=[0], ascending=[1], inplace=True)
        df.columns = ['日期','假休','天数']
        # df.index = df['日期']
        # descdb(df)
        sql_df = df.loc[:,df.columns]
        df.to_sql(name='jiaqi',con=cnx,schema=sql_df,if_exists='replace')


# 月度（全年，自然年度）累积对比图，自最早日期起，默认3年
# df，数据表，必须用DateTime做index
# riqi，数据记录的最近日期，可以是DateTIme的各种形式，只要pd能识别成功，形如2017-10-06
# xiangmu，主题，画图时写入标题
# imglist，输出图片路径list
# quyu，销售区域或区域聚合（分部）
# leixing，终端类型
# nianshu，用来对比的年份数，从当前年份向回数
# imgpath，图片存储路径
def chubiaoyuezhexian(df, riqi, xiangmu, cum= False, imglist=[], quyu='', leixing='', pinpai='', nianshu=3, imgpath='img\\'):
    monthcur = pd.to_datetime("%04d-%02d-01" %(riqi.year,riqi.month)) # 2017-10-01
    nianlist = []
    for i in range(nianshu):
        nianlist.append(monthcur+pd.DateOffset(years=-(i))) # 2017-10-01,2016-10-01,2015-10-01

    ds = pd.DataFrame(df[xiangmu],index=df.index)  # 取出日期索引的数据列

    # 分年份生成按照每天日期重新索引的数据列
    dslist = []
    for i in range(nianshu):
        if i == 0:
            periods = int(riqi.strftime('%j'))
        else:
            periods = 365
        dstmp = ds.reindex(pd.date_range(pd.to_datetime(str(nianlist[i].year)+'-01-01'),periods=periods,freq='D'),fill_value=0)
        if cum:
            dstmp = dstmp.resample('M').sum()
        else:
            dstmp = dstmp.resample('M').max()
        dstmp.columns = ['%04d'%(nianlist[i].year)]
        dstmp.index = (range(len(dstmp.index)))
        dslist.append(dstmp)

    df = dslist[-1] # 5,0 1 2 3 4
    for i in range(nianshu-1): # 0 1 2 3
        df = df.join(dslist[-(i+2)]) # -2 -3 -4 -5, 3 2 1 0

    colnames = []
    for i in range(nianshu):
        colnames.append((dslist[-(i+1)].columns)[0]) # -1 -2 -3 -4 -5, 4 3 2 1 0
    # print(colnames)
    df = df[colnames]
    zuobiao = pd.Series(list(df.index))
    df.index= zuobiao.apply(lambda x: '%02d' %(x+1))
    # print(colnames[0]+'\t'+str(type(colnames[0]))+ '\t'+ str(df[str(riqi.year)].max())+'\t' +str(type(riqi.year)))

    nianyue = '%04d年' % monthcur.year
    biaoti = leixing+quyu+pinpai+nianyue+xiangmu
    cumstr = ''
    if cum:
        cumstr = '月累积'
        df.cumsum().plot(title=biaoti+cumstr)
    else:
        cumstr= '月折线'
        df.plot(title= biaoti)
    if df[str(riqi.year)].max() > 10000:
        plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda x, pos: "%d万" %(int(x/10000))))  # 纵轴主刻度文本用y_formatter函数计算
    plt.savefig(imgpath+'%s%s.png' % (biaoti, cumstr))
    imglist.append(imgpath+'%s%s.png' % (biaoti, cumstr))
    plt.close()

    cumstr='月折线'
    df.plot(title=('%s%s') %(biaoti,cumstr))
    if df[str(riqi.year)].max() > 10000:
        plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda x, pos: "%.1f万" %((x/10000))))  # 纵轴主刻度文本用y_formatter函数计算
    plt.savefig(imgpath+'%s%s.png' % (biaoti, cumstr))
    imglist.append(imgpath+'%s%s.png' % (biaoti, cumstr))
    plt.close()


#日（整月）累积对比图，当月、环比、同期比
#riqienddate形如2017-12-08，代表数据结束点的日期
def chubiaorizhexian(df, riqienddate, xiangmu, cum = False,imglist=[], quyu='', leixing='',pinpai='',imgpath='img\\'):
    riqicurmonthfirst = pd.to_datetime("%04d-%02d-01" % (riqienddate.year, riqienddate.month))#日期格式的当月1日
    riqibeforemonthfirst = riqicurmonthfirst+pd.DateOffset(months=-1) # 日期格式的上月1日
    riqilastmonthfirst = riqicurmonthfirst+pd.DateOffset(years=-1) #日期格式的去年当月1日
    tianshu = cal.monthrange(riqienddate.year,riqienddate.month)[1] #当月的天数

    # print(df)
    ds = pd.DataFrame(df[xiangmu],index=df.index) #处理上月数据
    dates = pd.date_range(riqibeforemonthfirst,periods=tianshu,freq='D') #上月日期全集，截止到当月天数为止
    ds1 = ds.reindex(dates,fill_value=0) #重新索引，补全所有日期，空值用0填充
    ds1.index = (range(1,len(dates)+1)) #索引天日化
    ds1.columns = ['%04d%02d' % (riqibeforemonthfirst.year, riqibeforemonthfirst.month)] #列命名，形如201709

    dates = pd.date_range(riqilastmonthfirst, periods=tianshu, freq='D') #处理去年当月数据
    ds3 = ds.reindex(dates,fill_value=0)
    ds3.index = range(1,len(dates)+1)
    ds3.columns = ['%04d%02d' % (riqilastmonthfirst.year, riqilastmonthfirst.month)]

    dates = pd.date_range(riqicurmonthfirst, periods=riqienddate.day, freq='D') #处理当月数据，至截止日期
    ds2 = ds.reindex(dates,fill_value=0)
    ds2.index = range(1,len(dates)+1)
    ds2.columns = ['%04d%02d' % (riqicurmonthfirst.year, riqicurmonthfirst.month)]

    dff = ds3.join(ds2,how='left') #取去年当月天数做主轴
    dff = dff.join(ds1,how='left') #列名列表形如：['201610','201710','201709']
    dff = dff.loc[:,[ds2.columns[0], ds3.columns[0], ds1.columns[0]]] #列名列表形如：['201710','201610','201709']

    nianyue = '%04d%02d' % (riqicurmonthfirst.year, riqicurmonthfirst.month)
    biaoti = leixing+quyu+pinpai+nianyue+xiangmu
    dfc = dff
    if cum:
        dfc = dff.cumsum() #数据累积求和
        biaoti = biaoti+'日累积'
    # print(dfc)
    dfc.plot(title=biaoti)
    plt.ylim(0) #设定纵轴从0开始

    kedu = dfc.loc[riqienddate.day]
    # print(kedu)
    # print(kedu.index)
    # print(kedu[[0]])
    # print(kedu.max())

    # date_end_zuobiao = "%02d" % (df.index.max().day-1)
    plt.plot([riqienddate.day,riqienddate.day],[0,kedu[[0]]],'c--')
    plt.annotate(str(riqienddate.day),xy=(riqienddate.day,0),xycoords='data',
            xytext=(-20, -20), textcoords='offset points',color='r',
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"))
    for i in range(len(kedu)):
        plt.scatter([riqienddate.day,],[kedu[[i]]],50,color='Wheat')
        if kedu.max() >= 10000:
            kedubiaozhi = "%.1f万"  %(kedu[[i]]/10000)
            plt.gca().yaxis.set_major_formatter(
                FuncFormatter(lambda x, pos: "%d万" % (int(x / 10000))))  # 纵轴主刻度文本用y_formatter函数计算
        else:
            kedubiaozhi = "%d" %kedu[[i]]
        fontsize = 8
        if((i%2)) == 0:
            zhengfu = -1
        else:
            zhengfu = 0.4
        plt.annotate(kedubiaozhi, xy=(riqienddate.day, kedu[[i]]), xycoords='data',
                     xytext=(len(kedubiaozhi)*fontsize*zhengfu, int(len(kedubiaozhi)*fontsize*(-1)*zhengfu/2)), textcoords='offset points',fontsize = fontsize,
                     arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2", color='Purple'))

    imgsavepath = imgpath+biaoti+'（日累积月）.png'
    plt.savefig( imgsavepath)
    imglist.append(imgsavepath)
    plt.close()

    # return imgsavepath


def imglist2note(notestore, imglist, noteguid, notetitle, sty='replace'):
    #
    # 更新note内容为图片列表
    #
    note = Ttypes.Note()
    note.guid = noteguid
    note.title = notetitle

    # To include an attachment such as an image in a note, first create a Resource
    # for the attachment. At a minimum, the Resource contains the binary attachment
    # data, an MD5 hash of the binary data, and the attachment MIME type.
    # It can also include attributes such as filename and location.

    # Now, add the new Resource to the note's list of resources
    note.resources = []
    for img in imglist:
        image = open(img, 'rb').read()
        md5 = hashlib.md5()
        md5.update(image)
        hash = md5.digest()
        data = Ttypes.Data()  # 必须要重新构建一个Data（），否则内容不会变化
        data.size = len(image)
        data.bodyHash = hash
        data.body = image
        resource = Ttypes.Resource()
        resource.mime = 'image/png'
        resource.data = data
        note.resources.append(resource)

    # The content of an Evernote note is represented using Evernote Markup Language
    # (ENML). The full ENML specification can be found in the Evernote API Overview
    # at http://dev.evernote.com/documentation/cloud/chapters/ENML.php
    nBody = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
    nBody += "<!DOCTYPE en-note SYSTEM \"http://xml.evernote.com/pub/enml2.dtd\">"
    nBody += "<en-note>"
    if note.resources:
        # To display the Resource as part of the note's content, include an <en-media>
        # tag in the note's ENML content. The en-media tag identifies the corresponding
        # Resource using the MD5 hash.
        # nBody += "<br />" * 2
        for resource in note.resources:
            hexhash = binascii.hexlify(resource.data.bodyHash)
            str1 = "%s" %hexhash #b'cd34b4b6c8d9279217b03c396ca913df'
            # print (str1)
            str1 = str1[2:-1] #cd34b4b6c8d9279217b03c396ca913df
            # print (str1)
            nBody += "<en-media type=\"%s\" hash=\"%s\" /><br />"  %(resource.mime, str1)
    nBody += "</en-note>"

    note.content = nBody
    # print (note.content)

    # Finally, send the new note to Evernote using the updateNote method
    # The new Note object that is returned will contain server-generated
    # attributes such as the new note's unique GUID.
    try:
        updated_note = notestore.updateNote(note)
        jiayi()
        log.info('成功更新了笔记《%s》，guid：%s。' % (updated_note.title, updated_note.guid))
    except Etypes.EDAMSystemException as e:
        if e.errorCode == Etypes.EDAMErrorCode.RATE_LIMIT_REACHED:
            log.critical("API达到调用极限，需要 %d 秒后重来" % e.rateLimitDuration)
        else:
            log.critical('更新笔记时出现系统错误：'+str(e))
        exit(1)
