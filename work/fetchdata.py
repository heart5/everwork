# encoding:utf-8
"""
功能描述
"""
from threading import Timer

import pathmagic

with pathmagic.context():
    from func.logme import log
    from func.configpr import cfp
    from func.mailsfunc import getmail
    from func.wrapfuncs import timethis


def fetchworkfile_from_gmail(topic):
    hostg = cfp.get('gmail', 'host')
    usernameg = cfp.get('gmail', 'username')
    passwordg = cfp.get('gmail', 'password')
    dirwork = 'Work'
    mailitemsg = getmail(hostg, usernameg, passwordg, dirtarget=dirwork, unseen=True, topic=topic)
    # mailitemsg = getmail(hostg, usernameg, passwordg, dirtarget='Work', topic=topic)
    if mailitemsg is False:
        log.info('Gmail信箱目录《%s》中暂无新邮件。' % dirwork)
        return

    itemslst = list()
    for headerg, bodyg in mailitemsg:
        itemslst.append(headerg[1])
    print(itemslst)
    topicstring = '“%s”相关的' % topic if len(topic) > 0 else ''
    log.info('从Gmail邮箱目录《%s》中获取%d封%s新邮件。' % (dirwork, len(itemslst), topicstring))


@timethis
def filegmailevernote2datacenter(jiangemiao):
    try:
        fetchworkfile_from_gmail('')
    except Exception as eeee:
        log.critical('从gmail信箱获取工作文件时出现未名错误。%s' % (str(eeee)))

    global timer_filegmail2datacenter
    timer_filegmail2datacenter = Timer(jiangemiao, filegmailevernote2datacenter, [jiangemiao])
    timer_filegmail2datacenter.start()


if __name__ == '__main__':
    log.info(f'运行文件\t{__file__}')
    filegmailevernote2datacenter(60 * 53)
    print('Done')
