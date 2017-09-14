#
# encoding:utf-8
#
# 用evernote作为工作平台，通过Python链接整理各种工作数据，呈现给各个相关岗位。.
#
# To run (Unix):
#   export PYTHONPATH=../../lib; python everwork.py
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
from pylab import *
from matplotlib.ticker import MultipleLocator, FuncFormatter
from noteweather import weatherstat

mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False

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


def min_formatter(x, pos):
    return r"%02d:%02d" %(int(x/60), int(x%60))


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
        if note.title.find('武汉每日天气') >= 0:
            print note.guid, note.title

    print

# printnotefromnotebook('31eee750-e240-438b-a1f5-03ce34c904b4',100)

weatherstat(note_store, '277dff5e-7042-47c0-9d7b-aae270f903b8', '296f57a3-c660-4dd5-885a-56492deb2cee')
