"""
检查是否有新的QR，有就发送邮件
"""

import os
import time
import pathmagic

with pathmagic.context():
    from func.logme import log
    from func.first import getdirmain
    from etc.mailfun import mailfileindir
    from func.configpr import getcfpoptionvalue, setcfpoptionvalue
    from etc.getid import getdeviceid
    from func.evernttest import timestamp2str


def findnewqrthensendmail():
    fl = 'QR.png'
    qrfile = getdirmain() / fl
    if os.path.exists(qrfile):
        # print(qrfile)
        # print(os.path.abspath(qrfile))
        qrfiletimeini = getcfpoptionvalue('everwebchat', 'webchat', 'qrfiletime') 
        qrfilesecsnew = os.stat(qrfile).st_mtime
        qrfiletimenew = str(qrfilesecsnew)
        print(f"{qrfiletimeini},{timestamp2str(float(qrfiletimeini))}\t{qrfiletimenew},{timestamp2str(float(qrfiletimenew))}")
        if qrfiletimeini:
            if qrfiletimenew > qrfiletimeini:
                mailfileindir(getdirmain(), fl)
                setcfpoptionvalue('everwebchat', 'webchat', 'qrfiletime',
                                  qrfiletimenew)
        else:
            mailfileindir(getdirmain(), fl)
            setcfpoptionvalue('everwebchat', 'webchat', 'qrfiletime',qrfiletimenew)
    else:
        print(f"{fl}不存在")


if __name__ == '__main__':
    # log.info(f'运行文件\t{__file__}')
    findnewqrthensendmail()
    # log.info(f"文件\t{__file__}\t运行结束。")
