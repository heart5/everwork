#
# encoding:utf-8
#
# 有关evernote的各种探测性函数
#

import time, pandas as pd, sqlite3 as lite



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
    print ('名称\t'+ notebook.name) #phone
    print ('guid\t'+ notebook.guid) #f64c3076-60d1-4f0d-ac5c-f0e110f3a69a
    print ('更新序列号\t'+ notebook.updateSequenceNum) ##8285
    print ('默认笔记本\t'+ notebook.defaultNotebook) ##False
    print ('创建时间\t'+ timestamp2str(int(notebook.serviceCreated/1000)))  #2010-09-15 11:37:43
    print ('更新时间\t'+ timestamp2str(int(notebook.serviceUpdated/1000)))  #2016-08-29 19:38:24
    # print '发布中\t', notebook.publishing  #这种权限的调用返回None
    # print '发布过\t', notebook.published  #这种权限的调用返回None
    print ('笔记本组\t'+ notebook.stack) #手机平板
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

