#
#encoding:utf-8

#学习列表

supplies = ["pens", "staplers", "flame- throwers", "binders", "水泥"]
for i in range(len(supplies)):
    print ' Index ', str( i) , ' in supplies is:', supplies[i]

supplies = supplies * 3
for i in range(len(supplies)):
    print ' Index ', str( i) , ' in supplies is:', supplies[i]


#
# catNames = []
# while True:
#     print '请输入您第', len(catNames)+1, '只猫的名字，输入空值则退出'
#     name = str(input())
#     if name == '':
#         break
#     catNames = catNames + [name]
#
# print
# print '爱猫芳名如下：'
# for name in catNames:
#     print ' ',name

#学习时间函数的使用

import time,calendar

thistime = '1976-10-6 14:20:00'
timeArray = time.strptime(thistime,'%Y-%m-%d %H:%M:%S')
timeStamp = int(time.mktime(timeArray))
print thistime
print time.strftime("%Y/%m/%d %H:%M:%S",time.localtime(timeStamp))
print timeStamp
print time.localtime(timeStamp)

print time.strftime("%Y/%m/%d %H:%M:%S",time.localtime())
print int(time.mktime(time.localtime()))
print time.localtime()

cal = calendar.month(2017,9)
print cal