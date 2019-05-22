import yagmail

import pathmagic
with pathmagic.context():
    from func.first import dirmainpath
    from func.logme import log
    from func.wrapfuncs import timethis, ift2phone
    from func.configpr import getcfp

def mailfun():
    cfpew, cfpewpath = getcfp('everwork')
    host = cfpew.get('gmail', 'host')
    username = cfpew.get('gmail', 'username')
    password = cfpew.get('gmail', 'password')
    print(f"{username}")
    yag_imap_connecttion = yagmail.SMTP(user=username, password=password,
                                        host=host)
    subject = "特斯盒yagmail from python"
    contents = ['我是第一个，先来', str(dirmainpath / 'data' / 'everip.ini')]
    yag_imap_connecttion.send('1613394006@qq.com', subject, contents)


if __name__ == '__main__':
    log.info(f'运行文件\t{__file__}')
    mailfun()
    log.info(f'文件\t{__file__}\t测试完毕。')
