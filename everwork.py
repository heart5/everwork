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
from noteweather import weatherstat #调用同目录下其他文件（py）中的函数
# from everfunc import *

# plot中显示中文
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
    print ("Please fill in your developer token\nTo get a developer token, visit " \
        "https://sandbox.evernote.com/api/DeveloperToken.action")
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
currentuser = userStore.getUser()

# printuserattributeundertoken(currentuser)

print (int(time.time()), '\t', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))

version_ok = userStore.checkVersion(
    "Evernote EDAMTest (Python)",
    UserStoreConstants.EDAM_VERSION_MAJOR,
    UserStoreConstants.EDAM_VERSION_MINOR
)
print ("Is my Evernote API version up to date? ", str(version_ok))

if not version_ok:
    exit(1)

note_store = client.get_note_store()

# 列出账户中的全部笔记本
notebooks = note_store.listNotebooks()

# printnotebookattributeundertoken(notebooks[1])

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
            print (note.guid, note.title)

    print

printnotefromnotebook('31eee750-e240-438b-a1f5-03ce34c904b4',100)

weatherstat(note_store, '277dff5e-7042-47c0-9d7b-aae270f903b8', '296f57a3-c660-4dd5-885a-56492deb2cee')
