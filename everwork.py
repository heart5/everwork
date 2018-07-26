# encoding:utf-8
"""
用evernote作为工作平台，通过Python链接整理各种工作数据，呈现给各个相关岗位。.
"""
# import imp4nb
from func.evernt import writeini
from life.noteweather import weatherstattimer  # 调用同目录下其他文件（py）中的函数
from etc.log2note import log2notetimer
from work.order import showorderstat2note
from work.workplan import planfenxi
from work.dutyon import fetchattendance_from_evernote
from life.notejinchujilu import jinchustattimer
from life.peoplelog2note import peoplestattimer
from work.filemail import workfilefromgmail2datacenter
# log.debug('程序启动……')

# nbfbdf = readinisection2df(cfpdata, 'guidfenbunb', '销售业绩图表')
# for aa in nbfbdf.index:
#     cpath = 'img\\'+aa
#     if not os.path.exists(cpath):
#         os.mkdir(cpath)
#         log.debug('目录《' + cpath + '》被创建')

# pickstat(token, note_store, cnx, '1c0830d9-e42f-4ce7-bf36-ead868a55eca', '订单配货统计图', cum=True)



# desclitedb(cnx)
# swissknife(cnx)
# cnx.close()

# isnoteupdate(token, note_store, '1c0830d9-e42f-4ce7-bf36-ead868a55eca')

fetchattendance_from_evernote(60 * 60 * 8)
workfilefromgmail2datacenter(60 * 55)
showorderstat2note(60 * 60 * 1 + 60 * 8)
log2notetimer(60 * 45)
weatherstattimer(60 * 60 * 1 + 60 * 5)
jinchustattimer(60 * 60)
peoplestattimer(60 * 25)
planfenxi(60 * 65 * 2)
#
# writeini()

# findnotebookfromevernote(token)
# log.debug('程序结束！')
# print(vars())
