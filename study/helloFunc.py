#
# enconding:utf-8
#
# 各种函数、功能测试
#

from imp4nb import *

cnx = lite.connect('..\\data\\quandan.db')

desclitedb(cnx)

cnx.close()
