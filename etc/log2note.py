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
    from func.evernttest import get_notestore, imglist2note, readinifromnote
    from func.logme import log
    from func.wrapfuncs import timethis, ift2phone
    from func.termuxtools import termux_location
    from func.nettools import ifttt_notify


@timethis
# @ift2phone()
def log2note(noteguid, loglimit, levelstr=''):
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
                         f'everwork{levelstr4title}日志信息', loglinestr)
            cfp.set(namestr, countnameinini, f'{len(loglines)}')
            cfp.write(open(cfppath, 'w', encoding='utf-8'))
            print(f'新的log{levelstr4title}信息成功更新入笔记')
        except Exception as eeee:
            errmsg = f'处理新的log{levelstr4title}信息到笔记时出现未名错误。{eeee}'
            log.critical(errmsg)
            ifttt_notify(errmsg, 'log2note')


if __name__ == '__main__':
    print(f'开始运行文件\t{__file__}')
    readinifromnote()
    cfpfromnote, cfpfromnotepath = getcfp('everinifromnote')
    namestr = 'everlog'
    if cfpfromnote.has_option(namestr, 'loglimit'):
        loglimitc = cfpfromnote.getint(namestr, 'loglimit')
    else:
        loglimitc = 500

    cfpeverwork, cfpeverworkpath = getcfp('everwork')

    if cfpfromnote.has_option(namestr, 'critical') and (cfpfromnote.getboolean(namestr, 'critical') == True):
        levelstrc = 'CRITICAL'
        noteguidc = cfpeverwork.get('evernote', 'lognotecriticalguid')
        log2note(noteguidc, loglimitc, levelstrc)

    noteguidn = cfpeverwork.get('evernote', 'lognoteguid')
    log2note(noteguid=noteguidn, loglimit=loglimitc)

    # locinfo = termux_location()
    # print(locinfo)
    print(f'Done.结束执行文件\t{__file__}')
