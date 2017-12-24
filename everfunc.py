#
# encoding:utf-8
#
# 有关evernote的各种探测性函数
#

import time, calendar as cal, hashlib, binascii, re, os, logging, pandas as pd, sqlite3 as lite,\
    matplotlib.pyplot as plt, evernote.edam.type.ttypes as Types, evernote.edam.userstore.constants as UserStoreConstants, \
    evernote.edam.notestore.NoteStore as NoteStore
from pylab import *
from matplotlib.ticker import MultipleLocator, FuncFormatter
from evernote.api.client import EvernoteClient
from bs4 import BeautifulSoup

def workbefore():
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
    if not os.path.exists('log'):
        os.mkdir('log')

def mylog():
    log = logging.getLogger('ewer')
    logHandler = logging.FileHandler(filename='log\\everwork.log')
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


def timestamp2str(timestamp):
    return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(timestamp))


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

    # auth_token = "S=s37:U=3b449f:E=1659f8b7c0f:C=15e47da4ef8:P=1cd:A=en-devtoken:V=2:H=e445e5fcbceff83703151d71df584197"
    # auth_token = "S=s37:U=3b449f:E=16017ef9105:C=16012c93380:P=185:A=get-off-the-ground:V=2:H=3de0c5e50f23f1d252b8ebe8f958d368"  # 一天
    auth_token = "S=s37:U=3b449f:E=1676a821f3c:C=16012d0eff8:P=185:A=get-off-the-ground:V=2:H=1469bc6bfc7ac8a2f68b72c0c0335a29"  # 一年
    # auth_token = token

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

    userStore = client.get_user_store()

    # currentuser = userStore.getUser()
    # printuserattributeundertoken(currentuser)

    version_ok = userStore.checkVersion(
        "Evernote EDAMTest (Python)",
        UserStoreConstants.EDAM_VERSION_MAJOR,
        UserStoreConstants.EDAM_VERSION_MINOR
    )
    print("Is my Evernote API version up to date? ", str(version_ok))

    if not version_ok:
        log.critical('Evernote API版本过时，请更新之！程序终止并退出！！！')
        exit(1)

    note_store = client.get_note_store()

    return note_store


#列出笔记本中的笔记信息
def printnotefromnotebook( note_store,token,notebookguid, notecount,titlefind):
    notefilter = NoteStore.NoteFilter()
    notefilter.notebookGuid = notebookguid
    notemetaspec = NoteStore.NotesMetadataResultSpec(includeTitle=True, includeContentLength=True, includeCreated=True,
                                              includeUpdated=True, includeDeleted=True, includeUpdateSequenceNum=True,
                                              includeNotebookGuid=True, includeTagGuids=True, includeAttributes=True,
                                              includeLargestResourceMime=True, includeLargestResourceSize=True)
    ourNoteList=note_store.findNotesMetadata(token, notefilter, 0, notecount, notemetaspec)

    # print ourNoteList.notes[-1].title  #测试打印指定note的标题
    # print note_store.getNoteContent(ourNoteList.notes[-1].guid)  #测试打印指定note的内容
    # note = note_store.getNote(auth_token, ourNoteList.notes[9].guid, True, True, True, True)  #获得Note并打印其中的值
    # printnoteattributeundertoken(note)
    # print ourNoteList.notes[5] #打印NoteMetadata

    for note in ourNoteList.notes:
        if note.title.find(titlefind) >= 0:
            print (note.guid, note.title)

    print()


#测试笔记本（notebook）数据结构每个属性的返回值
#开发口令（token）的方式调用返回如下
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


#
# 把纵轴的刻度设置为万
#
def y_formatter(x, pos):
    return r"%d万" %(int(x/10000)) #%d


def rizi(df):
    return '%02d' %(df[0].day)


def yuezi(df):
    return '%02d' %(df[0]+1)


# 月度（全年，自然年度）累积对比图，自最早日期起，默认3年
# df，数据表，必须用DateTime做index
# riqi，当前月份，可以是DateTIme的各种形式，只要pd能识别成功，形如2017-10-01，代表2017年10月为标的月份
# xiangmu，主题，画图时写入标题
# imglist，输出图片路径list
# quyu，销售区域或区域聚合（分部）
# leixing，终端类型
# nianshu，用来对比的年份数，从当前年份向回数
# imgpath，图片存储路径
def chubiaoyueleiji(df,riqi,xiangmu,imglist=[], quyu='',leixing='',pinpai='',nianshu=3,imgpath='img\\'):
    riqicur = pd.to_datetime(riqi)
    nianlist = []
    for i in range(nianshu):
        nianlist.append(riqicur+pd.DateOffset(years=-(i)))

    ds = pd.DataFrame(df[xiangmu],index=df.index)#取出日期索引的数据列

    # 分年份生成按照每天日期重新索引的数据列
    dslist = []
    for i in range(nianshu):
        dstmp = ds.reindex(pd.date_range(pd.to_datetime(str(nianlist[i].year)+'-01-01'),periods=365,freq='D'),fill_value=0)
        dstmp = dstmp.resample('M').sum()
        dstmp.columns = ['%04d'%(nianlist[i].year)]
        dstmp.index = (range(12))
        dslist.append(dstmp)

    df = dslist[0]
    for i in range(nianshu-1):
        df = df.join(dslist[i+1])

    colnames = []
    for i in range(nianshu):
        colnames.append((dslist[i].columns)[0])
    # print(colnames)
    df = df[colnames]
    zuobiao = pd.DataFrame(df.index).apply(lambda r:yuezi(r),axis=1)
    df.index= zuobiao

    nianyue = '%04d年'%(riqicur.year)
    biaoti = leixing+quyu+pinpai+nianyue+xiangmu
    df.cumsum().plot(title=('%s月累积' %biaoti))
    # df.cumsum().plot(table=True,fontsize=12,figsize=(40,20))
    plt.gca().yaxis.set_major_formatter(FuncFormatter(y_formatter))  # 纵轴主刻度文本用y_formatter函数计算
    plt.savefig(imgpath+'%s（月累积）.png' %biaoti)
    imglist.append(imgpath+'%s（月累积）.png' %biaoti)
    plt.close()
    df.plot(title=('%s月折线') %biaoti)
    plt.gca().yaxis.set_major_formatter(FuncFormatter(y_formatter))  # 纵轴主刻度文本用y_formatter函数计算
    plt.savefig(imgpath+'%s（月折线）.png' %biaoti)
    imglist.append(imgpath+'%s（月折线）.png' %biaoti)
    plt.close()


#日（整月）累积对比图，当月、环比、同期比
#riqienddate形如2017-12-08，代表数据结束点的日期
def chubiaorileiji(df, riqienddate, xiangmu, imglist=[], quyu='', leixing='',pinpai='',imgpath='img\\'):
    riqicurmonthfirst = pd.to_datetime("%04d-%02d-01" %(riqienddate.year,riqienddate.month))#日期格式的当月1日
    riqibeforemonthfirst = riqicurmonthfirst+pd.DateOffset(months=-1) # 日期格式的上月1日
    riqilastmonthfirst = riqicurmonthfirst+pd.DateOffset(years=-1) #日期格式的去年当月1日
    tianshu = cal.monthrange(riqienddate.year,riqienddate.month)[1] #当月的天数

    ds = pd.DataFrame(df[xiangmu],index=df.index) #处理上月数据
    dates = pd.date_range(riqibeforemonthfirst,periods=tianshu,freq='D') #上月日期全集，截止到当月天数为止
    ds1 = ds.reindex(dates,fill_value=0) #重新索引，补全所有日期，空值用0填充
    ds1.index = (range(1,len(dates)+1)) #索引天日化
    ds1.columns = ['%04d%02d' %(riqibeforemonthfirst.year,riqibeforemonthfirst.month)] #列命名，形如201709

    dates = pd.date_range(riqilastmonthfirst,periods=tianshu,freq='D') #处理去年当月数据
    ds3 = ds.reindex(dates,fill_value=0)
    ds3.index = range(1,len(dates)+1)
    ds3.columns = ['%04d%02d' %(riqilastmonthfirst.year,riqilastmonthfirst.month)]

    dates = pd.date_range(riqicurmonthfirst,periods=riqienddate.day,freq='D') #处理当月数据，至截止日期
    ds2 = ds.reindex(dates,fill_value=0)
    ds2.index = range(1,len(dates)+1)
    ds2.columns = ['%04d%02d' %(riqicurmonthfirst.year,riqicurmonthfirst.month)]

    dff = ds3.join(ds2,how='left') #取去年当月天数做主轴
    dff = dff.join(ds1,how='left') #列名列表形如：['201610','201710','201709']
    dff = dff.loc[:,[ds2.columns[0],ds3.columns[0],ds1.columns[0]]] #列名列表形如：['201710','201610','201709']

    nianyue = '%04d%02d' %(riqicurmonthfirst.year,riqicurmonthfirst.month)
    biaoti = leixing+quyu+pinpai+nianyue+xiangmu
    dfc = dff.cumsum() #数据累积求和
    # print(dfc)
    dfc.plot(title=biaoti+'日累积')
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

#
#图片列表更新进笔记
#
def imglist2note(notestore, imglist, noteguid, notetitle,style='replace'):
    #
    # 要更新一个note，生成一个Note（），指定guid，更新其content
    #
    note = Types.Note()
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
        data = Types.Data()  # 必须要重新构建一个Data（），否则内容不会变化
        data.size = len(image)
        data.bodyHash = hash
        data.body = image
        resource = Types.Resource()
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
    updated_note = notestore.updateNote(note)
    # print(updated_note)
    # print ("Successfully updated a note with GUID: ", updated_note.guid, updated_note.title)
    log.info('成功更新了笔记《%s》，guid：%s。' %(updated_note.title,updated_note.guid))

