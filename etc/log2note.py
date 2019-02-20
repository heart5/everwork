# -*- coding: utf-8 -*-
"""
4524187f-c131-4d7d-b6cc-a1af20474a7f notification 笔记本
4a940ff2-74a8-4584-be46-aa6d68a4fa53 everworklog 笔记
log目录
"""

import os
from threading import Timer
import pathmagic
import re
import pandas as pd

with pathmagic.context():
    from func.first import getdirmain
    from func.configpr import getcfp
    from func.evernttest import get_notestore, imglist2note, readinifromnote, token, evernoteapijiayi, makenote
    from func.logme import log
    from func.wrapfuncs import timethis, ift2phone
    from func.termuxtools import termux_location, termux_telephony_deviceinfo
    from func.nettools import ifttt_notify
    # from etc.getid import getdeviceid
    import evernote.edam.type.ttypes as ttypes


@timethis
# @ift2phone()
def log2note(noteguid, loglimit, levelstr='', notetitle='everwork日志信息'):
    namestr = 'everlog'
    cfp, cfppath = getcfp(namestr)
    if not cfp.has_section(namestr):
        cfp.add_section(namestr)
        cfp.write(open(cfppath, 'w', encoding='utf-8'))

    if levelstr == 'CRITICAL':
        levelstrinner = levelstr + ':'
        levelstr4title = '严重错误'
        countnameinini = 'everlogcc'
    else:
        levelstrinner = levelstr
        levelstr4title = ''
        countnameinini = 'everlogc'

    # print(getdirmain())
    pathlog = getdirmain() / 'log'
    files = os.listdir(str(pathlog))
    loglines = []
    for fname in files[::-1]:
        # print(fname)
        if not fname.startswith('everwork.log'):
            log.warning(f'文件《{fname}》不是合法的日志文件，跳过。')
            continue
        with open(pathlog / fname, 'r', encoding='utf-8') as flog:
            loglines = loglines + [line.strip()
                                   for line in flog if line.find(levelstrinner) >= 0]

    ptn = re.compile('\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}')
    tmlst = [pd.to_datetime(re.match(ptn, x).group()) for x in loglines if
             re.match(ptn, x) is not None]
    loglines = [x for x in loglines if re.match(ptn, x) is not None]
    logsr = pd.Series(loglines, index=tmlst)
    logsr = logsr.sort_index()
    # print(logsr.index)
    # print(logsr)
    loglines = list(logsr)
    # print(loglines[:20])
    # print(len(loglines))
    print(f'日志的{levelstr4title}记录共有{len(loglines)}条，只取时间最近的{loglimit}条')
    if cfp.has_option(namestr, countnameinini):
        everlogc = cfp.getint(namestr, countnameinini)
    else:
        everlogc = 0
    # print(everlogc)
    if len(loglines) == everlogc:  # <=调整为==，用来应对log文件崩溃重建的情况
        print(f'暂无新的{levelstr4title}记录，不更新everwork的{levelstr}日志笔记。')
    else:
        loglinesloglimit = loglines[(-1 * loglimit):]
        loglinestr = '\n'.join(loglinesloglimit[::-1])
        loglinestr = loglinestr.replace('<', '《')
        loglinestr = loglinestr.replace('>', '》')
        loglinestr = loglinestr.replace('&', '并符')
        loglinestr = loglinestr.replace('=', '等于')
        loglinestr = '<pre>' + str(loglinestr) + '</pre>'
        # print(loglinestr)
        try:
            nstore = get_notestore()
            imglist2note(nstore, [], noteguid,
                         notetitle, loglinestr)
            cfp.set(namestr, countnameinini, f'{len(loglines)}')
            cfp.write(open(cfppath, 'w', encoding='utf-8'))
            print(f'新的log{levelstr4title}信息成功更新入笔记')
        except Exception as eeee:
            errmsg = f'处理新的log{levelstr4title}信息到笔记时出现未名错误。{eeee}'
            log.critical(errmsg)
            ifttt_notify(errmsg, 'log2note')

def log2notes():
    namestr = 'everlog'
    cfplog, cfplogpath = getcfp(namestr)
    if not cfplog.has_section(namestr):
        cfplog.add_section(namestr)
        cfplog.write(open(cfplogpath, 'w', encoding='utf-8'))
    if cfplog.has_option(namestr, 'device_id'):
        device_id = cfplog.get(namestr, 'device_id')
    else:
        outputdict = termux_telephony_deviceinfo()
        device_id = outputdict["device_id"].strip()
        # device_id =getdeviceid()
        cfplog.set(namestr, 'device_id', device_id)
        cfplog.write(open(cfplogpath, 'w', encoding='utf-8'))
        log.info(f'获取device_id:\t{device_id}，并写入ini文件：\t{cfplogpath}')
    if not cfplog.has_section(device_id):
        cfplog.add_section(device_id)
        cfplog.write(open(cfplogpath, 'w', encoding='utf-8'))

    global token
    if cfplog.has_option(device_id, 'logguid'):
        logguid = cfplog.get(device_id, 'logguid')
    else:
        note_store = get_notestore()
        parentnotebook = note_store.getNotebook('4524187f-c131-4d7d-b6cc-a1af20474a7f')
        evernoteapijiayi()
        note = ttypes.Note()
        note.title = f'服务器_{device_id}_日志信息'
        notelog = makenote(token, note_store, note.title, notebody='', parentnotebook=parentnotebook)
        logguid = notelog.guid
        cfplog.set(device_id, 'logguid', logguid)
        cfplog.write(open(cfplogpath, 'w', encoding='utf-8'))

    if cfplog.has_option(device_id, 'logcguid'):
        logcguid = cfplog.get(device_id, 'logcguid')
    else:
        note_store = get_notestore()
        parentnotebook = note_store.getNotebook('4524187f-c131-4d7d-b6cc-a1af20474a7f')
        evernoteapijiayi()
        note = ttypes.Note()
        note.title = f'服务器_{device_id}_严重错误日志信息'
        notelog = makenote(token, note_store, note.title, notebody='', parentnotebook=parentnotebook)
        logcguid = notelog.guid
        cfplog.set(device_id, 'logcguid', logcguid)
        cfplog.write(open(cfplogpath, 'w', encoding='utf-8'))

    readinifromnote()
    cfpfromnote, cfpfromnotepath = getcfp('everinifromnote')
    namestr = 'everlog'
    if cfpfromnote.has_option(namestr, 'loglimit'):
        loglimitc = cfpfromnote.getint(namestr, 'loglimit')
    else:
        loglimitc = 500
    if cfpfromnote.has_option('device', device_id):
        servername = cfpfromnote.get('device', device_id)
    else:
        servername = device_id

    cfpeverwork, cfpeverworkpath = getcfp('everwork')

    if cfpfromnote.has_option(namestr, 'critical') and (cfpfromnote.getboolean(namestr, 'critical') == True):
        levelstrc = 'CRITICAL'
        # noteguidc = cfpeverwork.get('evernote', 'lognotecriticalguid')
        log2note(logcguid, loglimitc, levelstrc, notetitle=f'服务器_{servername}_严重错误日志信息')

    # noteguidn = cfpeverwork.get('evernote', 'lognoteguid')
    log2note(noteguid=logguid, loglimit=loglimitc, notetitle=f'服务器_{servername}_日志信息')

    # locinfo = termux_location()
    # print(locinfo)
 

if __name__ == '__main__':
    print(f'开始运行文件\t{__file__}')
    log2notes()
    print(f'Done.结束执行文件\t{__file__}')
