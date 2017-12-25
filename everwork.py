#
# encoding:utf-8
#
# 用evernote作为工作平台，通过Python链接整理各种工作数据，呈现给各个相关岗位。.
#
#
from imp4nb import *
import evernote.edam.userstore.constants as UserStoreConstants
import evernote.edam.type.ttypes as Types
from evernote.api.client import EvernoteClient
from noteweather import weatherstat #调用同目录下其他文件（py）中的函数
from notewarehouse import *
from notedispatch import *

# thistime = '当前运行时间：' + str(int(time.time())) + '\t' + time.strftime("%Y-%m-%d %H:%M:%S",
#                                                                     time.localtime(time.time()))
log.debug('程序启动……')

cfp =ConfigParser()
cfp.read('data\\everwork.ini')
cfp.sections()
token = cfp.get('evernote','token')
# print(token)
log.debug('配置文件读取成功')


note_store = get_notestore(token)

# 列出账户中的全部笔记本
notebooks = note_store.listNotebooks()
printnotebookattributeundertoken(notebooks[-1])

# for x in notebooks:
#     printnotebookattributeundertoken(x)
# printnotefromnotebook('31eee750-e240-438b-a1f5-03ce34c904b4',100,'天气')
# printnotefromnotebook('87bbbe9a-4e9c-4f5d-84fb-1e94e62a0ec9',100,'订单')
# printnotefromnotebook('ba1423ed-5da1-4883-a2cc-070c93bf7e98',100,'销售')

#仓库管理 87bbbe9a-4e9c-4f5d-84fb-1e94e62a0ec9
#行政管理 31eee750-e240-438b-a1f5-03ce34c904b4
#武昌一部营销推广管理 bc69c8c1-1c51-4ab2-b7ff-d3ad649b647e
#武昌二部营销推广管理    guid：8cab2a52-c8a4-488c-b8e8-4180d06efc3b
#汉阳办营销推广管理    guid：1e365487-d2e1-4562-bf68-8189d347f589
#汉口办营销推广管理    guid：f9a9338f-ee36-49c3-b9fb-351305546b94
#经营    guid：ba1423ed-5da1-4883-a2cc-070c93bf7e98

#e5d81ffa-89e7-49ff-bd4c-a5a71ae14320 武汉雨天记录
#296f57a3-c660-4dd5-885a-56492deb2cee 武汉天气图
#277dff5e-7042-47c0-9d7b-aae270f903b8 武汉每日天气
#39ed537d-73fa-4ad8-b4fd-bc6f746fb302 真元日配送图
#1c0830d9-e42f-4ce7-bf36-ead868a55eca 订单配货统计图
#88c20442-6b4f-4bef-8c0b-ef6878397bf5 武昌一部销售业绩图表
#b8e0dc4a-933f-4753-a14b-b5635bc122d0 武昌二部销售业绩图表
#8a0606e4-ffac-4935-84e5-c235926e3fab 汉阳办销售业绩图表
#cd7c4002-80ee-4741-8ccb-eb58f45023a1 汉口办销售业绩图表
#1717d56c-1308-4447-a22e-9d6648631716 销售业绩图表

# weatherstat(note_store, '277dff5e-7042-47c0-9d7b-aae270f903b8', '296f57a3-c660-4dd5-885a-56492deb2cee')

notefenbulist=[
    ['一部','88c20442-6b4f-4bef-8c0b-ef6878397bf5','武昌一部销售业绩图表'],
    ['二部','b8e0dc4a-933f-4753-a14b-b5635bc122d0','武昌二部销售业绩图表'],
    ['汉阳','8a0606e4-ffac-4935-84e5-c235926e3fab','汉阳办销售业绩图表'],
    ['汉口','cd7c4002-80ee-4741-8ccb-eb58f45023a1','汉口办销售业绩图表'],
    ['销售部','1717d56c-1308-4447-a22e-9d6648631716','销售业绩图表']
]
notefenbudf = pd.DataFrame(notefenbulist,columns=['fenbu','guid','title'])
notefenbudf.index = notefenbudf['fenbu']
# descdb(notefenbudf)
# print(notefenbudf.loc['汉口'])
# print(notefenbudf.loc['汉口']['guid'])
# print(notefenbudf.loc['汉口']['title'])
# print(notefenbulist[0])
cnx = lite.connect('data\\quandan.db')
# dataokay(cnx)
# pickstat(note_store,cnx, '1c0830d9-e42f-4ce7-bf36-ead868a55eca','订单配货统计图')

qrystr = "select 日期,count(*) as 单数,sum(金额) as %s,substr(customer.往来单位编号,1,2) as 区域 ," \
         "substr(customer.往来单位编号,12,1) as 类型,product.品牌名称  as 品牌 from xiaoshoumingxi," \
         "customer,product where (customer.往来单位 = xiaoshoumingxi.单位全名) " \
         "and (product.商品全名 = xiaoshoumingxi.商品全名) and(区域 in %s) " \
         "and(类型 in %s) group by 日期"
# print(qrystr %('金额','(01,02,03)','()'))
fenxi(note_store,qrystr,'金额',notefenbudf,cnx)
# desclitedb(cnx)
# swissknife(cnx)
cnx.close()
log.debug('程序结束！')