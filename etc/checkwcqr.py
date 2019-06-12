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
    from func.evernttest import timestamp2str, imglist2note, note_store, getinivaluefromnote


def findnewqrthensendmail():
    fl = 'QR.png'
    qrfile = getdirmain() / fl
    if os.path.exists(qrfile):
        # print(qrfile)
        # print(os.path.abspath(qrfile))
        qrfiletimeini = getcfpoptionvalue('everwebchat', 'webchat', 'qrfiletime') 
        qrfilesecsnew = os.stat(qrfile).st_mtime
        qrfiletimenew = str(qrfilesecsnew)
        if qrfiletimeini:
            qrftlst = qrfiletimeini.split(',')
            print(timestamp2str(float(qrftlst[0])))
            if (qrfiletimenew > qrftlst[0]): # or True:
                qrtstr = f"{qrfiletimenew},{qrfiletimeini}"
                qrtstrlst = qrtstr.split(',')
                qrtstrflst = [timestamp2str(float(x)) for x in qrtstrlst]
                targetstr = '<pre>'+'\n'.join(qrtstrflst)+'</pre>'
                qrnoteguid = getinivaluefromnote('webchat', f"qr{getdeviceid()}")
                imglist2note(note_store, [qrfile], qrnoteguid,
                             f"{getinivaluefromnote('device', getdeviceid())} QR微信二维码", targetstr)
                mailfileindir(getdirmain(), fl)
                setcfpoptionvalue('everwebchat', 'webchat', 'qrfiletime', qrtstr)
        else:
            mailfileindir(getdirmain(), fl)
            setcfpoptionvalue('everwebchat', 'webchat', 'qrfiletime',qrfiletimenew)
    else:
        print(f"{fl}不存在")


if __name__ == '__main__':
    # log.info(f'运行文件\t{__file__}')
    findnewqrthensendmail()
    # log.info(f"文件\t{__file__}\t运行结束。")
