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
    from func.configpr import getcfpoptionvalue, setcfpoptionvalue
    from func.evernttest import get_notestore, imglist2note, readinifromnote, evernoteapijiayi, makenote, getinivaluefromnote
    from func.logme import log
    from func.wrapfuncs import timethis, ift2phone
    from func.termuxtools import termux_location, termux_telephony_deviceinfo
    from func.nettools import ifttt_notify
    from etc.getid import getdeviceid
    import evernote.edam.type.ttypes as ttypes


@timethis
# @ift2phone()
# @profile
def log2note(noteguid, loglimit, levelstr='', notetitle='everwork日志信息'):
    namestr = 'everlog'

    if levelstr == 'CRITICAL':
        levelstrinner = levelstr + ':'
        levelstr4title = '严重错误'
        countnameinini = 'everlogcc'
    else:
        levelstrinner = levelstr
        levelstr4title = ''
        countnameinini = 'everlogc'

    # log.info(getdirmain())
    pathlog = getdirmain() / 'log'
    files = os.listdir(str(pathlog))
    loglines = []
    for fname in files[::-1]:
        # log.info(fname)
        if not fname.startswith('everwork.log'):
            log.warning(f'文件《{fname}》不是合法的日志文件，跳过。')
            continue
        with open(pathlog / fname, 'r', encoding='utf-8') as flog:
            charsnum2showinline = getinivaluefromnote('everlog',
                                                      'charsnum2showinline')
            # print(f"log行最大显示字符数量为：\t{charsnum2showinline}")
            loglines = loglines + [line.strip()[:charsnum2showinline]
                                   for line in flog if line.find(levelstrinner) >= 0]

    ptn = re.compile('\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}')
    tmlst = [pd.to_datetime(re.match(ptn, x).group())
             for x in loglines if re.match(ptn, x)]
    loglines = [x for x in loglines if re.match(ptn, x)]
    logsr = pd.Series(loglines, index=tmlst)
    logsr = logsr.sort_index()
    # print(logsr.index)
    # print(logsr)
    loglines = list(logsr)
    # log.info(loglines[:20])
    # print(len(loglines))
    print(f'日志的{levelstr4title}记录共有{len(loglines)}条，只取时间最近的{loglimit}条')
    if not (everlogc := getcfpoptionvalue(namestr, namestr, countnameinini)):
        everlogc = 0
    # log.info(everlogc)
    if len(loglines) == everlogc:  # <=调整为==，用来应对log文件崩溃重建的情况
        print(f'暂无新的{levelstr4title}记录，不更新everwork的{levelstr}日志笔记。')
    else:
        loglinesloglimit = loglines[(-1 * loglimit):]
        loglinestr = '\n'.join(loglinesloglimit[::-1])
        loglinestr = loglinestr.replace('<', '《').replace('>',
                                                          '》').replace('=', '等于').replace('&', '并或')
        loglinestr = "<pre>" + loglinestr + "</pre>"
        log.info(f"日志字符串长度为：\t{len(loglinestr)}")
        # log.info(loglinestr[:100])
        try:
            nstore = get_notestore()
            imglist2note(nstore, [], noteguid,
                         notetitle, loglinestr)
            setcfpoptionvalue(namestr, namestr, countnameinini, f'{len(loglines)}')
            print(f'新的log{levelstr4title}信息成功更新入笔记')
        except Exception as eeee:
            errmsg = f'处理新的log{levelstr4title}信息到笔记时出现未名错误。{eeee}'
            log.critical(errmsg)
            ifttt_notify(errmsg, 'log2note')


def log2notes():
    namestr = 'everlog'
    device_id = getdeviceid()

    token = getcfpoptionvalue('everwork', 'evernote', 'token')
    # log.info(token)
    if not (logguid := getcfpoptionvalue(namestr, device_id, 'logguid')):
        note_store = get_notestore()
        parentnotebook = note_store.getNotebook(
            '4524187f-c131-4d7d-b6cc-a1af20474a7f')
        evernoteapijiayi()
        note = ttypes.Note()
        note.title = f'服务器_{device_id}_日志信息'

        notelog = makenote(token, note_store, note.title,
                           notebody='', parentnotebook=parentnotebook)
        logguid = notelog.guid
        setcfpoptionvalue(namestr, device_id, 'logguid', logguid)

    if not (logcguid := getcfpoptionvalue(namestr, device_id, 'logcguid')):
        note_store = get_notestore()
        parentnotebook = note_store.getNotebook(
            '4524187f-c131-4d7d-b6cc-a1af20474a7f')
        evernoteapijiayi()
        note = ttypes.Note()
        note.title = f'服务器_{device_id}_严重错误日志信息'
        notelog = makenote(token, note_store, note.title,
                           notebody='', parentnotebook=parentnotebook)
        logcguid = notelog.guid
        setcfpoptionvalue(namestr, device_id, 'logcguid', logcguid)

    if not (loglimitc := getinivaluefromnote(namestr, 'loglimit')):
        loglimitc = 500

    if not (servername := getinivaluefromnote('device', device_id)):
        servername = device_id

    if getinivaluefromnote(namestr, 'critical') == 1:
        levelstrc = 'CRITICAL'
        # noteguidc = cfpeverwork.get('evernote', 'lognotecriticalguid')
        log2note(logcguid, loglimitc, levelstrc,
                 notetitle=f'服务器_{servername}_严重错误日志信息')

    # noteguidn = cfpeverwork.get('evernote', 'lognoteguid')
    log2note(noteguid=logguid, loglimit=loglimitc,
             notetitle=f'服务器_{servername}_日志信息')

    # locinfo = termux_location()
    # print(locinfo)


if __name__ == '__main__':
    log.info(f'开始运行文件\t{__file__}')
    log2notes()
    log.info(f'Done.结束执行文件\t{__file__}')
