# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.10.3
# ---

# %%
import argparse
import yagmail
import re
import os
import sys
# from pathlib import Path

# %%
import pathmagic

# %%
with pathmagic.context():
    from func.first import dirmainpath
    from func.logme import log
    # from func.wrapfuncs import timethis, ift2phone
    from func.configpr import getcfp
    from func.evernttest import getinivaluefromnote


# %%
def mailfun(txtorfile, tonotek=False):
    cfpew, cfpewpath = getcfp('everwork')
    host = cfpew.get('gmail', 'host')
    username = cfpew.get('gmail', 'username')
    password = cfpew.get('gmail', 'password')
    # print(f"{username}")
    yag_imap_connecttion = yagmail.SMTP(user=username, password=password,
                                        host=host)
    mail2lst = re.split('[,，]', getinivaluefromnote('mail', 'mailto'))
    if tonotek:
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


# %%
def mailfileindir(dirfrom, extstr='.txt'):
    fls = [x for x in os.listdir(dirfrom) if x.endswith(extstr)]
    print(f"{fls}")
    for fl1 in fls:
        mailfun(dirfrom / fl1)


# %%
def configargp():
    parser = argparse.ArgumentParser(description='send files or content to mailbox.(发送文件或者文本内容到邮箱去。)')
    parser.add_argument('content', metavar='File', type=str, nargs='+', help='file name or content')
    parser.add_argument('-to', '--to', metavar='note', type=str, choices=['note'],
                        help='是否发送至笔记专用信箱创建新笔记')
    if len(sys.argv) == 1:
        parser.print_help()
        exit()
    args1 = parser.parse_args()
    print(args1)
    # print(sys.argv)
    return args1


# %%
if __name__ == '__main__':
    log.info(f'运行文件\t{__file__}')
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
