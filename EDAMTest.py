#
# encoding:utf-8
# A simple Evernote API demo script that lists all notebooks in the user's
# account and creates a simple test note in the default notebook.
#
# Before running this sample, you must fill in your Evernote developer token.
#
# To run (Unix):
#   export PYTHONPATH=../../lib; python EDAMTest.py
#

import hashlib
import binascii
import time,calendar
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import evernote.edam.userstore.constants as UserStoreConstants
import evernote.edam.type.ttypes as Types
import evernote.edam.notestore.NoteStore as NoteStore

from bs4 import BeautifulSoup
from evernote.api.client import EvernoteClient

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

auth_token = "S=s37:U=3b449f:E=1659f8b7c0f:C=15e47da4ef8:P=1cd:A=en-devtoken:V=2:H=e445e5fcbceff83703151d71df584197"

if auth_token == "your developer token":
    print "Please fill in your developer token"
    print "To get a developer token, visit " \
        "https://sandbox.evernote.com/api/DeveloperToken.action"
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


def timestamp2str(timestamp):
    return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(timestamp))


userStore = client.get_user_store()
currentuser = userStore.getUser()


# 测试用户（user）数据结构每个属性的返回值
# 开发口令（token）的方式调用返回如下
def printuserattributeundertoken(user):
    print 'id\t', str(user.id)  #返回3884191
    print '名称\t', str(user.username)  #返回heart5
    print '用户名\t', str(user.name)  #返回白晔峰
    # print '电子邮箱\t', str(user.email)  #这种权限的调用返回None
    print '时区\t', str(user.timezone)  #返回Asia/Harbin
    # print '服务级别\t',user.serviceLevel #这种权限的调用没有返回这个值，报错
    # print '启用时间\t', str(user.created), '\t', timestamp2str(user.created)  #这种权限的调用返回None
    # print '更新时间\t', str(user.updated), '\t', timestamp2str(user.updated)  #这种权限的调用返回None
    # print '删除时间\t', str(user.deleted), '\t', timestamp2str(user.deleted)  #这种权限的调用返回None
    print '活跃状态\t', str(user.active)  #返回True
    print '分享id\t', str(user.shardId)  #返回s37
    # print '用户属性\t', str(user.attributes)  #这种权限的调用返回None
    print '账户\t', str(user.accounting)  #返回Accounting(businessRole=None, currency=None, uploadLimitNextMonth=10737418240L, premiumOrderNumber=None, lastRequestedCharge=None, nextPaymentDue=None, unitDiscount=None, premiumCommerceService=None, nextChargeDate=None, premiumServiceStart=None, premiumSubscriptionNumber=None, lastFailedCharge=None, updated=None, businessId=None, uploadLimitEnd=1504854000000L, uploadLimit=10737418240L, lastSuccessfulCharge=None, premiumServiceStatus=2, unitPrice=None, premiumServiceSKU=None, premiumLockUntil=None, businessName=None, lastFailedChargeReason=None)
    print '活跃状态\t', str(user.active)  #返回True
    # print '商用用户信息\t', str(user.businessUserInfo)  #这种权限的调用返回None
    # print '头像url\t', str(user.photoUrl)  #这种权限的调用没有返回这个值，报错
    # print '头像最近更新\t', str(user.photoLastUpdated)  #这种权限的调用没有返回这个值，报错
    # print '账户限制\t', str(user.accountLimits)  #这种权限的调用没有返回这个值，报错


# printuserattributeundertoken(currentuser)

print int(time.time()), '\t', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

version_ok = userStore.checkVersion(
    "Evernote EDAMTest (Python)",
    UserStoreConstants.EDAM_VERSION_MAJOR,
    UserStoreConstants.EDAM_VERSION_MINOR
)
print "Is my Evernote API version up to date? ", str(version_ok)
print ""
if not version_ok:
    exit(1)


#测试笔记本（notebook）数据结构每个属性的返回值
#开发口令（token）的方式调用返回如下
def printnotebookattributeundertoken(notebook):
    print '名称\t', notebook.name  #phone
    print 'guid\t', notebook.guid  #f64c3076-60d1-4f0d-ac5c-f0e110f3a69a
    print '更新序列号\t', notebook.updateSequenceNum  ##8285
    print '默认笔记本\t', notebook.defaultNotebook  ##False
    print '创建时间\t', timestamp2str(int(notebook.serviceCreated/1000))  #2010-09-15 11:37:43
    print '更新时间\t', timestamp2str(int(notebook.serviceUpdated/1000))  #2016-08-29 19:38:24
    # print '发布中\t', notebook.publishing  #这种权限的调用返回None
    # print '发布过\t', notebook.published  #这种权限的调用返回None
    print '笔记本组\t', notebook.stack  #手机平板
    # print '共享笔记本id\t', notebook.sharedNotebookIds  #这种权限的调用返回None
    # print '共享笔记本\t', notebook.sharedNotebooks  #这种权限的调用返回None
    # print '商务笔记本\t', notebook.businessNotebook  #这种权限的调用返回None
    # print '联系人\t', notebook.contact  #这种权限的调用返回None
    # print '限定\t', notebook.restrictions  #NotebookRestrictions(noSetDefaultNotebook=None, noPublishToBusinessLibrary=True, noCreateTags=None, noUpdateNotes=None, expungeWhichSharedNotebookRestrictions=None, noExpungeTags=None, noSetNotebookStack=None, noCreateSharedNotebooks=None, noExpungeNotebook=None, noUpdateTags=None, noPublishToPublic=None, noUpdateNotebook=None, updateWhichSharedNotebookRestrictions=None, noSetParentTag=None, noCreateNotes=None, noEmailNotes=True, noReadNotes=None, noExpungeNotes=None, noShareNotes=None, noSendMessageToRecipients=None)
    # print '接受人设定\t', notebook.recipientSettings  #这种权限的调用没有返回这个值，报错


note_store = client.get_note_store()

# 列出账户中的全部笔记本
notebooks = note_store.listNotebooks()
# printnotebookattributeundertoken(notebooks[1])
# print "Found ", len(notebooks), " notebooks:"
# for notebook in notebooks:
#     print "\t*\t", notebook.name, "\t",notebook.guid, "\t",notebook.updateSequenceNum, "\t",notebook.defaultNotebook, "\t",timestamp2str(int(notebook.serviceCreated/1000)), "\t",timestamp2str(int(notebook.serviceUpdated/1000)), "\t",notebook.stack
#


#测试笔记（note）数据结构每个属性的返回值
#开发口令（token）的方式调用返回如下
#findNotesMetadata函数获取
def printnoteattributeundertoken( note):
    print 'guid\t', note.guid  #
    print '标题\t', note.title  #
    print '内容长度\t', note.contentLength  #762
    print '内容\t', note.content  #这种权限的调用没有返回这个值，报错；NoteStore.getNoteContent()也无法解析
    print '内容哈希值\t', str(note.contentHash)  ##8285
    print '创建时间\t', timestamp2str(int(note.created/1000))  #2017-09-04 22:39:51
    print '更新时间\t', timestamp2str(int(note.updated/1000))  #2017-09-07 06:38:47
    print '删除时间\t',note.deleted  #这种权限的调用返回None
    print '活跃\t', note.active  #True
    print '更新序列号\t', note.updateSequenceNum  #173514
    print '所在笔记本的guid\t', note.notebookGuid  #2c8e97b5-421f-461c-8e35-0f0b1a33e91c
    print '标签的guid表\t', note.tagGuids  #这种权限的调用返回None
    print '资源表\t', note.resources  #这种权限的调用返回None
    print '属性\t', note.attributes  #NoteAttributes(lastEditorId=139947593, placeName=None, sourceURL=None, classifications=None, creatorId=139947593, author=None, reminderTime=None, altitude=0.0, reminderOrder=None, shareDate=None, reminderDoneTime=None, longitude=114.293, lastEditedBy='\xe5\x91\xa8\xe8\x8e\x89 <305664756@qq.com>', source='mobile.android', applicationData=None, sourceApplication=None, latitude=30.4722, contentClass=None, subjectDate=None)
    print '标签名称表\t', note.tagNames  #这种权限的调用返回None
    # print '共享的笔记表\t', note.sharedNotes  #这种权限的调用没有返回这个值，报错
    # print '限定\t', note.restrictions  #这种权限的调用没有返回这个值，报错
    # print '范围\t', note.limits  #这种权限的调用没有返回这个值，报错


#列出笔记本中的笔记信息
def printnotefromnotebook( notebookguid, notecount):
    notefilter = NoteStore.NoteFilter()
    notefilter.notebookGuid = notebookguid
    notemetaspec = NoteStore.NotesMetadataResultSpec(includeTitle=True, includeContentLength=True, includeCreated=True,
                                              includeUpdated=True, includeDeleted=True, includeUpdateSequenceNum=True,
                                              includeNotebookGuid=True, includeTagGuids=True, includeAttributes=True,
                                              includeLargestResourceMime=True, includeLargestResourceSize=True)
    ourNoteList=note_store.findNotesMetadata(auth_token, notefilter, 0, notecount, notemetaspec)
    # print ourNoteList.notes[-1].title  #测试打印指定note的标题
    # print note_store.getNoteContent(ourNoteList.notes[-1].guid)  #测试打印指定note的内容
    # note = note_store.getNote(auth_token, ourNoteList.notes[9].guid, True, True, True, True)  #获得Note并打印其中的值
    # printnoteattributeundertoken(note)
    # print ourNoteList.notes[5] #打印NoteMetadata

    for note in ourNoteList.notes:
        # print "\t\t\t\t", note.title, "\t", note.guid, "\t", note.contentLength, "\t", note.created, "\t", note.updated
        # print "\t\t\t\t", note.title, "\t", note.guid, "\t", note.contentLength, "\t", timestamp2str(int(note.created/1000)), "\t", timestamp2str(int(note.updated/1000))
        # print note.title.find('天气')
        if note.title.find('天气') > 0:
            soup = BeautifulSoup(note_store.getNoteContent(note.guid), "html.parser")
            tags = soup.find('en-note')
            # print tags
            # print soup.get_text()
            # text = u'【自动更新，请勿编辑】September 19, 2016 at 05:04PM ：最高温度23℃，最低温度19 ℃；风速： 13 ，风向：Northeast；污染 Not Available；日出：September 19, 2016 at 06:09AM，日落：Sunset: September 19, 2016 at 06:23PM；湿度：39%September 20, 2016 at 07:04AM ：最高温度 29 ℃，最低温度18 ℃；风速： 8 ，风向：Northeast；污染： Not Available；日出：September 20, 2016 at 06:09AM，日落：Sunset: September 20, 2016 at 06:21PM；湿度：58%September 21, 2016 at 07:00AM ：最高温度 29 ℃，最低温度18 ℃；风速： 5 ，风向：Northeast；污染： Not Available；日出：September 21, 2016 at 06:10AM，日落：Sunset: September 21, 2016 at 06:20PM；湿度：59%September 22, 2016 at 07:03AM ：最高温度 31 ℃，最低温度19 ℃；风速： 3 ，风向：Southeast；污染： Not Available；日出：September 22, 2016 at 06:11AM，日落：Sunset: September 22, 2016 at 06:19PM；湿度：84%September 23, 2016 at 07:01AM ：最高温度 31 ℃，最低温度21 ℃；风速： 4 ，风向：Southeast；污染： Not Available；日出：September 23, 2016 at 06:11AM，日落：Sunset: September 23, 2016 at 06:18PM；湿度：81%September 24, 2016 at 07:04AM ：最高温度 33 ℃，最低温度23 ℃；风速： 8 ，风向：Southeast；污染： Not Available；日出：September 24, 2016 at 06:12AM，日落：Sunset: September 24, 2016 at 06:16PM；湿度：70%September 25, 2016 at 07:04AM ：最高温度 33 ℃，最低温度24 ℃；风速： 7 ，风向：East；污染： Not Available；日出：September 25, 2016 at 06:12AM，日落：Sunset: September 25, 2016 at 06:15PM；湿度：67%September 26, 2016 at 07:04AM ：最高温度 35 ℃，最低温度23 ℃；风速： 4 ，风向：Northeast；污染： Not Available；日出：September 26, 2016 at 06:13AM，日落：Sunset: September 26, 2016 at 06:14PM；湿度：90%September 27, 2016 at 07:00AM ：最高温度 32 ℃，最低温度22 ℃；风速： 8 ，风向：Northeast；污染： Not Available；日出：September 27, 2016 at 06:13AM，日落：Sunset: September 27, 2016 at 06:13PM；湿度：91%September 28, 2016 at 07:05AM ：最高温度 26 ℃，最低温度14 ℃；风速： 20 ，风向：Northeast；污染： Not Available；日出：September 28, 2016 at 06:14AM，日落：Sunset: September 28, 2016 at 06:11PM；湿度：77%September 29, 2016 at 07:02AM ：最高温度 18 ℃，最低温度16 ℃；风速： 15 ，风向：Northeast；污染： Not Available；日出：September 29, 2016 at 06:15AM，日落：Sunset: September 29, 2016 at 06:10PM；湿度：77%September 30, 2016 at 07:00AM ：最高温度 19 ℃，最低温度17 ℃；风速： 7 ，风向：Northeast；污染： Not Available；日出：September 30, 2016 at 06:15AM，日落：Sunset: September 30, 2016 at 06:09PM；湿度：82%October 01, 2016 at 07:02AM ：最高温度 22 ℃，最低温度18 ℃；风速： 4 ，风向：North；污染： Not Available；日出：October 01, 2016 at 06:16AM，日落：Sunset: October 01, 2016 at 06:08PM；湿度：94%October 02, 2016 at 07:03AM ：最高温度 24 ℃，最低温度17 ℃；风速： 3 ，风向：Northwest；污染： Not Available；日出：October 02, 2016 at 06:16AM，日落：Sunset: October 02, 2016 at 06:07PM；湿度：97%October 03, 2016 at 07:01AM ：最高温度 29 ℃，最低温度18 ℃；风速： 2 ，风向：North；污染： Not Available；日出：October 03, 2016 at 06:17AM，日落：Sunset: October 03, 2016 at 06:05PM；湿度：97%October 04, 2016 at 07:00AM ：最高温度 29 ℃，最低温度17 ℃；风速： 3 ，风向：East；污染： Not Available；日出：October 04, 2016 at 06:18AM，日落：Sunset: October 04, 2016 at 06:04PM；湿度：95%October 05, 2016 at 07:15AM ：最高温度 29 ℃，最低温度19 ℃；风速： 3 ，风向：Northeast；污染： Not Available；日出：October 05, 2016 at 06:18AM，日落：Sunset: October 05, 2016 at 06:03PM；湿度：95%October 06, 2016 at 07:04AM ：最高温度 29 ℃，最低温度20 ℃；风速： 7 ，风向：Northeast；日出：October 06, 2016 at 06:19AM，日落：Sunset: October 06, 2016 at 06:02PM；湿度：87%October 07, 2016 at 07:00AM ：最高温度 27 ℃，最低温度19 ℃；风速： 6 ，风向：Northeast；日出：October 07, 2016 at 06:19AM，日落：Sunset: October 07, 2016 at 06:00PM；湿度：86%October 08, 2016 at 07:01AM ：最高温度 26 ℃，最低温度15 ℃；风速： 10 ，风向：North；日出：October 08, 2016 at 06:20AM，日落：Sunset: October 08, 2016 at 05:59PM；湿度：82%October 09, 2016 at 07:01AM ：最高温度 23 ℃，最低温度14 ℃；风速： 8 ，风向：Northeast；日出：October 09, 2016 at 06:21AM，日落：Sunset: October 09, 2016 at 05:58PM；湿度：68%October 10, 2016 at 07:01AM ：最高温度 22 ℃，最低温度16 ℃；风速： 7 ，风向：Northeast；日出：October 10, 2016 at 06:21AM，日落：Sunset: October 10, 2016 at 05:57PM；湿度：70%October 11, 2016 at 07:01AM ：最高温度 22 ℃，最低温度17 ℃；风速： 5 ，风向：Northeast；日出：October 11, 2016 at 06:22AM，日落：Sunset: October 11, 2016 at 05:56PM；湿度：78%October 12, 2016 at 07:00AM ：最高温度 19 ℃，最低温度16 ℃；风速： 5 ，风向：Northeast；日出：October 12, 2016 at 06:23AM，日落：Sunset: October 12, 2016 at 05:55PM；湿度：92%October 13, 2016 at 07:00AM ：最高温度 19 ℃，最低温度16 ℃；风速： 2 ，风向：Northeast；日出：October 13, 2016 at 06:23AM，日落：Sunset: October 13, 2016 at 05:54PM；湿度：88%October 14, 2016 at 07:00AM ：最高温度 21 ℃，最低温度16 ℃；风速： 2 ，风向：Northeast；日出：October 14, 2016 at 06:24AM，日落：Sunset: October 14, 2016 at 05:52PM；湿度：94%October 15, 2016 at 07:00AM ：最高温度 24 ℃，最低温度17 ℃；风速： 7 ，风向：Northeast；日出：October 15, 2016 at 06:24AM，日落：Sunset: October 15, 2016 at 05:51PM；湿度：95%October 16, 2016 at 07:00AM ：最高温度 26 ℃，最低温度16 ℃；风速： 4 ，风向：North；日出：October 16, 2016 at 06:25AM，日落：Sunset: October 16, 2016 at 05:50PM；湿度：91%October 17, 2016 at 07:00AM ：最高温度 26 ℃，最低温度18 ℃；风速： 4 ，风向：Northeast；日出：October 17, 2016 at 06:26AM，日落：Sunset: October 17, 2016 at 05:49PM；湿度：89%October 18, 2016 at 07:01AM ：最高温度 27 ℃，最低温度19 ℃；风速： 2 ，风向：Northeast；日出：October 18, 2016 at 06:27AM，日落：Sunset: October 18, 2016 at 05:48PM；湿度：93%October 19, 2016 at 06:55AM ：最高温度 24 ℃，最低温度20 ℃；风速： 0 ，风向：Northeast；日出：October 19, 2016 at 06:27AM，日落：Sunset: October 19, 2016 at 05:47PM；湿度：95%October 20, 2016 at 07:00AM ：最高温度 22 ℃，最低温度19 ℃；风速： 7 ，风向：Northeast；日出：October 20, 2016 at 06:28AM，日落：Sunset: October 20, 2016 at 05:46PM；湿度：99%October 21, 2016 at 07:00AM ：最高温度 26 ℃，最低温度19 ℃；风速： 4 ，风向：Northeast；日出：October 21, 2016 at 06:29AM，日落：Sunset: October 21, 2016 at 05:45PM；湿度：97%October 22, 2016 at 07:00AM ：最高温度 20 ℃，最低温度16 ℃；风速： 9 ，风向：North；日出：October 22, 2016 at 06:29AM，日落：Sunset: October 22, 2016 at 05:44PM；湿度：95%October 23, 2016 at 07:01AM ：最高温度 18 ℃，最低温度14 ℃；风速： 7 ，风向：Northeast；日出：October 23, 2016 at 06:30AM，日落：Sunset: October 23, 2016 at 05:43PM；湿度：86%October 24, 2016 at 07:00AM ：最高温度 16 ℃，最低温度13 ℃；风速： 7 ，风向：North；日出：October 24, 2016 at 06:31AM，日落：Sunset: October 24, 2016 at 05:42PM；湿度：92%October 25, 2016 at 07:00AM ：最高温度 16 ℃，最低温度15 ℃；风速： 4 ，风向：North；日出：October 25, 2016 at 06:32AM，日落：Sunset: October 25, 2016 at 05:41PM；湿度：90%October 26, 2016 at 07:00AM ：最高温度 16 ℃，最低温度14 ℃；风速： 2 ，风向：Northwest；日出：October 26, 2016 at 06:32AM，日落：Sunset: October 26, 2016 at 05:40PM；湿度：100%October 27, 2016 at 07:00AM ：最高温度 17 ℃，最低温度14 ℃；风速： 4 ，风向：Northwest；日出：October 27, 2016 at 06:33AM，日落：Sunset: October 27, 2016 at 05:39PM；湿度：97%October 28, 2016 at 07:00AM ：最高温度 13 ℃，最低温度9 ℃；风速： 11 ，风向：North；日出：October 28, 2016 at 06:34AM，日落：Sunset: October 28, 2016 at 05:38PM；湿度：95%October 29, 2016 at 07:00AM ：最高温度 11 ℃，最低温度8 ℃；风速： 9 ，风向：Northeast；日出：October 29, 2016 at 06:35AM，日落：Sunset: October 29, 2016 at 05:38PM；湿度：91%October 30, 2016 at 07:00AM ：最高温度 16 ℃，最低温度12 ℃；风速： 2 ，风向：Northeast；日出：October 30, 2016 at 06:35AM，日落：Sunset: October 30, 2016 at 05:37PM；湿度：95%October 31, 2016 at 07:00AM ：最高温度 15 ℃，最低温度9 ℃；风速： 4 ，风向：Northwest；日出：October 31, 2016 at 06:36AM，日落：Sunset: October 31, 2016 at 05:36PM；湿度：97%November 01, 2016 at 07:00AM ：最高温度 15 ℃，最低温度8 ℃；风速： 4 ，风向：Northeast；日出：November 01, 2016 at 06:37AM，日落：Sunset: November 01, 2016 at 05:35PM；湿度：89%November 02, 2016 at 07:00AM ：最高温度 17 ℃，最低温度9 ℃；风速： 4 ，风向：Northwest；日出：November 02, 2016 at 06:38AM，日落：Sunset: November 02, 2016 at 05:34PM；湿度：94%November 03, 2016 at 07:00AM ：最高温度 18 ℃，最低温度9 ℃；风速： 2 ，风向：Northeast；日出：November 03, 2016 at 06:39AM，日落：Sunset: November 03, 2016 at 05:33PM；湿度：99%November 04, 2016 at 07:00AM ：最高温度 20 ℃，最低温度11 ℃；风速： 0 ，风向：Southeast；日出：November 04, 2016 at 06:39AM，日落：Sunset: November 04, 2016 at 05:32PM；湿度：99%November 05, 2016 at 07:00AM ：最高温度 23 ℃，最低温度13 ℃；风速： 7 ，风向：Southeast；日出：November 05, 2016 at 06:40AM，日落：Sunset: November 05, 2016 at 05:32PM；湿度：99%November 06, 2016 at 07:00AM ：最高温度 23 ℃，最低温度15 ℃；风速： 4 ，风向：Northeast；日出：November 06, 2016 at 06:41AM，日落：Sunset: November 06, 2016 at 05:31PM；湿度：91%November 07, 2016 at 07:00AM ：最高温度 15 ℃，最低温度9 ℃；风速： 7 ，风向：Northeast；日出：November 07, 2016 at 06:42AM，日落：Sunset: November 07, 2016 at 05:30PM；湿度：95%November 08, 2016 at 07:00AM ：最高温度 13 ℃，最低温度8 ℃；风速： 9 ，风向：North；日出：November 08, 2016 at 06:43AM，日落：Sunset: November 08, 2016 at 05:30PM；湿度：87%November 09, 2016 at 07:00AM ：最高温度 10 ℃，最低温度4 ℃；风速： 4 ，风向：Northeast；日出：November 09, 2016 at 06:43AM，日落：Sunset: November 09, 2016 at 05:29PM；湿度：76%November 10, 2016 at 07:00AM ：最高温度 14 ℃，最低温度7 ℃；风速： 4 ，风向：West；日出：November 10, 2016 at 06:44AM，日落：Sunset: November 10, 2016 at 05:28PM；湿度：96%November 11, 2016 at 07:00AM ：最高温度 17 ℃，最低温度9 ℃；风速： 4 ，风向：Southeast；日出：November 11, 2016 at 06:45AM，日落：Sunset: November 11, 2016 at 05:28PM；湿度：100%November 12, 2016 at 07:00AM ：最高温度 20 ℃，最低温度13 ℃；风速： 7 ，风向：Southeast；日出：November 12, 2016 at 06:46AM，日落：Sunset: November 12, 2016 at 05:27PM；湿度：97%November 13, 2016 at 07:00AM ：最高温度 22 ℃，最低温度14 ℃；风速： 4 ，风向：East；日出：November 13, 2016 at 06:47AM，日落：Sunset: November 13, 2016 at 05:27PM；湿度：98%November 14, 2016 at 07:00AM ：最高温度 22 ℃，最低温度14 ℃；风速： 4 ，风向：Northwest；日出：November 14, 2016 at 06:48AM，日落：Sunset: November 14, 2016 at 05:26PM；湿度：99%November 15, 2016 at 07:01AM ：最高温度 19 ℃，最低温度13 ℃；风速： 9 ，风向：Northeast；日出：November 15, 2016 at 06:48AM，日落：Sunset: November 15, 2016 at 05:26PM；湿度：91%November 16, 2016 at 07:00AM ：最高温度 16 ℃，最低温度14 ℃；风速： 9 ，风向：East；日出：November 16, 2016 at 06:49AM，日落：Sunset: November 16, 2016 at 05:25PM；湿度：92%November 17, 2016 at 07:00AM ：最高温度 16 ℃，最低温度14 ℃；风速： 5 ，风向：Northeast；日出：November 17, 2016 at 06:50AM，日落：Sunset: November 17, 2016 at 05:25PM；湿度：98%November 18, 2016 at 07:00AM ：最高温度 16 ℃，最低温度14 ℃；风速： 2 ，风向：Northwest；日出：November 18, 2016 at 06:51AM，日落：Sunset: November 18, 2016 at 05:24PM；湿度：99%November 19, 2016 at 07:00AM ：最高温度 21 ℃，最低温度14 ℃；风速： 2 ，风向：Northwest；日出：November 19, 2016 at 06:52AM，日落：Sunset: November 19, 2016 at 05:24PM；湿度：100%November 20, 2016 at 07:00AM ：最高温度 18 ℃，最低温度14 ℃；风速： 5 ，风向：North；日出：November 20, 2016 at 06:53AM，日落：Sunset: November 20, 2016 at 05:23PM；湿度：92%November 21, 2016 at 07:00AM ：最高温度 18 ℃，最低温度6 ℃；风速： 4 ，风向：Northwest；日出：November 21, 2016 at 06:54AM，日落：Sunset: November 21, 2016 at 05:23PM；湿度：98%November 22, 2016 at 07:00AM ：最高温度 5 ℃，最低温度-1 ℃；风速： 13 ，风向：Northeast；日出：November 22, 2016 at 06:54AM，日落：Sunset: November 22, 2016 at 05:23PM；湿度：89%November 23, 2016 at 07:00AM ：最高温度 1 ℃，最低温度-2 ℃；风速： 9 ，风向：North；日出：November 23, 2016 at 06:55AM，日落：Sunset: November 23, 2016 at 05:23PM；湿度：85%November 24, 2016 at 07:00AM ：最高温度 6 ℃，最低温度2 ℃；风速： 2 ，风向：Northeast；日出：November 24, 2016 at 06:56AM，日落：Sunset: November 24, 2016 at 05:22PM；湿度：76%November 25, 2016 at 07:00AM ：最高温度 7 ℃，最低温度3 ℃；风速： 4 ，风向：Northeast；日出：November 25, 2016 at 06:57AM，日落：Sunset: November 25, 2016 at 05:22PM；湿度：69%November 26, 2016 at 07:00AM ：最高温度 12 ℃，最低温度2 ℃；风速： 4 ，风向：West；日出：November 26, 2016 at 06:58AM，日落：Sunset: November 26, 2016 at 05:22PM；湿度：77%November 27, 2016 at 07:00AM ：最高温度 14 ℃，最低温度3 ℃；风速： 2 ，风向：Southeast；日出：November 27, 2016 at 06:59AM，日落：Sunset: November 27, 2016 at 05:22PM；湿度：95%November 28, 2016 at 07:00AM ：最高温度 14 ℃，最低温度4 ℃；风速： 9 ，风向：Northeast；日出：November 28, 2016 at 07:00AM，日落：Sunset: November 28, 2016 at 05:22PM；湿度：92%November 29, 2016 at 07:01AM ：最高温度 11 ℃，最低温度3 ℃；风速： 7 ，风向：Northeast；日出：November 29, 2016 at 07:00AM，日落：Sunset: November 29, 2016 at 05:21PM；湿度：90%November 30, 2016 at 07:00AM ：最高温度 12 ℃，最低温度4 ℃；风速： 2 ，风向：Northwest；日出：November 30, 2016 at 07:01AM，日落：Sunset: November 30, 2016 at 05:21PM；湿度：98%December 01, 2016 at 07:00AM ：最高温度 14 ℃，最低温度4 ℃；风速： 2 ，风向：Southeast；日出：December 01, 2016 at 07:02AM，日落：Sunset: December 01, 2016 at 05:21PM；湿度：100%December 02, 2016 at 07:00AM ：最高温度 14 ℃，最低温度6 ℃；风速： 2 ，风向：Northeast；日出：December 02, 2016 at 07:03AM，日落：Sunset: December 02, 2016 at 05:21PM；湿度：99%December 03, 2016 at 07:00AM ：最高温度 15 ℃，最低温度6 ℃；风速： 4 ，风向：Southeast；日出：December 03, 2016 at 07:04AM，日落：Sunset: December 03, 2016 at 05:21PM；湿度：87%December 04, 2016 at 07:00AM ：最高温度 17 ℃，最低温度6 ℃；风速： 2 ，风向：Southwest；日出：December 04, 2016 at 07:04AM，日落：Sunset: December 04, 2016 at 05:21PM；湿度：98%December 05, 2016 at 07:00AM ：最高温度 18 ℃，最低温度3 ℃；风速： 4 ，风向：South；日出：December 05, 2016 at 07:05AM，日落：Sunset: December 05, 2016 at 05:21PM；湿度：98%December 06, 2016 at 07:00AM ：最高温度 12 ℃，最低温度4 ℃；风速： 8 ，风向：Northeast；日出：December 06, 2016 at 07:06AM，日落：Sunset: December 06, 2016 at 05:21PM；湿度：87%December 07, 2016 at 07:00AM ：最高温度 15 ℃，最低温度6 ℃；风速： 4 ，风向：Southeast；日出：December 07, 2016 at 07:07AM，日落：Sunset: December 07, 2016 at 05:21PM；湿度：90%December 08, 2016 at 07:00AM ：最高温度 17 ℃，最低温度6 ℃；风速： 3 ，风向：South；日出：December 08, 2016 at 07:07AM，日落：Sunset: December 08, 2016 at 05:22PM；湿度：97%December 09, 2016 at 07:00AM ：最高温度 17 ℃，最低温度6 ℃；风速： 8 ，风向：Northeast；日出：December 09, 2016 at 07:08AM，日落：Sunset: December 09, 2016 at 05:22PM；湿度：89%December 10, 2016 at 07:00AM ：最高温度 14 ℃，最低温度7 ℃；风速： 4 ，风向：North；日出：December 10, 2016 at 07:09AM，日落：Sunset: December 10, 2016 at 05:22PM；湿度：85%December 11, 2016 at 07:01AM ：最高温度 14 ℃，最低温度8 ℃；风速： 4 ，风向：Northeast；日出：December 11, 2016 at 07:10AM，日落：Sunset: December 11, 2016 at 05:22PM；湿度：91%December 12, 2016 at 07:00AM ：最高温度 12 ℃，最低温度8 ℃；风速： 4 ，风向：Northeast；日出：December 12, 2016 at 07:10AM，日落：Sunset: December 12, 2016 at 05:22PM；湿度：90%December 13, 2016 at 07:00AM ：最高温度 11 ℃，最低温度5 ℃；风速： 4 ，风向：Northwest；日出：December 13, 2016 at 07:11AM，日落：Sunset: December 13, 2016 at 05:23PM；湿度：91%December 14, 2016 at 07:00AM ：最高温度 9 ℃，最低温度1 ℃；风速： 11 ，风向：North；日出：December 14, 2016 at 07:12AM，日落：Sunset: December 14, 2016 at 05:23PM；湿度：80%December 15, 2016 at 07:00AM ：最高温度 11 ℃，最低温度2 ℃；风速： 2 ，风向：Northeast；日出：December 15, 2016 at 07:12AM，日落：Sunset: December 15, 2016 at 05:23PM；湿度：88%December 16, 2016 at 07:00AM ：最高温度 11 ℃，最低温度2 ℃；风速： 7 ，风向：Northeast；日出：December 16, 2016 at 07:13AM，日落：Sunset: December 16, 2016 at 05:24PM；湿度：89%December 17, 2016 at 07:00AM ：最高温度 12 ℃，最低温度7 ℃；风速： 9 ，风向：Southeast；日出：December 17, 2016 at 07:13AM，日落：Sunset: December 17, 2016 at 05:24PM；湿度：82%December 18, 2016 at 07:00AM ：最高温度 16 ℃，最低温度9 ℃；风速： 2 ，风向：Southeast；日出：December 18, 2016 at 07:14AM，日落：Sunset: December 18, 2016 at 05:25PM；湿度：77%December 19, 2016 at 07:00AM ：最高温度 13 ℃，最低温度9 ℃；风速： 2 ，风向：Northeast；日出：December 19, 2016 at 07:15AM，日落：Sunset: December 19, 2016 at 05:25PM；湿度：81%December 20, 2016 at 07:00AM ：最高温度 13 ℃，最低温度9 ℃；风速： 9 ，风向：Northeast；日出：December 20, 2016 at 07:15AM，日落：Sunset: December 20, 2016 at 05:25PM；湿度：95%December 21, 2016 at 07:00AM ：最高温度 9 ℃，最低温度4 ℃；风速： 9 ，风向：Northwest；日出：December 21, 2016 at 07:16AM，日落：Sunset: December 21, 2016 at 05:26PM；湿度：99%December 22, 2016 at 07:00AM ：最高温度 13 ℃，最低温度2 ℃；风速： 4 ，风向：West；日出：December 22, 2016 at 07:16AM，日落：Sunset: December 22, 2016 at 05:27PM；湿度：97%December 23, 2016 at 07:00AM ：最高温度 14 ℃，最低温度7 ℃；风速： 11 ，风向：Northeast；日出：December 23, 2016 at 07:17AM，日落：Sunset: December 23, 2016 at 05:27PM；湿度：92%December 24, 2016 at 07:00AM ：最高温度 9 ℃，最低温度7 ℃；风速： 9 ，风向：Northeast；日出：December 24, 2016 at 07:17AM，日落：Sunset: December 24, 2016 at 05:28PM；湿度：72%December 25, 2016 at 07:00AM ：最高温度 8 ℃，最低温度5 ℃；风速： 9 ，风向：Northeast；日出：December 25, 2016 at 07:18AM，日落：Sunset: December 25, 2016 at 05:28PM；湿度：95%December 26, 2016 at 07:00AM ：最高温度 8 ℃，最低温度2 ℃；风速： 7 ，风向：Northwest；日出：December 26, 2016 at 07:18AM，日落：Sunset: December 26, 2016 at 05:29PM；湿度：90%December 27, 2016 at 07:00AM ：最高温度 9 ℃，最低温度0 ℃；风速： 2 ，风向：North；日出：December 27, 2016 at 07:18AM，日落：Sunset: December 27, 2016 at 05:29PM；湿度：95%December 28, 2016 at 07:00AM ：最高温度 8 ℃，最低温度0 ℃；风速： 9 ，风向：Southeast；日出：December 28, 2016 at 07:19AM，日落：Sunset: December 28, 2016 at 05:30PM；湿度：93%December 29, 2016 at 07:00AM ：最高温度 8 ℃，最低温度1 ℃；风速： 7 ，风向：Northeast；日出：December 29, 2016 at 07:19AM，日落：Sunset: December 29, 2016 at 05:31PM；湿度：86%December 30, 2016 at 07:01AM ：最高温度 10 ℃，最低温度1 ℃；风速： 7 ，风向：East；日出：December 30, 2016 at 07:19AM，日落：Sunset: December 30, 2016 at 05:31PM；湿度：93%December 31, 2016 at 07:00AM ：最高温度 13 ℃，最低温度4 ℃；风速： 7 ，风向：East；日出：December 31, 2016 at 07:20AM，日落：Sunset: December 31, 2016 at 05:32PM；湿度：96%January 01, 2017 at 07:00AM ：最高温度 15 ℃，最低温度7 ℃；风速： 9 ，风向：Southeast；日出：January 01, 2017 at 07:20AM，日落：Sunset: January 01, 2017 at 05:33PM；湿度：84%January 02, 2017 at 07:00AM ：最高温度 16 ℃，最低温度6 ℃；风速： 4 ，风向：North；日出：January 02, 2017 at 07:20AM，日落：Sunset: January 02, 2017 at 05:33PM；湿度：87%January 03, 2017 at 07:00AM ：最高温度 16 ℃，最低温度11 ℃；风速： 2 ，风向：Northeast；日出：January 03, 2017 at 07:20AM，日落：Sunset: January 03, 2017 at 05:34PM；湿度：93%January 04, 2017 at 07:00AM ：最高温度 14 ℃，最低温度11 ℃；风速： 4 ，风向：Northeast；日出：January 04, 2017 at 07:20AM，日落：Sunset: January 04, 2017 at 05:35PM；湿度：87%January 05, 2017 at 07:00AM ：最高温度 10 ℃，最低温度8 ℃；风速： 4 ，风向：North；日出：January 05, 2017 at 07:21AM，日落：Sunset: January 05, 2017 at 05:36PM；湿度：99%January 06, 2017 at 07:00AM ：最高温度 9 ℃，最低温度7 ℃；风速： 7 ，风向：Northeast；日出：January 06, 2017 at 07:21AM，日落：Sunset: January 06, 2017 at 05:36PM；湿度：97%January 07, 2017 at 07:00AM ：最高温度 9 ℃，最低温度3 ℃；风速： 7 ，风向：Northwest；日出：January 07, 2017 at 07:21AM，日落：Sunset: January 07, 2017 at 05:37PM；湿度：94%January 08, 2017 at 07:00AM ：最高温度 12 ℃，最低温度2 ℃；风速： 2 ，风向：North；日出：January 08, 2017 at 07:21AM，日落：Sunset: January 08, 2017 at 05:38PM；湿度：95%January 09, 2017 at 07:00AM ：最高温度 11 ℃，最低温度6 ℃；风速： 4 ，风向：Northeast；日出：January 09, 2017 at 07:21AM，日落：Sunset: January 09, 2017 at 05:39PM；湿度：93%January 10, 2017 at 07:00AM ：最高温度 9 ℃，最低温度4 ℃；风速： 9 ，风向：Northeast；日出：January 10, 2017 at 07:21AM，日落：Sunset: January 10, 2017 at 05:40PM；湿度：82%January 11, 2017 at 07:00AM ：最高温度 7 ℃，最低温度4 ℃；风速： 4 ，风向：Northeast；日出：January 11, 2017 at 07:21AM，日落：Sunset: January 11, 2017 at 05:40PM；湿度：90%January 12, 2017 at 07:00AM ：最高温度 11 ℃，最低温度1 ℃；风速： 4 ，风向：West；日出：January 12, 2017 at 07:21AM，日落：Sunset: January 12, 2017 at 05:41PM；湿度：97%January 13, 2017 at 06:00AM ：最高温度 12 ℃，最低温度3 ℃；风速： 2 ，风向：West；日出：January 13, 2017 at 07:21AM，日落：Sunset: January 13, 2017 at 05:42PM；湿度：94%January 14, 2017 at 06:00AM ：最高温度 11 ℃，最低温度3 ℃；风速： 4 ，风向：Northeast；日出：January 14, 2017 at 07:21AM，日落：Sunset: January 14, 2017 at 05:43PM；湿度：76%January 15, 2017 at 06:00AM ：最高温度 9 ℃，最低温度1 ℃；风速： 2 ，风向：Northeast；日出：January 15, 2017 at 07:21AM，日落：Sunset: January 15, 2017 at 05:44PM；湿度：74%January 16, 2017 at 06:00AM ：最高温度 10 ℃，最低温度4 ℃；风速： 2 ，风向：Northeast；日出：January 16, 2017 at 07:20AM，日落：Sunset: January 16, 2017 at 05:45PM；湿度：93%January 17, 2017 at 06:00AM ：最高温度 11 ℃，最低温度5 ℃；风速： 4 ，风向：North；日出：January 17, 2017 at 07:20AM，日落：Sunset: January 17, 2017 at 05:46PM；湿度：83%January 18, 2017 at 06:00AM ：最高温度 9 ℃，最低温度4 ℃；风速： 4 ，风向：Northeast；日出：January 18, 2017 at 07:20AM，日落：Sunset: January 18, 2017 at 05:47PM；湿度：83%January 19, 2017 at 06:00AM ：最高温度 11 ℃，最低温度-1 ℃；风速： 6 ，风向：Northwest；日出：January 19, 2017 at 07:20AM，日落：Sunset: January 19, 2017 at 05:47PM；湿度：93%January 20, 2017 at 06:00AM ：最高温度 7 ℃，最低温度-1 ℃；风速： 7 ，风向：Northeast；日出：January 20, 2017 at 07:19AM，日落：Sunset: January 20, 2017 at 05:48PM；湿度：50%January 21, 2017 at 06:00AM ：最高温度 9 ℃，最低温度1 ℃；风速： 0 ，风向：Southeast；日出：January 21, 2017 at 07:19AM，日落：Sunset: January 21, 2017 at 05:49PM；湿度：76%January 22, 2017 at 06:00AM ：最高温度 12 ℃，最低温度2 ℃；风速： 0 ，风向：Northeast；日出：January 22, 2017 at 07:19AM，日落：Sunset: January 22, 2017 at 05:50PM；湿度：87%January 23, 2017 at 06:00AM ：最高温度 12 ℃，最低温度3 ℃；风速： 0 ，风向：East；日出：January 23, 2017 at 07:18AM，日落：Sunset: January 23, 2017 at 05:51PM；湿度：82%January 24, 2017 at 06:00AM ：最高温度 13 ℃，最低温度4 ℃；风速： 2 ，风向：Northwest；日出：January 24, 2017 at 07:18AM，日落：Sunset: January 24, 2017 at 05:52PM；湿度：72%January 25, 2017 at 06:00AM ：最高温度 14 ℃，最低温度4 ℃；风速： 2 ，风向：Northwest；日出：January 25, 2017 at 07:18AM，日落：Sunset: January 25, 2017 at 05:53PM；湿度：84%January 26, 2017 at 06:00AM ：最高温度 16 ℃，最低温度6 ℃；风速： 4 ，风向：Southwest；日出：January 26, 2017 at 07:17AM，日落：Sunset: January 26, 2017 at 05:53PM；湿度：91%January 27, 2017 at 06:00AM ：最高温度 14 ℃，最低温度7 ℃；风速： 2 ，风向：Northwest；日出：January 27, 2017 at 07:17AM，日落：Sunset: January 27, 2017 at 05:54PM；湿度：79%January 28, 2017 at 06:00AM ：最高温度 17 ℃，最低温度9 ℃；风速： 7 ，风向：Southeast；日出：January 28, 2017 at 07:16AM，日落：Sunset: January 28, 2017 at 05:55PM；湿度：80%January 29, 2017 at 06:00AM ：最高温度 9 ℃，最低温度1 ℃；风速： 9 ，风向：North；日出：January 29, 2017 at 07:16AM，日落：Sunset: January 29, 2017 at 05:56PM；湿度：84%January 30, 2017 at 06:00AM ：最高温度 8 ℃，最低温度2 ℃；风速： 7 ，风向：Northeast；日出：January 30, 2017 at 07:15AM，日落：Sunset: January 30, 2017 at 05:57PM；湿度：77%January 31, 2017 at 06:00AM ：最高温度 5 ℃，最低温度2 ℃；风速： 7 ，风向：Northeast；日出：January 31, 2017 at 07:15AM，日落：Sunset: January 31, 2017 at 05:58PM；湿度：70%February 01, 2017 at 06:00AM ：最高温度 8 ℃，最低温度3 ℃；风速： 4 ，风向：North；日出：February 01, 2017 at 07:14AM，日落：Sunset: February 01, 2017 at 05:59PM；湿度：92%February 02, 2017 at 06:00AM ：最高温度 6 ℃，最低温度4 ℃；风速： 7 ，风向：Northeast；日出：February 02, 2017 at 07:13AM，日落：Sunset: February 02, 2017 at 05:59PM；湿度：91%February 03, 2017 at 06:00AM ：最高温度 6 ℃，最低温度3 ℃；风速： 4 ，风向：North；日出：February 03, 2017 at 07:13AM，日落：Sunset: February 03, 2017 at 06:00PM；湿度：99%February 04, 2017 at 06:00AM ：最高温度 11 ℃，最低温度2 ℃；风速： 0 ，风向：Northwest；日出：February 04, 2017 at 07:12AM，日落：Sunset: February 04, 2017 at 06:01PM；湿度：96%February 05, 2017 at 06:00AM ：最高温度 13 ℃，最低温度4 ℃；风速： 2 ，风向：East；日出：February 05, 2017 at 07:11AM，日落：Sunset: February 05, 2017 at 06:02PM；湿度：96%February 06, 2017 at 06:00AM ：最高温度 14 ℃，最低温度5 ℃；风速： 2 ，风向：Northeast；日出：February 06, 2017 at 07:11AM，日落：Sunset: February 06, 2017 at 06:03PM；湿度：99%February 07, 2017 at 06:00AM ：最高温度 7 ℃，最低温度2 ℃；风速： 7 ，风向：Northeast；日出：February 07, 2017 at 07:10AM，日落：Sunset: February 07, 2017 at 06:04PM；湿度：67%February 08, 2017 at 06:00AM ：最高温度 7 ℃，最低温度-1 ℃；风速： 9 ，风向：Northwest；日出：February 08, 2017 at 07:09AM，日落：Sunset: February 08, 2017 at 06:04PM；湿度：94%February 09, 2017 at 06:00AM ：最高温度 8 ℃，最低温度-1 ℃；风速： 2 ，风向：Northeast；日出：February 09, 2017 at 07:08AM，日落：Sunset: February 09, 2017 at 06:05PM；湿度：91%February 10, 2017 at 06:00AM ：最高温度 9 ℃，最低温度-1 ℃；风速： 0 ，风向：Northeast；日出：February 10, 2017 at 07:08AM，日落：Sunset: February 10, 2017 at 06:06PM；湿度：88%February 11, 2017 at 06:00AM ：最高温度 11 ℃，最低温度1 ℃；风速： 0 ，风向：Northeast；日出：February 11, 2017 at 07:07AM，日落：Sunset: February 11, 2017 at 06:07PM；湿度：70%February 12, 2017 at 06:00AM ：最高温度 14 ℃，最低温度2 ℃；风速： 2 ，风向：Southeast；日出：February 12, 2017 at 07:06AM，日落：Sunset: February 12, 2017 at 06:08PM；湿度：86%February 13, 2017 at 06:00AM ：最高温度 17 ℃，最低温度6 ℃；风速： 0 ，风向：East；日出：February 13, 2017 at 07:05AM，日落：Sunset: February 13, 2017 at 06:09PM；湿度：83%February 14, 2017 at 06:00AM ：最高温度 17 ℃，最低温度6 ℃；风速： 2 ，风向：North；日出：February 14, 2017 at 07:04AM，日落：Sunset: February 14, 2017 at 06:09PM；湿度：77%February 15, 2017 at 06:00AM ：最高温度 19 ℃，最低温度10 ℃；风速： 2 ，风向：Southeast；日出：February 15, 2017 at 07:03AM，日落：Sunset: February 15, 2017 at 06:10PM；湿度：85%February 16, 2017 at 06:00AM ：最高温度 22 ℃，最低温度11 ℃；风速： 4 ，风向：Southwest；日出：February 16, 2017 at 07:02AM，日落：Sunset: February 16, 2017 at 06:11PM；湿度：78%February 17, 2017 at 06:00AM ：最高温度 15 ℃，最低温度7 ℃；风速： 18 ，风向：Northeast；日出：February 17, 2017 at 07:01AM，日落：Sunset: February 17, 2017 at 06:12PM；湿度：71%February 18, 2017 at 06:00AM ：最高温度 17 ℃，最低温度9 ℃；风速： 2 ，风向：Northwest；日出：February 18, 2017 at 07:01AM，日落：Sunset: February 18, 2017 at 06:13PM；湿度：84%February 19, 2017 at 06:00AM ：最高温度 22 ℃，最低温度14 ℃；风速： 4 ，风向：Southeast；日出：February 19, 2017 at 06:59AM，日落：Sunset: February 19, 2017 at 06:13PM；湿度：92%February 20, 2017 at 06:00AM ：最高温度 15 ℃，最低温度6 ℃；风速： 0 ，风向：Northeast；日出：February 20, 2017 at 06:58AM，日落：Sunset: February 20, 2017 at 06:14PM；湿度：89%February 21, 2017 at 06:00AM ：最高温度 8 ℃，最低温度1 ℃；风速： 9 ，风向：Northeast；日出：February 21, 2017 at 06:58AM，日落：Sunset: February 21, 2017 at 06:15PM；湿度：61%February 22, 2017 at 06:00AM ：最高温度 7 ℃，最低温度3 ℃；风速： 0 ，风向：Northwest；日出：February 22, 2017 at 06:57AM，日落：Sunset: February 22, 2017 at 06:16PM；湿度：88%February 23, 2017 at 06:00AM ：最高温度 12 ℃，最低温度4 ℃；风速： 2 ，风向：Northwest；日出：February 23, 2017 at 06:55AM，日落：Sunset: February 23, 2017 at 06:16PM；湿度：86%February 24, 2017 at 06:00AM ：最高温度 12 ℃，最低温度4 ℃；风速： 2 ，风向：Northwest；日出：February 24, 2017 at 06:54AM，日落：Sunset: February 24, 2017 at 06:17PM；湿度：88%February 25, 2017 at 06:00AM ：最高温度 14 ℃，最低温度4 ℃；风速： 0 ，风向：West；日出：February 25, 2017 at 06:53AM，日落：Sunset: February 25, 2017 at 06:18PM；湿度：86%February 26, 2017 at 06:00AM ：最高温度 17 ℃，最低温度6 ℃；风速： 0 ，风向：Northwest；日出：February 26, 2017 at 06:52AM，日落：Sunset: February 26, 2017 at 06:19PM；湿度：87%February 27, 2017 at 06:00AM ：最高温度 18 ℃，最低温度7 ℃；风速： 0 ，风向：Northeast；日出：February 27, 2017 at 06:51AM，日落：Sunset: February 27, 2017 at 06:19PM；湿度：76%February 28, 2017 at 06:00AM ：最高温度 19 ℃，最低温度8 ℃；风速： 2 ，风向：Northeast；日出：February 28, 2017 at 06:50AM，日落：Sunset: February 28, 2017 at 06:20PM；湿度：75%March 01, 2017 at 06:00AM ：最高温度 17 ℃，最低温度2 ℃；风速： 4 ，风向：West；日出：March 01, 2017 at 06:49AM，日落：Sunset: March 01, 2017 at 06:21PM；湿度：79%March 02, 2017 at 06:00AM ：最高温度 14 ℃，最低温度5 ℃；风速： 2 ，风向：Northwest；日出：March 02, 2017 at 06:48AM，日落：Sunset: March 02, 2017 at 06:21PM；湿度：73%March 03, 2017 at 06:00AM ：最高温度 18 ℃，最低温度9 ℃；风速： 4 ，风向：Southeast；日出：March 03, 2017 at 06:47AM，日落：Sunset: March 03, 2017 at 06:22PM；湿度：65%March 04, 2017 at 06:00AM ：最高温度 13 ℃，最低温度9 ℃；风速： 2 ，风向：Northeast；日出：March 04, 2017 at 06:46AM，日落：Sunset: March 04, 2017 at 06:23PM；湿度：74%March 05, 2017 at 06:00AM ：最高温度 16 ℃，最低温度8 ℃；风速： 0 ，风向：North；日出：March 05, 2017 at 06:44AM，日落：Sunset: March 05, 2017 at 06:24PM；湿度：97%March 06, 2017 at 06:00AM ：最高温度 17 ℃，最低温度7 ℃；风速： 4 ，风向：Northeast；日出：March 06, 2017 at 06:43AM，日落：Sunset: March 06, 2017 at 06:24PM；湿度：79%March 07, 2017 at 06:00AM ：最高温度 18 ℃，最低温度5 ℃；风速： 0 ，风向：Northeast；日出：March 07, 2017 at 06:42AM，日落：Sunset: March 07, 2017 at 06:25PM；湿度：90%March 08, 2017 at 06:00AM ：最高温度 18 ℃，最低温度7 ℃；风速： 0 ，风向：Northeast；日出：March 08, 2017 at 06:41AM，日落：Sunset: March 08, 2017 at 06:26PM；湿度：80%March 09, 2017 at 06:00AM ：最高温度 20 ℃，最低温度11 ℃；风速： 0 ，风向：Southeast；日出：March 09, 2017 at 06:40AM，日落：Sunset: March 09, 2017 at 06:26PM；湿度：82%March 10, 2017 at 06:00AM ：最高温度 14 ℃，最低温度11 ℃；风速： 2 ，风向：Southeast；日出：March 10, 2017 at 06:39AM，日落：Sunset: March 10, 2017 at 06:27PM；湿度：92%March 11, 2017 at 06:00AM ：最高温度 19 ℃，最低温度12 ℃；风速： 2 ，风向：Northeast；日出：March 11, 2017 at 06:37AM，日落：Sunset: March 11, 2017 at 06:28PM；湿度：95%March 12, 2017 at 06:00AM ：最高温度 16 ℃，最低温度10 ℃；风速： 2 ，风向：Northeast；日出：March 12, 2017 at 06:36AM，日落：Sunset: March 12, 2017 at 06:28PM；湿度：93%March 13, 2017 at 06:00AM ：最高温度 9 ℃，最低温度5 ℃；风速： 9 ，风向：Northeast；日出：March 13, 2017 at 06:35AM，日落：Sunset: March 13, 2017 at 06:29PM；湿度：93%March 14, 2017 at 06:00AM ：最高温度 14 ℃，最低温度7 ℃；风速： 4 ，风向：Northeast；日出：March 14, 2017 at 06:34AM，日落：Sunset: March 14, 2017 at 06:30PM；湿度：73%March 15, 2017 at 06:00AM ：最高温度 13 ℃，最低温度7 ℃；风速： 4 ，风向：East；日出：March 15, 2017 at 06:32AM，日落：Sunset: March 15, 2017 at 06:30PM；湿度：61%March 16, 2017 at 06:00AM ：最高温度 16 ℃，最低温度8 ℃；风速： 2 ，风向：West；日出：March 16, 2017 at 06:31AM，日落：Sunset: March 16, 2017 at 06:31PM；湿度：89%March 17, 2017 at 06:00AM ：最高温度 13 ℃，最低温度9 ℃；风速： 2 ，风向：Southeast；日出：March 17, 2017 at 06:30AM，日落：Sunset: March 17, 2017 at 06:32PM；湿度：92%March 18, 2017 at 06:00AM ：最高温度 17 ℃，最低温度11 ℃；风速： 2 ，风向：North；日出：March 18, 2017 at 06:29AM，日落：Sunset: March 18, 2017 at 06:32PM；湿度：95%March 19, 2017 at 06:00AM ：最高温度 13 ℃，最低温度11 ℃；风速： 2 ，风向：West；日出：March 19, 2017 at 06:28AM，日落：Sunset: March 19, 2017 at 06:33PM；湿度：93%March 20, 2017 at 06:00AM ：最高温度 16 ℃，最低温度7 ℃；风速： 2 ，风向：Northwest；日出：March 20, 2017 at 06:26AM，日落：Sunset: March 20, 2017 at 06:34PM；湿度：95%March 21, 2017 at 06:00AM ：最高温度 15 ℃，最低温度9 ℃；风速： 2 ，风向：North；日出：March 21, 2017 at 06:25AM，日落：Sunset: March 21, 2017 at 06:34PM；湿度：91%March 22, 2017 at 06:00AM ：最高温度 12 ℃，最低温度7 ℃；风速： 2 ，风向：Northeast；日出：March 22, 2017 at 06:24AM，日落：Sunset: March 22, 2017 at 06:35PM；湿度：97%March 23, 2017 at 06:00AM ：最高温度 14 ℃，最低温度9 ℃；风速： 4 ，风向：Northeast；日出：March 23, 2017 at 06:23AM，日落：Sunset: March 23, 2017 at 06:35PM；湿度：93%March 24, 2017 at 06:00AM ：最高温度 11 ℃，最低温度7 ℃；风速： 4 ，风向：North；日出：March 24, 2017 at 06:21AM，日落：Sunset: March 24, 2017 at 06:36PM；湿度：94%March 25, 2017 at 06:00AM ：最高温度 18 ℃，最低温度8 ℃；风速： 0 ，风向：West；日出：March 25, 2017 at 06:20AM，日落：Sunset: March 25, 2017 at 06:37PM；湿度：98%March 26, 2017 at 06:00AM ：最高温度 19 ℃，最低温度8 ℃；风速： 2 ，风向：East；日出：March 26, 2017 at 06:19AM，日落：Sunset: March 26, 2017 at 06:37PM；湿度：96%March 27, 2017 at 06:00AM ：最高温度 23 ℃，最低温度13 ℃；风速： 2 ，风向：South；日出：March 27, 2017 at 06:18AM，日落：Sunset: March 27, 2017 at 06:38PM；湿度：91%March 28, 2017 at 06:00AM ：最高温度 24 ℃，最低温度11 ℃；风速： 4 ，风向：Southeast；日出：March 28, 2017 at 06:17AM，日落：Sunset: March 28, 2017 at 06:39PM；湿度：70%March 29, 2017 at 06:00AM ：最高温度 22 ℃，最低温度14 ℃；风速： 4 ，风向：Northeast；日出：March 29, 2017 at 06:15AM，日落：Sunset: March 29, 2017 at 06:39PM；湿度：88%March 30, 2017 at 06:00AM ：最高温度 16 ℃，最低温度10 ℃；风速： 4 ，风向：Northwest；日出：March 30, 2017 at 06:14AM，日落：Sunset: March 30, 2017 at 06:40PM；湿度：93%March 31, 2017 at 06:00AM ：最高温度 18 ℃，最低温度8 ℃；风速： 2 ，风向：Northwest；日出：March 31, 2017 at 06:13AM，日落：Sunset: March 31, 2017 at 06:40PM；湿度：86%April 01, 2017 at 06:00AM ：最高温度 21 ℃，最低温度9 ℃；风速： 0 ，风向：North；日出：April 01, 2017 at 06:12AM，日落：Sunset: April 01, 2017 at 06:41PM；湿度：91%April 02, 2017 at 06:00AM ：最高温度 23 ℃，最低温度13 ℃；风速： 4 ，风向：Southeast；日出：April 02, 2017 at 06:11AM，日落：Sunset: April 02, 2017 at 06:42PM；湿度：89%April 03, 2017 at 06:00AM ：最高温度 20 ℃，最低温度16 ℃；风速： 11 ，风向：Southeast；日出：April 03, 2017 at 06:09AM，日落：Sunset: April 03, 2017 at 06:42PM；湿度：69%April 04, 2017 at 06:00AM ：最高温度 20 ℃，最低温度16 ℃；风速： 9 ，风向：Southeast；日出：April 04, 2017 at 06:08AM，日落：Sunset: April 04, 2017 at 06:43PM；湿度：69%April 05, 2017 at 06:00AM ：最高温度 20 ℃，最低温度17 ℃；风速： 2 ，风向：Northwest；日出：April 05, 2017 at 06:07AM，日落：Sunset: April 05, 2017 at 06:44PM；湿度：97%April 06, 2017 at 06:00AM ：最高温度 21 ℃，最低温度16 ℃；风速： 7 ，风向：Northeast；日出：April 06, 2017 at 06:06AM，日落：Sunset: April 06, 2017 at 06:44PM；湿度：94%April 07, 2017 at 06:00AM ：最高温度 23 ℃，最低温度17 ℃；风速： 0 ，风向：Northeast；日出：April 07, 2017 at 06:05AM，日落：Sunset: April 07, 2017 at 06:45PM；湿度：98%April 08, 2017 at 06:00AM ：最高温度 25 ℃，最低温度16 ℃；风速： 4 ，风向：Southeast；日出：April 08, 2017 at 06:03AM，日落：Sunset: April 08, 2017 at 06:46PM；湿度：93%April 09, 2017 at 06:00AM ：最高温度 16 ℃，最低温度10 ℃；风速： 13 ，风向：Northeast；日出：April 09, 2017 at 06:02AM，日落：Sunset: April 09, 2017 at 06:46PM；湿度：90%April 10, 2017 at 06:00AM ：最高温度 10 ℃，最低温度6 ℃；风速： 7 ，风向：Northeast；日出：April 10, 2017 at 06:01AM，日落：Sunset: April 10, 2017 at 06:47PM；湿度：89%April 11, 2017 at 06:00AM ：最高温度 18 ℃，最低温度10 ℃；风速： 0 ，风向：Northwest；日出：April 11, 2017 at 06:00AM，日落：Sunset: April 11, 2017 at 06:47PM；湿度：93%April 12, 2017 at 06:00AM ：最高温度 21 ℃，最低温度11 ℃；风速： 4 ，风向：North；日出：April 12, 2017 at 05:59AM，日落：Sunset: April 12, 2017 at 06:48PM；湿度：95%April 13, 2017 at 06:00AM ：最高温度 23 ℃，最低温度13 ℃；风速： 0 ，风向：South；日出：April 13, 2017 at 05:58AM，日落：Sunset: April 13, 2017 at 06:49PM；湿度：97%April 14, 2017 at 06:00AM ：最高温度 27 ℃，最低温度16 ℃；风速： 2 ，风向：Southeast；日出：April 14, 2017 at 05:57AM，日落：Sunset: April 14, 2017 at 06:49PM；湿度：90%April 15, 2017 at 06:00AM ：最高温度 29 ℃，最低温度19 ℃；风速： 0 ，风向：Southeast；日出：April 15, 2017 at 05:55AM，日落：Sunset: April 15, 2017 at 06:50PM；湿度：89%April 16, 2017 at 06:00AM ：最高温度 26 ℃，最低温度15 ℃；风速： 2 ，风向：East；日出：April 16, 2017 at 05:54AM，日落：Sunset: April 16, 2017 at 06:51PM；湿度：93%April 17, 2017 at 06:00AM ：最高温度 26 ℃，最低温度17 ℃；风速： 0 ，风向：Northwest；日出：April 17, 2017 at 05:53AM，日落：Sunset: April 17, 2017 at 06:51PM；湿度：85%April 18, 2017 at 06:00AM ：最高温度 28 ℃，最低温度17 ℃；风速： 4 ，风向：Southwest；日出：April 18, 2017 at 05:52AM，日落：Sunset: April 18, 2017 at 06:52PM；湿度：79%April 19, 2017 at 06:00AM ：最高温度 25 ℃，最低温度16 ℃；风速： 2 ，风向：Southeast；日出：April 19, 2017 at 05:51AM，日落：Sunset: April 19, 2017 at 06:53PM；湿度：88%April 20, 2017 at 06:00AM ：最高温度 22 ℃，最低温度14 ℃；风速： 4 ，风向：Northwest；日出：April 20, 2017 at 05:50AM，日落：Sunset: April 20, 2017 at 06:53PM；湿度：76%April 21, 2017 at 06:00AM ：最高温度 20 ℃，最低温度11 ℃；风速： 4 ，风向：Northwest；日出：April 21, 2017 at 05:49AM，日落：Sunset: April 21, 2017 at 06:54PM；湿度：85%April 22, 2017 at 06:00AM ：最高温度 23 ℃，最低温度12 ℃；风速： 0 ，风向：Northwest；日出：April 22, 2017 at 05:48AM，日落：Sunset: April 22, 2017 at 06:55PM；湿度：93%April 23, 2017 at 06:00AM ：最高温度 25 ℃，最低温度14 ℃；风速： 2 ，风向：Southeast；日出：April 23, 2017 at 05:47AM，日落：Sunset: April 23, 2017 at 06:55PM；湿度：84%April 24, 2017 at 06:00AM ：最高温度 28 ℃，最低温度18 ℃；风速： 4 ，风向：Southeast；日出：April 24, 2017 at 05:46AM，日落：Sunset: April 24, 2017 at 06:56PM；湿度：86%April 25, 2017 at 06:00AM ：最高温度 19 ℃，最低温度15 ℃；风速： 4 ，风向：Northwest；日出：April 25, 2017 at 05:45AM，日落：Sunset: April 25, 2017 at 06:57PM；湿度：86%April 26, 2017 at 06:00AM ：最高温度 21 ℃，最低温度14 ℃；风速： 9 ，风向：North；日出：April 26, 2017 at 05:44AM，日落：Sunset: April 26, 2017 at 06:57PM；湿度：90%April 27, 2017 at 06:00AM ：最高温度 23 ℃，最低温度13 ℃；风速： 4 ，风向：Northwest；日出：April 27, 2017 at 05:43AM，日落：Sunset: April 27, 2017 at 06:58PM；湿度：68%April 28, 2017 at 06:00AM ：最高温度 26 ℃，最低温度14 ℃；风速： 0 ，风向：Southwest；日出：April 28, 2017 at 05:42AM，日落：Sunset: April 28, 2017 at 06:59PM；湿度：83%April 29, 2017 at 06:00AM ：最高温度 28 ℃，最低温度15 ℃；风速： 4 ，风向：South；日出：April 29, 2017 at 05:41AM，日落：Sunset: April 29, 2017 at 06:59PM；湿度：85%April 30, 2017 at 06:00AM ：最高温度 30 ℃，最低温度18 ℃；风速： 2 ，风向：Southeast；日出：April 30, 2017 at 05:40AM，日落：Sunset: April 30, 2017 at 07:00PM；湿度：81%May 01, 2017 at 06:00AM ：最高温度 23 ℃，最低温度17 ℃；风速： 2 ，风向：Southeast；日出：May 01, 2017 at 05:39AM，日落：Sunset: May 01, 2017 at 07:01PM；湿度：77%May 02, 2017 at 06:00AM ：最高温度 28 ℃，最低温度17 ℃；风速： 2 ，风向：Northwest；日出：May 02, 2017 at 05:38AM，日落：Sunset: May 02, 2017 at 07:01PM；湿度：93%May 03, 2017 at 06:00AM ：最高温度 25 ℃，最低温度17 ℃；风速： 9 ，风向：East；日出：May 03, 2017 at 05:38AM，日落：Sunset: May 03, 2017 at 07:02PM；湿度：85%May 04, 2017 at 06:00AM ：最高温度 26 ℃，最低温度16 ℃；风速： 7 ，风向：Northwest；日出：May 04, 2017 at 05:37AM，日落：Sunset: May 04, 2017 at 07:03PM；湿度：85%May 05, 2017 at 06:00AM ：最高温度 28 ℃，最低温度17 ℃；风速： 0 ，风向：Northeast；日出：May 05, 2017 at 05:36AM，日落：Sunset: May 05, 2017 at 07:03PM；湿度：94%May 06, 2017 at 06:00AM ：最高温度 24 ℃，最低温度16 ℃；风速： 4 ，风向：Northeast；日出：May 06, 2017 at 05:35AM，日落：Sunset: May 06, 2017 at 07:04PM；湿度：52%May 07, 2017 at 06:00AM ：最高温度 23 ℃，最低温度17 ℃；风速： 0 ，风向：North；日出：May 07, 2017 at 05:34AM，日落：Sunset: May 07, 2017 at 07:05PM；湿度：84%May 08, 2017 at 06:00AM ：最高温度 26 ℃，最低温度16 ℃；风速： 4 ，风向：Northwest；日出：May 08, 2017 at 05:33AM，日落：Sunset: May 08, 2017 at 07:05PM；湿度：96%May 09, 2017 at 06:00AM ：最高温度 29 ℃，最低温度17 ℃；风速： 0 ，风向：West；日出：May 09, 2017 at 05:33AM，日落：Sunset: May 09, 2017 at 07:06PM；湿度：94%May 10, 2017 at 06:00AM ：最高温度 32 ℃，最低温度21 ℃；风速： 0 ，风向：Southeast；日出：May 10, 2017 at 05:32AM，日落：Sunset: May 10, 2017 at 07:07PM；湿度：89%May 11, 2017 at 06:00AM ：最高温度 25 ℃，最低温度17 ℃；风速： 9 ，风向：Southeast；日出：May 11, 2017 at 05:31AM，日落：Sunset: May 11, 2017 at 07:07PM；湿度：84%May 12, 2017 at 06:00AM ：最高温度 29 ℃，最低温度18 ℃；风速： 0 ，风向：Northwest；日出：May 12, 2017 at 05:30AM，日落：Sunset: May 12, 2017 at 07:08PM；湿度：92%May 13, 2017 at 06:00AM ：最高温度 33 ℃，最低温度20 ℃；风速： 4 ，风向：South；日出：May 13, 2017 at 05:30AM，日落：Sunset: May 13, 2017 at 07:09PM；湿度：90%May 14, 2017 at 06:00AM ：最高温度 32 ℃，最低温度20 ℃；风速： 2 ，风向：Northeast；日出：May 14, 2017 at 05:29AM，日落：Sunset: May 14, 2017 at 07:09PM；湿度：93%May 15, 2017 at 06:00AM ：最高温度 27 ℃，最低温度17 ℃；风速： 4 ，风向：Northwest；日出：May 15, 2017 at 05:28AM，日落：Sunset: May 15, 2017 at 07:10PM；湿度：92%May 16, 2017 at 06:00AM ：最高温度 27 ℃，最低温度17 ℃；风速： 4 ，风向：Northwest；日出：May 16, 2017 at 05:28AM，日落：Sunset: May 16, 2017 at 07:11PM；湿度：86%May 17, 2017 at 06:00AM ：最高温度 29 ℃，最低温度18 ℃；风速： 2 ，风向：South；日出：May 17, 2017 at 05:27AM，日落：Sunset: May 17, 2017 at 07:11PM；湿度：93%May 18, 2017 at 06:00AM ：最高温度 32 ℃，最低温度21 ℃；风速： 0 ，风向：Southeast；日出：May 18, 2017 at 05:27AM，日落：Sunset: May 18, 2017 at 07:12PM；湿度：92%May 19, 2017 at 06:00AM ：最高温度 29 ℃，最低温度21 ℃；风速： 2 ，风向：Southeast；日出：May 19, 2017 at 05:26AM，日落：Sunset: May 19, 2017 at 07:13PM；湿度：77%May 20, 2017 at 06:00AM ：最高温度 31 ℃，最低温度22 ℃；风速： 0 ，风向：East；日出：May 20, 2017 at 05:25AM，日落：Sunset: May 20, 2017 at 07:13PM；湿度：94%May 21, 2017 at 06:00AM ：最高温度 32 ℃，最低温度23 ℃；风速： 0 ，风向：East；日出：May 21, 2017 at 05:25AM，日落：Sunset: May 21, 2017 at 07:14PM；湿度：93%May 22, 2017 at 06:00AM ：最高温度 27 ℃，最低温度21 ℃；风速： 4 ，风向：Southeast；日出：May 22, 2017 at 05:25AM，日落：Sunset: May 22, 2017 at 07:15PM；湿度：95%May 23, 2017 at 06:00AM ：最高温度 22 ℃，最低温度18 ℃；风速： 13 ，风向：North；日出：May 23, 2017 at 05:24AM，日落：Sunset: May 23, 2017 at 07:15PM；湿度：96%May 24, 2017 at 06:00AM ：最高温度 27 ℃，最低温度16 ℃；风速： 4 ，风向：Northwest；日出：May 24, 2017 at 05:24AM，日落：Sunset: May 24, 2017 at 07:16PM；湿度：85%May 25, 2017 at 06:00AM ：最高温度 30 ℃，最低温度18 ℃；风速： 2 ，风向：West；日出：May 25, 2017 at 05:23AM，日落：Sunset: May 25, 2017 at 07:16PM；湿度：85%May 26, 2017 at 06:01AM ：最高温度 31 ℃，最低温度20 ℃；风速： 0 ，风向：Southwest；日出：May 26, 2017 at 05:23AM，日落：Sunset: May 26, 2017 at 07:17PM；湿度：90%May 27, 2017 at 06:00AM ：最高温度 32 ℃，最低温度22 ℃；风速： 2 ，风向：Southwest；日出：May 27, 2017 at 05:22AM，日落：Sunset: May 27, 2017 at 07:18PM；湿度：86%May 28, 2017 at 06:00AM ：最高温度 33 ℃，最低温度22 ℃；风速： 0 ，风向：Southeast；日出：May 28, 2017 at 05:22AM，日落：Sunset: May 28, 2017 at 07:18PM；湿度：89%May 29, 2017 at 06:00AM ：最高温度 34 ℃，最低温度23 ℃；风速： 4 ，风向：Southeast；日出：May 29, 2017 at 05:22AM，日落：Sunset: May 29, 2017 at 07:19PM；湿度：80%May 30, 2017 at 06:00AM ：最高温度 32 ℃，最低温度24 ℃；风速： 0 ，风向：Southeast；日出：May 30, 2017 at 05:21AM，日落：Sunset: May 30, 2017 at 07:19PM；湿度：82%May 31, 2017 at 06:00AM ：最高温度 33 ℃，最低温度24 ℃；风速： 0 ，风向：Southwest；日出：May 31, 2017 at 05:21AM，日落：Sunset: May 31, 2017 at 07:20PM；湿度：94%June 01, 2017 at 06:00AM ：最高温度 29 ℃，最低温度22 ℃；风速： 4 ，风向：Southwest；日出：June 01, 2017 at 05:21AM，日落：Sunset: June 01, 2017 at 07:20PM；湿度：85%June 02, 2017 at 06:00AM ：最高温度 33 ℃，最低温度24 ℃；风速： 0 ，风向：Northwest；日出：June 02, 2017 at 05:21AM，日落：Sunset: June 02, 2017 at 07:21PM；湿度：96%June 03, 2017 at 06:00AM ：最高温度 33 ℃，最低温度24 ℃；风速： 0 ，风向：East；日出：June 03, 2017 at 05:20AM，日落：Sunset: June 03, 2017 at 07:21PM；湿度：90%June 04, 2017 at 06:00AM ：最高温度 31 ℃，最低温度21 ℃；风速： 4 ，风向：Northeast；日出：June 04, 2017 at 05:20AM，日落：Sunset: June 04, 2017 at 07:22PM；湿度：79%June 05, 2017 at 06:01AM ：最高温度 24 ℃，最低温度17 ℃；风速： 9 ，风向：Northeast；日出：June 05, 2017 at 05:20AM，日落：Sunset: June 05, 2017 at 07:22PM；湿度：87%June 06, 2017 at 06:00AM ：最高温度 27 ℃，最低温度19 ℃；风速： 4 ，风向：Northwest；日出：June 06, 2017 at 05:20AM，日落：Sunset: June 06, 2017 at 07:23PM；湿度：89%June 07, 2017 at 06:00AM ：最高温度 31 ℃，最低温度22 ℃；风速： 0 ，风向：Southwest；日出：June 07, 2017 at 05:20AM，日落：Sunset: June 07, 2017 at 07:23PM；湿度：95%June 08, 2017 at 06:00AM ：最高温度 32 ℃，最低温度24 ℃；风速： 7 ，风向：Southeast；日出：June 08, 2017 at 05:20AM，日落：Sunset: June 08, 2017 at 07:24PM；湿度：91%June 09, 2017 at 06:00AM ：最高温度 29 ℃，最低温度26 ℃；风速： 2 ，风向：Southeast；日出：June 09, 2017 at 05:20AM，日落：Sunset: June 09, 2017 at 07:24PM；湿度：93%June 10, 2017 at 06:00AM ：最高温度 29 ℃，最低温度22 ℃；风速： 7 ，风向：South；日出：June 10, 2017 at 05:20AM，日落：Sunset: June 10, 2017 at 07:25PM；湿度：91%June 11, 2017 at 06:00AM ：最高温度 29 ℃，最低温度23 ℃；风速： 0 ，风向：North；日出：June 11, 2017 at 05:20AM，日落：Sunset: June 11, 2017 at 07:25PM；湿度：94%June 12, 2017 at 06:00AM ：最高温度 27 ℃，最低温度22 ℃；风速： 0 ，风向：Northeast；日出：June 12, 2017 at 05:20AM，日落：Sunset: June 12, 2017 at 07:26PM；湿度：97%June 13, 2017 at 06:00AM ：最高温度 25 ℃，最低温度21 ℃；风速： 0 ，风向：Northeast；日出：June 13, 2017 at 05:20AM，日落：Sunset: June 13, 2017 at 07:26PM；湿度：96%June 14, 2017 at 06:00AM ：最高温度 27 ℃，最低温度21 ℃；风速： 0 ，风向：Northeast；日出：June 14, 2017 at 05:20AM，日落：Sunset: June 14, 2017 at 07:26PM；湿度：94%June 15, 2017 at 06:00AM ：最高温度 24 ℃，最低温度19 ℃；风速： 2 ，风向：North；日出：June 15, 2017 at 05:20AM，日落：Sunset: June 15, 2017 at 07:27PM；湿度：94%June 17, 2017 at 06:00AM ：最高温度 29 ℃，最低温度23 ℃；风速： 0 ，风向：Northwest；日出：June 17, 2017 at 05:20AM，日落：Sunset: June 17, 2017 at 07:27PM；湿度：95%June 18, 2017 at 06:00AM ：最高温度 29 ℃，最低温度22 ℃；风速： 2 ，风向：Southeast；日出：June 18, 2017 at 05:20AM，日落：Sunset: June 18, 2017 at 07:28PM；湿度：84%June 19, 2017 at 06:00AM ：最高温度 29 ℃，最低温度23 ℃；风速： 4 ，风向：Southeast；日出：June 19, 2017 at 05:20AM，日落：Sunset: June 19, 2017 at 07:28PM；湿度：92%June 20, 2017 at 06:00AM ：最高温度 31 ℃，最低温度24 ℃；风速： 2 ，风向：South；日出：June 20, 2017 at 05:20AM，日落：Sunset: June 20, 2017 at 07:28PM；湿度：96%June 21, 2017 at 06:00AM ：最高温度 31 ℃，最低温度23 ℃；风速： 4 ，风向：Southeast；日出：June 21, 2017 at 05:21AM，日落：Sunset: June 21, 2017 at 07:28PM；湿度：92%June 22, 2017 at 06:00AM ：最高温度 32 ℃，最低温度25 ℃；风速： 0 ，风向：Southeast；日出：June 22, 2017 at 05:21AM，日落：Sunset: June 22, 2017 at 07:28PM；湿度：96%June 23, 2017 at 06:00AM ：最高温度 27 ℃，最低温度23 ℃；风速： 0 ，风向：Southeast；日出：June 23, 2017 at 05:21AM，日落：Sunset: June 23, 2017 at 07:29PM；湿度：97%June 24, 2017 at 06:00AM ：最高温度 30 ℃，最低温度24 ℃；风速： 2 ，风向：Northwest；日出：June 24, 2017 at 05:21AM，日落：Sunset: June 24, 2017 at 07:29PM；湿度：97%June 25, 2017 at 06:00AM ：最高温度 30 ℃，最低温度23 ℃；风速： 2 ，风向：Northwest；日出：June 25, 2017 at 05:22AM，日落：Sunset: June 25, 2017 at 07:29PM；湿度：95%June 26, 2017 at 06:00AM ：最高温度 29 ℃，最低温度22 ℃；风速： 0 ，风向：Northwest；日出：June 26, 2017 at 05:22AM，日落：Sunset: June 26, 2017 at 07:29PM；湿度：97%June 27, 2017 at 06:00AM ：最高温度 31 ℃，最低温度23 ℃；风速： 7 ，风向：Southwest；日出：June 27, 2017 at 05:22AM，日落：Sunset: June 27, 2017 at 07:29PM；湿度：90%June 28, 2017 at 06:00AM ：最高温度 29 ℃，最低温度22 ℃；风速： 2 ，风向：Southwest；日出：June 28, 2017 at 05:23AM，日落：Sunset: June 28, 2017 at 07:29PM；湿度：89%June 29, 2017 at 06:00AM ：最高温度 30 ℃，最低温度23 ℃；风速： 0 ，风向：Southeast；日出：June 29, 2017 at 05:23AM，日落：Sunset: June 29, 2017 at 07:29PM；湿度：95%June 30, 2017 at 06:00AM ：最高温度 26 ℃，最低温度23 ℃；风速： 7 ，风向：Southeast；日出：June 30, 2017 at 05:23AM，日落：Sunset: June 30, 2017 at 07:29PM；湿度：96%July 01, 2017 at 06:00AM ：最高温度 26 ℃，最低温度23 ℃；风速： 0 ，风向：South；日出：July 01, 2017 at 05:24AM，日落：Sunset: July 01, 2017 at 07:29PM；湿度：98%July 02, 2017 at 06:00AM ：最高温度 31 ℃，最低温度24 ℃；风速： 0 ，风向：Southwest；日出：July 02, 2017 at 05:24AM，日落：Sunset: July 02, 2017 at 07:29PM；湿度：97%July 03, 2017 at 06:00AM ：最高温度 32 ℃，最低温度25 ℃；风速： 0 ，风向：South；日出：July 03, 2017 at 05:25AM，日落：Sunset: July 03, 2017 at 07:29PM；湿度：96%July 04, 2017 at 06:00AM ：最高温度 32 ℃，最低温度26 ℃；风速： 2 ，风向：Southeast；日出：July 04, 2017 at 05:25AM，日落：Sunset: July 04, 2017 at 07:29PM；湿度：95%July 05, 2017 at 06:00AM ：最高温度 31 ℃，最低温度27 ℃；风速： 7 ，风向：Southeast；日出：July 05, 2017 at 05:25AM，日落：Sunset: July 05, 2017 at 07:29PM；湿度：91%July 06, 2017 at 06:00AM ：最高温度 33 ℃，最低温度27 ℃；风速： 4 ，风向：Southeast；日出：July 06, 2017 at 05:26AM，日落：Sunset: July 06, 2017 at 07:29PM；湿度：86%July 07, 2017 at 06:00AM ：最高温度 31 ℃，最低温度27 ℃；风速： 7 ，风向：South；日出：July 07, 2017 at 05:26AM，日落：Sunset: July 07, 2017 at 07:29PM；湿度：79%July 08, 2017 at 06:00AM ：最高温度 30 ℃，最低温度26 ℃；风速： 4 ，风向：Southeast；日出：July 08, 2017 at 05:27AM，日落：Sunset: July 08, 2017 at 07:29PM；湿度：87%July 09, 2017 at 06:00AM ：最高温度 28 ℃，最低温度24 ℃；风速： 4 ，风向：South；日出：July 09, 2017 at 05:27AM，日落：Sunset: July 09, 2017 at 07:28PM；湿度：89%July 10, 2017 at 06:00AM ：最高温度 32 ℃，最低温度24 ℃；风速： 0 ，风向：Southwest；日出：July 10, 2017 at 05:28AM，日落：Sunset: July 10, 2017 at 07:28PM；湿度：98%July 11, 2017 at 06:00AM ：最高温度 33 ℃，最低温度26 ℃；风速： 0 ，风向：Southeast；日出：July 11, 2017 at 05:28AM，日落：Sunset: July 11, 2017 at 07:28PM；湿度：96%July 12, 2017 at 06:00AM ：最高温度 33 ℃，最低温度27 ℃；风速： 4 ，风向：South；日出：July 12, 2017 at 05:29AM，日落：Sunset: July 12, 2017 at 07:28PM；湿度：84%July 13, 2017 at 06:00AM ：最高温度 33 ℃，最低温度27 ℃；风速： 4 ，风向：South；日出：July 13, 2017 at 05:29AM，日落：Sunset: July 13, 2017 at 07:27PM；湿度：80%July 14, 2017 at 06:00AM ：最高温度 33 ℃，最低温度27 ℃；风速： 4 ，风向：South；日出：July 14, 2017 at 05:30AM，日落：Sunset: July 14, 2017 at 07:27PM；湿度：80%July 15, 2017 at 06:00AM ：最高温度 33 ℃，最低温度27 ℃；风速： 4 ，风向：South；日出：July 15, 2017 at 05:30AM，日落：Sunset: July 15, 2017 at 07:27PM；湿度：79%July 16, 2017 at 06:00AM ：最高温度 35 ℃，最低温度27 ℃；风速： 4 ，风向：South；日出：July 16, 2017 at 05:31AM，日落：Sunset: July 16, 2017 at 07:26PM；湿度：85%July 17, 2017 at 06:00AM ：最高温度 36 ℃，最低温度28 ℃；风速： 0 ，风向：Southeast；日出：July 17, 2017 at 05:32AM，日落：Sunset: July 17, 2017 at 07:26PM；湿度：89%July 18, 2017 at 06:00AM ：最高温度 34 ℃，最低温度27 ℃；风速： 0 ，风向：Southeast；日出：July 18, 2017 at 05:32AM，日落：Sunset: July 18, 2017 at 07:26PM；湿度：83%July 19, 2017 at 06:00AM ：最高温度 34 ℃，最低温度27 ℃；风速： 4 ，风向：Southwest；日出：July 19, 2017 at 05:33AM，日落：Sunset: July 19, 2017 at 07:25PM；湿度：80%July 20, 2017 at 06:00AM ：最高温度 35 ℃，最低温度28 ℃；风速： 4 ，风向：South；日出：July 20, 2017 at 05:33AM，日落：Sunset: July 20, 2017 at 07:25PM；湿度：77%July 21, 2017 at 06:00AM ：最高温度 37 ℃，最低温度28 ℃；风速： 11 ，风向：Southwest；日出：July 21, 2017 at 05:34AM，日落：Sunset: July 21, 2017 at 07:24PM；湿度：73%July 22, 2017 at 06:00AM ：最高温度 39 ℃，最低温度28 ℃；风速： 2 ，风向：South；日出：July 22, 2017 at 05:35AM，日落：Sunset: July 22, 2017 at 07:24PM；湿度：75%July 23, 2017 at 06:00AM ：最高温度 40 ℃，最低温度29 ℃；风速： 0 ，风向：South；日出：July 23, 2017 at 05:35AM，日落：Sunset: July 23, 2017 at 07:23PM；湿度：83%July 24, 2017 at 06:00AM ：最高温度 40 ℃，最低温度29 ℃；风速： 0 ，风向：Southwest；日出：July 24, 2017 at 05:36AM，日落：Sunset: July 24, 2017 at 07:22PM；湿度：84%July 25, 2017 at 06:00AM ：最高温度 39 ℃，最低温度30 ℃；风速： 0 ，风向：Northwest；日出：July 25, 2017 at 05:36AM，日落：Sunset: July 25, 2017 at 07:22PM；湿度：82%July 26, 2017 at 06:00AM ：最高温度 40 ℃，最低温度30 ℃；风速： 0 ，风向：East；日出：July 26, 2017 at 05:37AM，日落：Sunset: July 26, 2017 at 07:21PM；湿度：85%July 27, 2017 at 06:00AM ：最高温度 41 ℃，最低温度30 ℃；风速： 2 ，风向：Southwest；日出：July 27, 2017 at 05:38AM，日落：Sunset: July 27, 2017 at 07:21PM；湿度：79%July 28, 2017 at 06:00AM ：最高温度 40 ℃，最低温度28 ℃；风速： 2 ，风向：North；日出：July 28, 2017 at 05:38AM，日落：Sunset: July 28, 2017 at 07:20PM；湿度：86%July 29, 2017 at 06:00AM ：最高温度 37 ℃，最低温度27 ℃；风速： 9 ，风向：Northeast；日出：July 29, 2017 at 05:39AM，日落：Sunset: July 29, 2017 at 07:19PM；湿度：90%July 30, 2017 at 06:00AM ：最高温度 36 ℃，最低温度27 ℃；风速： 4 ，风向：North；日出：July 30, 2017 at 05:39AM，日落：Sunset: July 30, 2017 at 07:19PM；湿度：90%July 31, 2017 at 06:00AM ：最高温度 34 ℃，最低温度27 ℃；风速： 4 ，风向：Northwest；日出：July 31, 2017 at 05:40AM，日落：Sunset: July 31, 2017 at 07:18PM；湿度：90%August 01, 2017 at 06:01AM ：最高温度 32 ℃，最低温度26 ℃；风速： 4 ，风向：North；日出：August 01, 2017 at 05:41AM，日落：Sunset: August 01, 2017 at 07:17PM；湿度：93%August 02, 2017 at 06:00AM ：最高温度 32 ℃，最低温度26 ℃；风速： 2 ，风向：Northwest；日出：August 02, 2017 at 05:41AM，日落：Sunset: August 02, 2017 at 07:16PM；湿度：95%August 03, 2017 at 06:00AM ：最高温度 36 ℃，最低温度28 ℃；风速： 0 ，风向：Southwest；日出：August 03, 2017 at 05:42AM，日落：Sunset: August 03, 2017 at 07:16PM；湿度：94%August 04, 2017 at 06:00AM ：最高温度 36 ℃，最低温度28 ℃；风速： 7 ，风向：Northeast；日出：August 04, 2017 at 05:42AM，日落：Sunset: August 04, 2017 at 07:15PM；湿度：91%August 05, 2017 at 06:00AM ：最高温度 34 ℃，最低温度28 ℃；风速： 0 ，风向：Southeast；日出：August 05, 2017 at 05:43AM，日落：Sunset: August 05, 2017 at 07:14PM；湿度：92%August 06, 2017 at 06:00AM ：最高温度 37 ℃，最低温度29 ℃；风速： 0 ，风向：South；日出：August 06, 2017 at 05:44AM，日落：Sunset: August 06, 2017 at 07:13PM；湿度：92%August 07, 2017 at 06:00AM ：最高温度 38 ℃，最低温度29 ℃；风速： 2 ，风向：South；日出：August 07, 2017 at 05:44AM，日落：Sunset: August 07, 2017 at 07:12PM；湿度：82%August 08, 2017 at 06:00AM ：最高温度 32 ℃，最低温度25 ℃；风速： 2 ，风向：Northeast；日出：August 08, 2017 at 05:45AM，日落：Sunset: August 08, 2017 at 07:11PM；湿度：85%August 09, 2017 at 06:00AM ：最高温度 32 ℃，最低温度24 ℃；风速： 0 ，风向：West；日出：August 09, 2017 at 05:46AM，日落：Sunset: August 09, 2017 at 07:10PM；湿度：93%August 10, 2017 at 06:00AM ：最高温度 36 ℃，最低温度27 ℃；风速： 4 ，风向：South；日出：August 10, 2017 at 05:46AM，日落：Sunset: August 10, 2017 at 07:10PM；湿度：93%August 11, 2017 at 06:00AM ：最高温度 32 ℃，最低温度25 ℃；风速： 2 ，风向：Southeast；日出：August 11, 2017 at 05:47AM，日落：Sunset: August 11, 2017 at 07:09PM；湿度：90%August 12, 2017 at 06:00AM ：最高温度 27 ℃，最低温度24 ℃；风速： 4 ，风向：East；日出：August 12, 2017 at 05:47AM，日落：Sunset: August 12, 2017 at 07:08PM；湿度：93%August 13, 2017 at 06:00AM ：最高温度 27 ℃，最低温度24 ℃；风速： 2 ，风向：Southwest；日出：August 13, 2017 at 05:48AM，日落：Sunset: August 13, 2017 at 07:07PM；湿度：98%August 14, 2017 at 06:00AM ：最高温度 29 ℃，最低温度24 ℃；风速： 0 ，风向：Northwest；日出：August 14, 2017 at 05:48AM，日落：Sunset: August 14, 2017 at 07:06PM；湿度：97%August 15, 2017 at 06:00AM ：最高温度 32 ℃，最低温度24 ℃；风速： 0 ，风向：Northwest；日出：August 15, 2017 at 05:49AM，日落：Sunset: August 15, 2017 at 07:05PM；湿度：97%August 16, 2017 at 06:00AM ：最高温度 32 ℃，最低温度24 ℃；风速： 0 ，风向：West；日出：August 16, 2017 at 05:50AM，日落：Sunset: August 16, 2017 at 07:04PM；湿度：95%August 17, 2017 at 06:00AM ：最高温度 32 ℃，最低温度26 ℃；风速： 7 ，风向：Southeast；日出：August 17, 2017 at 05:50AM，日落：Sunset: August 17, 2017 at 07:03PM；湿度：91%August 18, 2017 at 06:00AM ：最高温度 34 ℃，最低温度27 ℃；风速： 4 ，风向：Southeast；日出：August 18, 2017 at 05:51AM，日落：Sunset: August 18, 2017 at 07:02PM；湿度：89%August 19, 2017 at 06:00AM ：最高温度 34 ℃，最低温度26 ℃；风速： 4 ，风向：South；日出：August 19, 2017 at 05:52AM，日落：Sunset: August 19, 2017 at 07:00PM；湿度：80%August 20, 2017 at 06:00AM ：最高温度 33 ℃，最低温度26 ℃；风速： 4 ，风向：Northeast；日出：August 20, 2017 at 05:52AM，日落：Sunset: August 20, 2017 at 06:59PM；湿度：91%August 21, 2017 at 06:00AM ：最高温度 33 ℃，最低温度27 ℃；风速： 2 ，风向：Northeast；日出：August 21, 2017 at 05:53AM，日落：Sunset: August 21, 2017 at 06:58PM；湿度：94%August 22, 2017 at 06:00AM ：最高温度 36 ℃，最低温度27 ℃；风速： 2 ，风向：North；日出：August 22, 2017 at 05:53AM，日落：Sunset: August 22, 2017 at 06:57PM；湿度：92%August 23, 2017 at 06:01AM ：最高温度 36 ℃，最低温度28 ℃；风速： 9 ，风向：East；日出：August 23, 2017 at 05:54AM，日落：Sunset: August 23, 2017 at 06:56PM；湿度：85%August 24, 2017 at 06:00AM ：最高温度 34 ℃，最低温度27 ℃；风速： 0 ，风向：East；日出：August 24, 2017 at 05:54AM，日落：Sunset: August 24, 2017 at 06:55PM；湿度：90%August 25, 2017 at 06:00AM ：最高温度 33 ℃，最低温度26 ℃；风速： 0 ，风向：North；日出：August 25, 2017 at 05:55AM，日落：Sunset: August 25, 2017 at 06:54PM；湿度：95%August 26, 2017 at 06:00AM ：最高温度 32 ℃，最低温度26 ℃；风速： 4 ，风向：Northeast；日出：August 26, 2017 at 05:55AM，日落：Sunset: August 26, 2017 at 06:53PM；湿度：87%August 27, 2017 at 06:00AM ：最高温度 35 ℃，最低温度27 ℃；风速： 2 ，风向：Northeast；日出：August 27, 2017 at 05:56AM，日落：Sunset: August 27, 2017 at 06:51PM；湿度：92%August 28, 2017 at 06:00AM ：最高温度 36 ℃，最低温度26 ℃；风速： 2 ，风向：Southeast；日出：August 28, 2017 at 05:57AM，日落：Sunset: August 28, 2017 at 06:50PM；湿度：90%August 29, 2017 at 06:00AM ：最高温度 34 ℃，最低温度23 ℃；风速： 9 ，风向：Northeast；日出：August 29, 2017 at 05:57AM，日落：Sunset: August 29, 2017 at 06:49PM；湿度：89%August 30, 2017 at 06:00AM ：最高温度 27 ℃，最低温度20 ℃；风速： 9 ，风向：Northwest；日出：August 30, 2017 at 05:58AM，日落：Sunset: August 30, 2017 at 06:48PM；湿度：90%August 31, 2017 at 06:00AM ：最高温度 27 ℃，最低温度21 ℃；风速： 4 ，风向：Northwest；日出：August 31, 2017 at 05:58AM，日落：Sunset: August 31, 2017 at 06:47PM；湿度：87%September 01, 2017 at 06:00AM ：最高温度 27 ℃，最低温度22 ℃；风速： 4 ，风向：Northwest；日出：September 01, 2017 at 05:59AM，日落：Sunset: September 01, 2017 at 06:46PM；湿度：88%September 02, 2017 at 06:00AM ：最高温度 25 ℃，最低温度21 ℃；风速： 2 ，风向：Northeast；日出：September 02, 2017 at 05:59AM，日落：Sunset: September 02, 2017 at 06:44PM；湿度：94%September 03, 2017 at 06:00AM ：最高温度 24 ℃，最低温度20 ℃；风速： 4 ，风向：Northeast；日出：September 03, 2017 at 06:00AM，日落：Sunset: September 03, 2017 at 06:43PM；湿度：95%September 04, 2017 at 06:00AM ：最高温度 29 ℃，最低温度22 ℃；风速： 2 ，风向：Northwest；日出：September 04, 2017 at 06:01AM，日落：Sunset: September 04, 2017 at 06:42PM；湿度：95%September 05, 2017 at 06:00AM ：最高温度 31 ℃，最低温度22 ℃；风速： 2 ，风向：North；日出：September 05, 2017 at 06:01AM，日落：Sunset: September 05, 2017 at 06:41PM；湿度：96%September 06, 2017 at 06:00AM ：最高温度 27 ℃，最低温度21 ℃；风速： 0 ，风向：Northwest；日出：September 06, 2017 at 06:02AM，日落：Sunset: September 06, 2017 at 06:39PM；湿度：92%September 07, 2017 at 06:00AM ：最高温度 31 ℃，最低温度22 ℃；风速： 0 ，风向：Northwest；日出：September 07, 2017 at 06:02AM，日落：Sunset: September 07, 2017 at 06:38PM；湿度：94%September 08, 2017 at 06:00AM ：最高温度 32 ℃，最低温度24 ℃；风速： 0 ，风向：East；日出：September 08, 2017 at 06:03AM，日落：Sunset: September 08, 2017 at 06:37PM；湿度：96%'
            pattern = u'(\w*\s*\d+,\s*\d{4}\s*at\s*\d{2}:\d{2}[AP]M)\s+'

            slice = re.split(pattern, soup.get_text())
            print len(slice)
            split_item = []
            for i in range(1, len(slice), 2):
                split_item.append(slice[i] + " " + slice[i + 1])

            # print len(split_item)
            # print split_item[-1]
            # print split_item
            # for t in split_item:
            #     print t

            itempattern = re.compile(
                u'(?P<date>\w*\s*\d+,\s*\d{4}\s*at\s*\d{2}:\d{2}[AP]M)\s+：最高温度\s*(?P<gaowen>-?\d*)\s*℃，最低温度(?P<diwen>-?\d*)\s*℃；风速：\s*(?P<fengsu>\d*) \s*，风向：(?P<fengxiang>\w*)；(?:污染：*\s*Not Available；)*日出：\s*(?P<sunon>\w*\s*\d+,\s*\d{4}\s*at\s*\d{2}:\d{2}[AP]M)，日落：(?:Sunset:)*\s*(?P<sunoff>\w*\s*\d+,\s*\d{4}\s*at\s*\d{2}:\d{2}[AP]M)；湿度：(?P<shidu>\w*)%')
            # print re.findall(itempattern, itemtext)
            # timestr = 'August 12, 2017 at 06:00AM'
            # itemtime = time.strptime(timestr, '%B %d, %Y at %I:%M%p')
            # print itemtime

            data_list = []
            for ii in split_item:
                for jj in re.findall(itempattern, ii):
                    stritem = [pd.Timestamp(jj[0]),
                               int(jj[1]), int(jj[2]), int(jj[3]), jj[4],
                               pd.Timestamp(jj[5]),
                               pd.Timestamp(jj[6]),
                               int(jj[7])]
                # print stritem
                data_list.append(stritem)

            # print type(data_list[0][0]), type(data_list[0][5]), type(data_list[0][6])
            #
            # print len(data_list)
            # print data_list[0]
            # # print data_list
            # print type(data_list)

            df = pd.DataFrame(data_list,
                              columns=['date', 'gaowen', 'diwen', 'fengsu', 'fengxiang', 'sunon', 'sunoff', 'shidu'])

            # print df.head()
            # print df.tail()
            # print df.index
            # # print df.columns
            # # print df.values
            # print df.describe()

            # print df
            # print type(df)

            # x = list(df['date'])
            # y = list(df['gaowen'])
            # plt.plot(x,y)
            # plt.show()

            # tss = pd.Series(list(df['gaowen']),index=pd.date_range('9/19/2016', periods=354))
            # tss = pd.Series(list(df[0:100]['gaowen']),index=df[0:100]['date'])
            # tss.cumsum()
            # tss.plot()

            tss = pd.Series(list(df['gaowen']), index=df['date'])
            tss.cumsum()
            tss.plot()

            # tssr = tss.resample('M').mean()
            tssr = tss.asfreq('10D', method='pad')
            tssr.cumsum()
            tssr.plot()

            # plt.show()

            plt.savefig('sample.png')

    print


print

ziduandict = {1: '日期',}

printnotefromnotebook('31eee750-e240-438b-a1f5-03ce34c904b4',100)

# notecollectioncounts = note_store.findNoteCounts(notefilter,False)


# print
# print "Creating a new note in the default notebook"
# print

# To create a new note, simply create a new Note object and fill in
# attributes such as the note's title.
note = Types.Note()
note.title = "天气气温折线图"
note.guid = '296f57a3-c660-4dd5-885a-56492deb2cee'
note.notebookGuid = '31eee750-e240-438b-a1f5-03ce34c904b4'

# To include an attachment such as an image in a note, first create a Resource
# for the attachment. At a minimum, the Resource contains the binary attachment
# data, an MD5 hash of the binary data, and the attachment MIME type.
# It can also include attributes such as filename and location.
image = open('sample.png', 'rb').read()
md5 = hashlib.md5()
md5.update(image)
hash = md5.digest()

data = Types.Data()
data.size = len(image)
data.bodyHash = hash
data.body = image

resource = Types.Resource()
resource.mime = 'image/png'
resource.data = data

# Now, add the new Resource to the note's list of resources
note.resources = [resource]

# To display the Resource as part of the note's content, include an <en-media>
# tag in the note's ENML content. The en-media tag identifies the corresponding
# Resource using the MD5 hash.
hash_hex = binascii.hexlify(hash)

# The content of an Evernote note is represented using Evernote Markup Language
# (ENML). The full ENML specification can be found in the Evernote API Overview
# at http://dev.evernote.com/documentation/cloud/chapters/ENML.php
note.content = '<?xml version="1.0" encoding="UTF-8"?>'
note.content += '<!DOCTYPE en-note SYSTEM ' \
    '"http://xml.evernote.com/pub/enml2.dtd">'
note.content += '<en-note>每天最高气温<br/>'
note.content += '<en-media type="image/png" hash="' + hash_hex + '"/>'
note.content += '</en-note>'

# Finally, send the new note to Evernote using the createNote method
# The new Note object that is returned will contain server-generated
# attributes such as the new note's unique GUID.
updated_note = note_store.updateNote(note)

print "Successfully created a new note with GUID: ", updated_note.guid
