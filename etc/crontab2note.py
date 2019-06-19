"""
检查crontab是否更新，更好就更新相应笔记并发送邮件
"""

import os
import time
import pathmagic

with pathmagic.context():
    from func.logme import log
    from func.first import getdirmain
    from func.mailsfunc import findnewthenupdatenote


def findnewcronthenupdate():
    r = os.popen('whoami')
    me = r.read()[:-1]
    cronfile = f'/data/data/com.termux/files/usr/var/spool/cron/crontabs/{me}'
    findnewthenupdatenote(cronfile, 'eversys', 'everwork', 'cron', 'cron自动运行排期表')
    

if __name__ == '__main__':
    # log.info(f'运行文件\t{__file__}')
    findnewcronthenupdate()
    # log.info(f"文件\t{__file__}\t运行结束。")
