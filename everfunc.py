#
# encoding:utf-8
#
# 有关evernote的各种探测性函数
#

import time, pandas as pd, sqlite3 as lite,matplotlib.pyplot as plt,calendar as cal
from pylab import *


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
# quyu，销售区域或区域聚合（分部）
# leixing，终端类型
# nianshu，用来对比的年份数，从当前年份向回数
def chubiaoyueleiji(df,riqi,xiangmu,quyu='',leixing='',pinpai='',nianshu=3,imgpath='img\\'):
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

    # descdb(df)

    nianyue = '%04d年'%(riqicur.year)
    biaoti = leixing+quyu+pinpai+nianyue+xiangmu
    df.cumsum().plot(title=('%s月累积' %biaoti))
    # df.cumsum().plot(table=True,fontsize=12,figsize=(40,20))
    plt.gca().yaxis.set_major_formatter(FuncFormatter(y_formatter))  # 纵轴主刻度文本用y_formatter函数计算
    plt.savefig(imgpath+'%s（月累积）.png' %biaoti)
    plt.close()
    df.plot(title=('%s月折线') %biaoti)
    plt.gca().yaxis.set_major_formatter(FuncFormatter(y_formatter))  # 纵轴主刻度文本用y_formatter函数计算
    plt.savefig(imgpath+'%s（月折线）.png' %biaoti)
    plt.close()
    # plt.show()
    # ds1.plot()
    #
    # ds2 = ds1.resample('M').sum()
    # descdb(ds2)
    # print(ds2.sum())
    # ds2.plot()
    # plt.show()

    # dfr = df.reindex(dates,fill_value=0)
    # descdb(dfr)
    # df['danshu'].plot()
    # plt.show()
    # df['jine'].plot()
    # plt.show()


#日（整月）累积对比图，当月、环比、同期比
#riqi形如2017-10-01，代表2017年10月为标的月份
def chubiaorileiji(df, riqi, xiangmu, quyu='', leixing='',pinpai='',imgpath='img\\'):
    riqicur = pd.to_datetime(riqi)
    riqibefore = riqicur+pd.DateOffset(months=-1)
    riqilast = riqicur+pd.DateOffset(years=-1)
    tianshu = cal.monthrange(riqicur.year,riqicur.month)[1]

    ds = pd.DataFrame(df[xiangmu],index=df.index)
    # print(ds.index)
    # print(ds)
    dates = pd.date_range(riqibefore,periods=tianshu,freq='D')
    # print(dates)
    ds1 = ds.reindex(dates,fill_value=0)
    # ds1 = ds1.resample('M').sum()
    # descdb(ds1)
    ds1.index = (range(1,tianshu+1))
    ds1.columns = ['%04d%02d' %(riqibefore.year,riqibefore.month)]
    # descdb(ds1)

    dates = pd.date_range(riqilast,periods=tianshu,freq='D')
    # print(dates)
    ds3 = ds.reindex(dates,fill_value=0)
    # ds2 =ds2.resample('M').sum()
    # descdb(ds3)
    ds3.index = range(1,tianshu+1)
    ds3.columns = ['%04d%02d' %(riqilast.year,riqilast.month)]
    # descdb(ds3)

    dates = pd.date_range(riqicur,periods=tianshu,freq='D')
    # print(dates)
    ds2 = ds.reindex(dates,fill_value=0)
    # ds2 =ds2.resample('M').sum()
    # descdb(ds2)
    ds2.index = range(1,tianshu+1)
    ds2.columns = ['%04d%02d' %(riqicur.year,riqicur.month)]
    # descdb(ds2)

    dff = ds2.join(ds1,how='left')
    dff = dff.join(ds3,how='left')
    dff = dff[['%04d%02d' %(riqicur.year,riqicur.month),'%04d%02d' %(riqibefore.year,riqibefore.month),'%04d%02d' %(riqilast.year,riqilast.month)]]
    # descdb(df)
    zuobiao = pd.DataFrame(dates).apply(lambda r:rizi(r),axis=1)
    dff.index= zuobiao
    # descdb(df)
    nianyue = '%04d%02d'%(riqicur.year,riqicur.month)
    biaoti = leixing+quyu+pinpai+nianyue+xiangmu
    if len(df) > 12:
        # print(len(df))
        dff.cumsum().plot(title=biaoti+'日累积')
    else:
        dff.cumsum().plot(title=biaoti+'日累积')

    date_end = "%02d" %(df.index.max().day)
    print(date_end)
    dfc = dff.cumsum()
    kedu = dfc.loc[date_end]
    print(kedu)
    print(kedu.index)
    print(kedu[[0]])
    print(kedu[[0]])

    # date_end_zuobiao = "%02d" % (df.index.max().day-1)
    plt.plot([date_end,date_end],[0,kedu[[0]].ix[0,1]],'c--')
    plt.gca().yaxis.set_major_formatter(FuncFormatter(y_formatter))  # 纵轴主刻度文本用y_formatter函数计算
    imgsavepath = imgpath+biaoti+'（日累积月）.png'
    plt.savefig( imgsavepath)
    # plt.show()
    plt.close()
    # ds1.plot()
    #
    # ds2 = ds1.resample('M').sum()
    # descdb(ds2)
    # print(ds2.sum())
    # ds2.plot()
    # plt.show()

    # dfr = df.reindex(dates,fill_value=0)
    # descdb(dfr)
    # df['danshu'].plot()
    # plt.show()
    # df['jine'].plot()
    # plt.show()
    return imgsavepath

