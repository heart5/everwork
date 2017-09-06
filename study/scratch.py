#
#encoding:utf-8

#学习时间函数的使用

import time

thistime = '2017-8-6 14:20:00'
timeArray = time.strptime(thistime,'%Y-%m-%d %H:%M:%S')
timeStamp = int(time.mktime(timeArray))
otherTimeStr = time.strftime("%Y/%m/%d %H:%M:%S", timeArray)
print thistime
print timeStamp
print otherTimeStr
print time.localtime()
print time.localtime(timeStamp)