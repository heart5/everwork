# encoding:utf-8
"""
用evernote作为工作平台，通过Python链接整理各种工作数据，呈现给各个相关岗位。.
"""

from imp4nb import *
import evernote.edam.userstore.constants as UserStoreConstants
import evernote.edam.type.ttypes as Types
from evernote.api.client import EvernoteClient
from noteweather import *  # 调用同目录下其他文件（py）中的函数
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

# findnotefromnotebook(note_store, token, 'c068e01f-1a7a-4e65-b8e4-ed93eed6bd0b', '鲁山')  # 从笔记本中查找标题中包含指定字符串的笔记


# todo 一体化目录构建

nbfbdf = readinisection2df(cfpdata, 'guidfenbunb', '销售业绩图表')
for aa in nbfbdf.index:
    cpath = 'img\\'+aa
    if not os.path.exists(cpath):
        os.mkdir(cpath)
        log.debug('目录《' + cpath + '》被创建')

cnx = lite.connect('data\\quandan.db')
dataokay(cnx)

# pickstat(token, note_store, cnx, '1c0830d9-e42f-4ce7-bf36-ead868a55eca', '订单配货统计图', cum=True)

# pinpaifenxi(token, note_store, cnx, daysbefore=360, brandnum=5)

# desclitedb(cnx)
# swissknife(cnx)
cnx.close()

# isnoteupdate(token, note_store, '1c0830d9-e42f-4ce7-bf36-ead868a55eca')

weatherstattimer(token, note_store, 60 * 60 * 3 + 60)

jinchustattimer(token, note_store, 60 * 60)

writeini()
log.debug('程序结束！')
# print(vars())
