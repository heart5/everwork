# encoding:utf-8
"""
用evernote作为工作平台，通过Python链接整理各种工作数据，呈现给各个相关岗位。.
"""

from imp4nb import *
from noteweather import *  # 调用同目录下其他文件（py）中的函数
from notewarehouse import *
from notedispatch import *
from notesaledetails import *
from notejinchujilu import *
from log2note import *

# log.debug('程序启动……')
# todo 一体化目录构建

# nbfbdf = readinisection2df(cfpdata, 'guidfenbunb', '销售业绩图表')
# for aa in nbfbdf.index:
#     cpath = 'img\\'+aa
#     if not os.path.exists(cpath):
#         os.mkdir(cpath)
#         log.debug('目录《' + cpath + '》被创建')

# cnx = lite.connect('data\\quandan.db')
# dataokay(cnx)

# pickstat(token, note_store, cnx, '1c0830d9-e42f-4ce7-bf36-ead868a55eca', '订单配货统计图', cum=True)

# pinpaifenxi(token, note_store, cnx, daysbefore=360, brandnum=5)

# desclitedb(cnx)
# swissknife(cnx)
# cnx.close()

# isnoteupdate(token, note_store, '1c0830d9-e42f-4ce7-bf36-ead868a55eca')


token = cfp.get('evernote', 'token')
log2notetimer(token, 60 * 45)
weatherstattimer(token, 60 * 60 * 3 + 60 * 25)
jinchustattimer(token, 60 * 60)

writeini()

# findnotebookfromevernote(token)
# log.debug('程序结束！')
# print(vars())
