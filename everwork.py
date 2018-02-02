# encoding:utf-8
"""
用evernote作为工作平台，通过Python链接整理各种工作数据，呈现给各个相关岗位。.
"""

from imp4nb import *
import evernote.edam.userstore.constants as UserStoreConstants
import evernote.edam.type.ttypes as Types
from evernote.api.client import EvernoteClient
from noteweather import weatherstat #调用同目录下其他文件（py）中的函数
from notewarehouse import *
from notedispatch import *
from notesaledetails import *
from notejinchujilu import *

log.debug('程序启动……')

token = cfp.get('evernote','token')
log.debug('配置文件读取成功')

note_store = get_notestore(token)

# #列出账户中的全部笔记本
# notebooks = note_store.listNotebooks()
# # p_notebookattributeundertoken(notebooks[-1])
#
# for x in notebooks:
#     p_notebookattributeundertoken(x)

# 39ed537d-73fa-4ad8-b4fd-bc6f746fb302 真元日配送图
# 1c0830d9-e42f-4ce7-bf36-ead868a55eca 订单配货统计图
# 49eff8eb-5bce-43b9-a95a-c1ee7eab71fa 有友全渠道销售图表

# findnotefromnotebook(note_store, token, 'c068e01f-1a7a-4e65-b8e4-ed93eed6bd0b', '图表')  # 从笔记本中查找标题中包含指定字符串的笔记

# weatherstat(token, note_store, '277dff5e-7042-47c0-9d7b-aae270f903b8', '296f57a3-c660-4dd5-885a-56492deb2cee')
#
# dfjinchugoogle = jilugoogle('data\\google')
# descdb(dfjinchugoogle)
# print(dfjinchugoogle.groupby('address', as_index=False).count())
#
# noteinputlist = [
#     ['f119e38e-3876-4937-80f1-e6a6b2e5d3d0', 'wenchanglu', 'work'],
#     ['d8fa0226-88ac-4b6c-b8fd-63a9038a6abf', 'huadianxiaolu', 'home'],
#     ['1ea50564-dee7-4e82-87b5-39703671e623', 'dingziqiao', 'life'],
#     ['25967ecd-4062-4eed-bfa2-ac7fbe499154', 'lushan', 'home'],
#     ['84e9ee0b-30c3-4404-84e2-7b4614980b4b', 'hanyangban', 'work'],
#     ['6fb1e016-01ab-439d-929e-994dc980ddbe', 'hankouban', 'work'],
#     ['24aad619-2356-499e-9fa7-f685af3a81b1', 'maotanhuamushichang', 'work'],
# ]
#
# dfjinchunote = jilunote(note_store, noteinputlist)
# descdb(dfjinchunote)
# print(dfjinchunote.groupby('address', as_index=False).count())
#
# dfjinchu = dfjinchunote.append(dfjinchugoogle).sort_index()
# descdb(dfjinchu)
#
# dfjinchu['time'] = dfjinchu.index
# dfjinchu = dfjinchu.drop_duplicates()
# del dfjinchu['time']
# descdb(dfjinchu)
#
# noteoutputlist = [
#     # ['daye', '0fa3222e-1029-4417-a7a2-8ec64f9c9a12', '家（大冶）进出记录统计图表'],
#     # ['lushan', '987c1d5e-d8ad-41aa-9269-d2b840616410', '老家（鲁山）进出统计图表'],
#     # ['dingziqiao', '6eef085c-0e84-4753-bf3e-b45473a12274', '丁字桥进出统计图表'],
#     # ['yangfu\'restraunaut', '06bb4996-d0d8-4266-87d5-f3283d71f58e', '东西湖三秀路进出记录统计图表'],
#     ['huadianxiaolu', '08a01c35-d16d-4b22-b7f7-61e3993fd2cb', '家附近出入统计图表'],
#     ['qiwei', '294b584f-f34a-49f0-b4d3-08085a37bfd5', '创食人公司进出记录统计图表'],
#     ['wenchanglu', '7f4bec82-626b-4022-b3c2-0d9b3d71198d', '公司（文昌路）进出记录统计图表'],
#     ['hanyangban', 'a7e84055-f075-44ab-8205-5a42f3f05284', '汉阳办进出记录统计图表'],
#     ['hankouban', '2c5e3728-be69-4e52-a8ff-07860e8593b7', '汉口办进出记录统计图表'],
#     ['maotanhuamushichang', '2d908c33-d0a2-4d42-8d4d-5a0bc9d2ff7e', '公司进出记录统计图表'],
# ]
#
# jinchustat(token, note_store, dfjinchu, noteoutputlist)

# todo 一体化目录构建

nbfbdf = readinisection2df(cfp, 'guidfenbunb', '销售业绩图表')
for aa in nbfbdf.index:
    cpath = 'img\\'+aa
    if not os.path.exists(cpath):
        os.mkdir(cpath)
        log.debug('目录《' + cpath + '》被创建')

cnx = lite.connect('data\\quandan.db')
dataokay(cnx)

# pickstat(token, note_store, cnx, '1c0830d9-e42f-4ce7-bf36-ead868a55eca', '订单配货统计图', cum=True)

pinpaifenxi(token, note_store, cnx, daysbefore=30, brandnum=2)

# desclitedb(cnx)
# swissknife(cnx)
cnx.close()

writeini()
log.debug('程序结束！')
