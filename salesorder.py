#
# encoding:utf-8
#
"""
处理订单数据，进行各种统计，用于每日订单核对等工作

"""

from imp4nb import *
from bs4 import BeautifulSoup
from matplotlib.ticker import MultipleLocator, FuncFormatter
import pygsheets


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


def workfilefromgmail2datacenter(jiangemiao):

    try:
        fetchworkfile_from_gmail('')
    except Exception as eeee:
        log.critical('从gmail信箱获取工作文件时出现未名错误。%s' % (str(eeee)))

    global timer_filegmail2datacenter
    timer_filegmail2datacenter = Timer(jiangemiao, workfilefromgmail2datacenter, [jiangemiao])
    timer_filegmail2datacenter.start()


if __name__ == '__main__':
    fetchworkfile_from_gmail('销售订单')
    # workfilefromgmail2datacenter(60*60*2)
