#!python2
# encoding:utf-8
# 工作需要，和evernote交互，并生成动态笔记

#导入必要的库
import evernote
import requests

from evernote.api.client import EvernoteClient

devToken = 'S=s37:U=3b449f:E=1659f8b7c0f:C=15e47da4ef8:P=1cd:A=en-devtoken:V=2:H=e445e5fcbceff83703151d71df584197'
client = EvernoteClient(token=devToken)

#获取类
userStore = client.get_user_store()
user = userStore.getUser()
print('登录为'+str(user.username))
if user.premiumInfo.premium: print('我们是朋友啊！')
