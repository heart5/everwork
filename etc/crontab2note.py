"""
检查crontab是否更新，有更新就更新相应笔记并并开关设置发送邮件
"""

import os
import re
import pathmagic

with pathmagic.context():
    # from func.first import dirmainpath
    from func.logme import log
    from func.mailsfunc import findnewthenupdatenote


def findnewcronthenupdate():

    # 获取用户名，方便适配不同的运行平台
    r = os.popen('whoami')
    me = r.read()[:-1]
    print(me)
    cronfile = f'/data/data/com.termux/files/usr/var/spool/cron/crontabs/{me}'
    cfl = open(cronfile, 'r').readlines()
    cflen = [len(x.split()) for x in cfl if not x.startswith('#')]
    clean = True
    for it in cflen:
        clean = clean and (it >= 6)
        if not clean:
            break

    if clean:
        findnewthenupdatenote(cronfile, 'eversys', 'everwork', 'cron', 'cron自动运行排期表', sendmail=True)
    else:
        log.critical(f"自动运行排表有误，请检查。{len(cflen)}\t{cflen}")


def findcronlogthenupdate():
    logpath = "/data/termux/com.termux/files/usr/var/log"
    # logpath = dirmainpath / 'log'
    logfiles = os.listdir(logpath)
    ptn = re.compile("ew_")
    # ptn = re.compile("ever")
    ewlogfiles = [ x for x in logfiles if re.match(ptn, x) and x.endswith('.log')]
    print(ewlogfiles)
    for item in ewlogfiles:
        pre = re.split(ptn, item)[1].replace('.', '_')
        print(pre)
        findnewthenupdatenote(item, 'eversys', 'everwork', pre, f"cron_{pre}", f"cron_{pre}日志")


if __name__ == '__main__':
    # log.info(f'运行文件\t{__file__}')
    findnewcronthenupdate()
    findcronlogthenupdate()
    # log.info(f"文件\t{__file__}\t运行结束。")
