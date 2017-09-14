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
from pylab import *
from matplotlib.ticker import MultipleLocator, FuncFormatter

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
        # print "\t\t\t\t", note.title, "\t", note.guid, "\t", note.contentLength, "\t", note.created, "\t", note.updated
        # print "\t\t\t\t", note.title, "\t", note.guid, "\t", note.contentLength, "\t", timestamp2str(int(note.created/1000)), "\t", timestamp2str(int(note.updated/1000))
        # print note.title.find('天气')
        if note.title.find('武汉每日天气') >= 0:
            soup = BeautifulSoup(note_store.getNoteContent(note.guid), "html.parser")
            # tags = soup.find('en-note')
            # print tags
            # print soup.get_text()

            pattern = u'(\w*\s*\d+,\s*\d{4}\s*at\s*\d{2}:\d{2}[AP]M)\s+'
            slice = re.split(pattern, soup.get_text())
            # print len(slice)
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
                               # pd.Timestamp(jj[5]).strftime("%I%M"),
                               int(pd.Timestamp(jj[5]).strftime("%H"))*60+int(pd.Timestamp(jj[5]).strftime("%M")),
                               # pd.Timestamp(jj[6]),
                               int(pd.Timestamp(jj[6]).strftime("%H"))*60+int(pd.Timestamp(jj[6]).strftime("%M")),
                               int(jj[7])]
                # print stritem
                data_list.append(stritem)

            # print type(data_list[0][0]), type(data_list[0][5]), type(data_list[0][6])
            #
            print len(data_list)
            print data_list[0]
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

            # tss = pd.Series(list(df['gaowen']), index=df['date'])
            # tss.cumsum()
            # tss.plot()

            fig, ax1 = plt.subplots()

            # plt.figure(figsize=(16, 12))
            plt.plot(df['date'], df['gaowen'], lw=1.5, label= u'日高温')
            plt.plot(df['date'], df['diwen'], lw=1.5, label= u'日低温')
            plt.plot(df['date'], df['fengsu'], lw=1.5, label= u'风速')
            # plt.plot(df['date'], df['sunon'], lw=1.5, label= u'日出')

            plt.xlabel(u'日期')
            plt.ylabel(u'温度（℃）')
            # plt.axis('tight')
            plt.legend(loc = 0)

            ax2 = ax1.twinx()
            plt.plot(df['date'], df['shidu'], 'y*', lw=1.5, label=u'湿度')
            plt.legend(loc = 7)
            plt.ylabel(u'湿度（%）')

            plt.title(u'武汉温度湿度风速图')
            plt.grid(True)

            # tssr = tss.resample('M').max()
            # tssr = tss.asfreq('10D', method='pad')
            # tssr.cumsum()
            # tssr.plot()

            # plt.show()

            plt.savefig('wenshifeng.png')
            plt.close()

            fig, ax1 = plt.subplots()
            plt.plot(df['date'], df['sunon'], lw=1.5, label= u'日出')

            ax = plt.gca()
            # 主刻度文本用pi_formatter函数计算
            ax.yaxis.set_major_formatter(FuncFormatter(min_formatter))

            plt.xlabel(u'日期')
            plt.ylabel(u'日出（时分）')
            # plt.axis('tight')
            plt.legend(loc = 2)

            ax2 = ax1.twinx()
            plt.plot(df['date'], df['sunoff'], 'y*', lw=1.5, label=u'日落')

            ax = plt.gca()
            # 主刻度文本用pi_formatter函数计算
            ax.yaxis.set_major_formatter(FuncFormatter(min_formatter))

            plt.legend(loc = 3)
            plt.ylabel(u'日落（时分）')

            plt.title(u'武汉日出日落图')
            plt.grid(True)

            plt.savefig('sunonoff.png')

            plt.close()

    print


print

printnotefromnotebook('31eee750-e240-438b-a1f5-03ce34c904b4',100)

# notecollectioncounts = note_store.findNoteCounts(notefilter,False)


# print
# print "Creating a new note in the default notebook"
# print

# To create a new note, simply create a new Note object and fill in
# attributes such as the note's title.
note = Types.Note()
note.title = "武汉天气图"
note.guid = '296f57a3-c660-4dd5-885a-56492deb2cee'
note.notebookGuid = '31eee750-e240-438b-a1f5-03ce34c904b4'

# To include an attachment such as an image in a note, first create a Resource
# for the attachment. At a minimum, the Resource contains the binary attachment
# data, an MD5 hash of the binary data, and the attachment MIME type.
# It can also include attributes such as filename and location.
image = open('wenshifeng.png', 'rb').read()
md5 = hashlib.md5()
md5.update(image)
hash = md5.digest()
# print hash

data = Types.Data()
data.size = len(image)
data.bodyHash = hash
data.body = image
# print data

resource_wenshifeng = Types.Resource()
resource_wenshifeng.mime = 'image/png'
resource_wenshifeng.data = data
# print resource_wenshifeng

# To display the Resource as part of the note's content, include an <en-media>
# tag in the note's ENML content. The en-media tag identifies the corresponding
# Resource using the MD5 hash.
# hash_hex_wenshifeng = binascii.hexlify(hash)


# print note.resources

image = open('sunonoff.png', 'rb').read()
md5 = hashlib.md5()
md5.update(image)
hash = md5.digest()
# print hash

data = Types.Data()
data.size = len(image)
data.bodyHash = hash
data.body = image
# print  data

resource_sunonoff = Types.Resource()
resource_sunonoff.mime = 'image/png'
resource_sunonoff.data = data
# print resource_sunonoff

# To display the Resource as part of the note's content, include an <en-media>
# tag in the note's ENML content. The en-media tag identifies the corresponding
# Resource using the MD5 hash.
hash_hex_sunonoff = binascii.hexlify(hash)


# Now, add the new Resource to the note's list of resources
note.resources =[resource_wenshifeng, resource_sunonoff]
# note.resources.append(resource_wenshifeng)

# print len(note.resources)
# # print note.resources
# print note.resources[0]
# print note.resources[1]


# The content of an Evernote note is represented using Evernote Markup Language
# (ENML). The full ENML specification can be found in the Evernote API Overview
# at http://dev.evernote.com/documentation/cloud/chapters/ENML.php
nBody = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
nBody += "<!DOCTYPE en-note SYSTEM \"http://xml.evernote.com/pub/enml2.dtd\">"
nBody += "<en-note>"
if note.resources:
    ### Add Resource objects to note body
    # nBody += "<br />" * 2
    for resource in note.resources:
        hexhash = binascii.hexlify(resource.data.bodyHash)
        nBody += "<en-media type=\"%s\" hash=\"%s\" /><br />" % \
                 (resource.mime, hexhash)
nBody += "</en-note>"

note.content = nBody

# print note.content
# Finally, send the new note to Evernote using the createNote method
# The new Note object that is returned will contain server-generated
# attributes such as the new note's unique GUID.
updated_note = note_store.updateNote(note)

print "Successfully updated a note with GUID: ", updated_note.guid
