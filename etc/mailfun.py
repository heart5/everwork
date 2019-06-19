import argparse
import yagmail
import re
import os
import sys
from pathlib import Path

import pathmagic
with pathmagic.context():
    from func.first import dirmainpath
    from func.logme import log
    from func.wrapfuncs import timethis, ift2phone
    from func.configpr import getcfp
    from func.evernttest import getinivaluefromnote

def mailfun(txtorfile, tonote=False):
    cfpew, cfpewpath = getcfp('everwork')
    host = cfpew.get('gmail', 'host')
    username = cfpew.get('gmail', 'username')
    password = cfpew.get('gmail', 'password')
    # print(f"{username}")
    yag_imap_connecttion = yagmail.SMTP(user=username, password=password,
                                        host=host)
    mail2lst = re.split('[,，]', getinivaluefromnote('mail', 'mailto'))
    if tonote:
        mail2lst.append(getinivaluefromnote('mail', 'mailtonote'))
        print(mail2lst)
    subject = str(txtorfile)
    if os.path.exists(subject):
        print(f"{subject}是个文件")
        if subject.endswith('.txt'):
            flhd = open(txtorfile, 'r')
            txtcontent = flhd.read()
            flhd.close()
        else:
            txtcontent = subject
        contents = [txtcontent, str(txtorfile)]
    else:
        contents = [txtorfile]
        subject = txtorfile[:30]
    # print(f"{mail2lst}")
    yag_imap_connecttion.send(mail2lst, subject, contents)
    yag_imap_connecttion.close()


def mailfileindir(dirfrom, extstr='.txt'):
    fls = [x for x in os.listdir(dirfrom) if x.endswith(extstr)]
    print(f"{fls}")
    for fl in fls:
        mailfun(dirfrom / fl)
        

def configargp():
    parser = argparse.ArgumentParser(description='send files or content to mailbox.(发送文件或者文本内容到邮箱去。)')
    parser.add_argument('content', metavar='File', type=str, nargs='+', help='file name or content')
    parser.add_argument('-to', '--to', metavar='note', type=str, choices=['note'], 
                        help='是否发送至笔记专用信箱创建新笔记')
    if len(sys.argv) == 1:
        parser.print_help()
        exit()
    args = parser.parse_args()
    print(args)
    # print(sys.argv)
    return args



if __name__ == '__main__':
    log.info(f'运行文件\t{__file__}')
    # notelststr = "[['8b83d72c-4497-4366-9ae1-f76ab7da9dae', '../newsapp.txt', 1007566], ['8fa57804-944d-471e-bb4b-15d13dda4d60', '../../guangfa.txt', 988335], ['0bdbf2ac-581b-4f12-890d-90163f602606', '../../weixinyundongpaihangbang.txt', 988333], ['ba164df1-af4d-4d17-a54c-bdd0c9106248', '../../weixinzhifuhuizong.txt', 988332], ['4b613fbd-7e79-4aa5-836c-c38a277514c5', '../../weixinzhifupingzheng.txt', 988331], ['1814a377-7dd4-4168-97a2-ed5e34ceb913', '../../zhuanzhang.txt', 988325], ['ed1335b3-7790-4f40-aa75-c6a6b4712fd1', '../../zixunxml.txt', 988323], ['a326a5c3-9168-4a35-b281-5c43441147b1', '../../didichuxing.txt', 987854], ['a02f87b4-abd8-40e4-bf1f-c8c7497e87a7', '../../ewlog.txt', 990549]"
    # mailfun(notelststr)
    # mailtxtfileindir(dirmainpath / '..')
    args = configargp()
    for fl in args.content:
        if args.to:
            tonote = True
        else:
            tonote = False
        mailfun(dirmainpath / fl, tonote)
    log.info(f'文件\t{__file__}\t运行完毕。')
