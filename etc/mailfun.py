import yagmail
import re
import os
from pathlib import Path

import pathmagic
with pathmagic.context():
    from func.first import dirmainpath
    from func.logme import log
    from func.wrapfuncs import timethis, ift2phone
    from func.configpr import getcfp
    from func.evernttest import getinivaluefromnote

def mailfun(txtfile):
    cfpew, cfpewpath = getcfp('everwork')
    host = cfpew.get('gmail', 'host')
    username = cfpew.get('gmail', 'username')
    password = cfpew.get('gmail', 'password')
    print(f"{username}")
    yag_imap_connecttion = yagmail.SMTP(user=username, password=password,
                                        host=host)
    mail2lst = re.split('[,，]', getinivaluefromnote('mail', 'mailto'))
    subject = str(txtfile)
    if subject.endswith('.txt'):
        flhd = open(txtfile, 'r')
        txtcontent = flhd.read()
        flhd.close()
    else:
        txtcontent = subject
    contents = [txtcontent, str(txtfile)]
    # print(f"{mail2lst}")
    yag_imap_connecttion.send(mail2lst, subject, contents)
    yag_imap_connecttion.close()


def mailfileindir(dirfrom, extstr='.txt'):
    fls = [x for x in os.listdir(dirfrom) if x.endswith(extstr)]
    print(f"{fls}")
    for fl in fls:
        mailfun(dirfrom / fl)

if __name__ == '__main__':
    log.info(f'运行文件\t{__file__}')
    # mailtxtfileindir(dirmainpath / '..')
    mailfileindir(dirmainpath, '.png')
    log.info(f'文件\t{__file__}\t测试完毕。')
