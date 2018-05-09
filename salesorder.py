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


def ordergmail(topic):
    host = cfp.get('gmail', 'host')
    username = cfp.get('gmail', 'username')
    password = cfp.get('gmail', 'password')
    mailitems = getMail(host, username, password, dirtarget='Work', topic=topic)

    itemslst = []
    for header, body in mailitems:
        itemslst.append(header[1])
        print(header[1])
    print('从Gmail邮箱获取%d条“%s”相关的信息记录' % (len(itemslst), topic))


if __name__ == '__main__':
    token = cfp.get('evernote', 'token')
    ordergmail('2014-1')
