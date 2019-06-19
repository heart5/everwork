"""
检查是否有新的QR，有就发送邮件
"""

import os
import time
import pathmagic

with pathmagic.context():
    from func.logme import log
    from func.first import getdirmain
    from func.mailsfunc import findnewthenupdatenote


def findnewqrthensendmail():
    fl = 'QR.png'
    qrfile = getdirmain() / fl
    findnewthenupdatenote(qrfile, 'everwebchat', 'webchat', 'qr', 'QR微信二维码')
    

def findnewcronthenupdate():
    r = os.popen('whoami')
    me = r.read()[:-1]
    cronfile = f'/data/data/com.termux/files/usr/var/spool/cron/crontabs/{me}'
    findnewthenupdatenote(cronfile, 'everwork', 'everwork', 'cron',
                          'cron自动运行排期表')
    

if __name__ == '__main__':
    # log.info(f'运行文件\t{__file__}')
    findnewqrthensendmail()
    findnewcronthenupdate()
    # log.info(f"文件\t{__file__}\t运行结束。")
