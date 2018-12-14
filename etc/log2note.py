# -*- coding: utf-8 -*-
"""
4524187f-c131-4d7d-b6cc-a1af20474a7f notification 笔记本
4a940ff2-74a8-4584-be46-aa6d68a4fa53 everworklog 笔记
log目录
"""

import os
from threading import Timer
import pathmagic

with pathmagic.context():
    from func.first import getdirmain
    from func.configpr import getcfp
    from func.evernt import get_notestore, imglist2note
    from func.logme import log
    from func.wrapfuncs import timethis, ift2phone


@timethis
@ift2phone()
def log2note():
    namestr = 'everlog'
    cfp, cfppath = getcfp(namestr)
    if not cfp.has_section(namestr):
        cfp.add_section(namestr)
        cfp.write(open(cfppath, 'w', encoding='utf-8'))
    if cfp.has_option(namestr, 'critical') and (cfp.getboolean(namestr, 'critical') == True):
        levelstr = 'CRITICAL'
    else:
        levelstr = ''

    if levelstr == 'CRITICAL':
        levelstr4title = '严重错误'
    else:
        levelstr4title = ''

    print(getdirmain())
    pathlog = getdirmain() / 'log'
    files = os.listdir(str(pathlog))
    loglines = []
    for fname in files[::-1]:
        with open(pathlog / fname, 'r', encoding='utf-8') as flog:
            loglines = loglines + [line.strip()
                                   for line in flog if line.find(levelstr) >= 0]

    if cfp.has_option(namestr, 'loglimit'):
        loglimit = cfp.getint(namestr, 'loglimit')
    else:
        loglimit = 500
    log.info(f'日志的{levelstr4title}记录共有{len(loglines)}条，只取时间最近的{loglimit}条')
    # print()
    # global cfp, inifilepath
    if cfp.has_option(namestr, 'everlogc'):
        everlogc = cfp.getint(namestr, 'everlogc')
    else:
        everlogc = 0
    if len(loglines) == everlogc:  # <=调整为==，用来应对log文件崩溃重建的情况
        log.info(f'暂无新{levelstr4title}记录，不更新everworklog笔记。')
    else:
        loglinesloglimit = loglines[(-1 * loglimit):]
        loglinestr = '\n'.join(loglinesloglimit[::-1])
        loglinestr = loglinestr.replace('<', '《')
        loglinestr = loglinestr.replace('>', '》')
        loglinestr = loglinestr.replace('&', '并符')
        loglinestr = loglinestr.replace('=', '等于')
        # logbytestr = str(loglinestr.encode('utf-8'))
        # logbytestr = logbytestr.replace('\x16', '')
        # loglinestr = bytes(logbytestr, encoding='utf-8')
        loglinestr = '<pre>' + str(loglinestr) + '</pre>'
        # print(loglinestr)
        noteguid_lognote = '4a940ff2-74a8-4584-be46-aa6d68a4fa53'
        try:
            nstore = get_notestore()
            imglist2note(nstore, [], noteguid_lognote,
                         f'everwork{levelstr4title}日志信息', loglinestr)
            cfp.set(namestr, 'everlogc', f'{len(loglines)}')
            cfp.write(open(cfppath, 'w', encoding='utf-8'))
            log.info(f'新的log{levelstr4title}信息成功更新入笔记')
        except Exception as eeee:
            log.critical(f'处理新的log{levelstr4title}信息到笔记时出现未名错误。{eeee}')


def log2notetimer(jiangemiao):

    log2note()

    global timer_log2note
    timer_log2note = Timer(jiangemiao, log2notetimer, [jiangemiao])
    timer_log2note.start()


if __name__ == '__main__':
    log.info(f'开始运行文件\t{__file__}')
    log2note()
    log.info(f'Done.结束执行文件\t{__file__}')
