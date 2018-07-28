# encoding:utf-8
"""
用evernote作为工作平台，通过Python链接整理各种工作数据，呈现给各个相关岗位。.
"""
# import imp4nb
from life.noteweather import weatherstattimer  # 调用同目录下其他文件（py）中的函数
from etc.log2note import log2notetimer
from work.order import showorderstat2note
from work.workplan import planfenxi
from life.notejinchujilu import jinchustattimer
from life.peoplelog2note import peoplestattimer
from work.filemail import workfilefromgmail2datacenter
from func.logme import log

log.debug('自动线程任务启动……')
# pickstat(token, note_store, cnx, '1c0830d9-e42f-4ce7-bf36-ead868a55eca', '订单配货统计图', cum=True)
# desclitedb(cnx)
# swissknife(cnx)
# cnx.close()
# isnoteupdate(token, note_store, '1c0830d9-e42f-4ce7-bf36-ead868a55eca')
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
log.info('自动线程任务启动完毕！')
