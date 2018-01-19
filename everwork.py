# encoding:utf-8
"""
用evernote作为工作平台，通过Python链接整理各种工作数据，呈现给各个相关岗位。.
"""

from imp4nb import *
import evernote.edam.userstore.constants as UserStoreConstants
import evernote.edam.type.ttypes as Types
from evernote.api.client import EvernoteClient
from noteweather import weatherstat #调用同目录下其他文件（py）中的函数
from notewarehouse import *
from notedispatch import *
from notesaledetails import *
from notejinchujilu import *

# thistime = '当前运行时间：' + str(int(time.time())) + '\t' + time.strftime("%Y-%m-%d %H:%M:%S",
#                                                                     time.localtime(time.time()))
log.debug('程序启动……')

token = cfp.get('evernote','token')
log.debug('配置文件读取成功')

note_store = get_notestore(token)

# #列出账户中的全部笔记本
# notebooks = note_store.listNotebooks()
# # printnotebookattributeundertoken(notebooks[-1])
#
# for x in notebooks:
#     printnotebookattributeundertoken(x)

#39ed537d-73fa-4ad8-b4fd-bc6f746fb302 真元日配送图
#1c0830d9-e42f-4ce7-bf36-ead868a55eca 订单配货统计图
#49eff8eb-5bce-43b9-a95a-c1ee7eab71fa 有友全渠道销售图表

# findnotefromnotebook(note_store,token,'c068e01f-1a7a-4e65-b8e4-ed93eed6bd0b','统计') #从笔记本中查找标题中包含指定字符串的笔记

# todo 一体化目录构建
nbfbdf = readinisection2df(cfp,'guidfenbunb','销售业绩图表')
for aa in nbfbdf.index:
    cpath = 'img\\'+aa
    if not os.path.exists(cpath):
        os.mkdir(cpath)
        log.debug('目录《' + cpath + '》被创建')

cnx = lite.connect('data\\quandan.db')
# dataokay(cnx)
# weatherstat(token, note_store, '277dff5e-7042-47c0-9d7b-aae270f903b8', '296f57a3-c660-4dd5-885a-56492deb2cee')
# pickstat(token, note_store, cnx, '1c0830d9-e42f-4ce7-bf36-ead868a55eca', '订单配货统计图', cum=True)
# jilustat(token, note_store, '24aad619-2356-499e-9fa7-f685af3a81b1', '2d908c33-d0a2-4d42-8d4d-5a0bc9d2ff7e',
#          title='公司进出记录统计图表')
# jilustat(token, note_store, 'd8fa0226-88ac-4b6c-b8fd-63a9038a6abf', '08a01c35-d16d-4b22-b7f7-61e3993fd2cb',
#          title='家附近出入统计')

brandlist = ['丽芝士', '兰花恋人',
             '易加', '卤帝七号', '呈呈', '伍滋味', '脆马蹄', '鱼友味', '武丰', '柒柒湘', '俊媳妇', '湘寿鸭', '好媳妇',
              '香之派', '友意', '大西南', '金昌盛', '康赞', '恒的', '孙妈', '银城湘味', '刘香源', '蜀望', '口口德福',
             '威龙', '好运', '心诺',  '农尔康', '君思', '珍可惠', '红帅', '先生', '好棒美', '三友', '君妃', '火卤卤',
             '花氏', '洞庭渔王', '相思', '凤凰园', '洁龙', '怡口湘', '阿林', '好巴食', '巧大娘', '老成都', '一品鱼舫',
             '香约', '朝启', '顶牛', '湘俚味', '红叶', '无穷', '快活嘴', '花心子', '蛋大厨', '绿野香', '佳宝',
             '湘宝王', '乡巴佬', '鑫之恋', '泰越精厨', '可可哥', '倍儿爽', '小鹏', '醉吃香', '津尝乐', '张师傅',
             '馋大嘴', '卫龙', '凤将军', '馋大嘴', '儿时代', '爽口佳', '新丰园', '津津友味', '鲜多鲜', 'U品部落',
             '光头祥', '大霸王', '丽芝士', '非凡', '鲜客', '童年时代', '麦小呆', '渔米之湘',
             'U品部落', '抓鱼的猫', '旭东', '创食人', '']
# brandlist = ['津津友味','鲜多鲜','丽芝士','非凡','鲜客','童年时代','麦小呆','渔米之湘','U品部落',
#              '抓鱼的猫','旭东','创食人','']
# brandlist = ['津津友味','鲜多鲜','丽芝士','童年时代','渔米之湘','U品部落','抓鱼的猫','卫龙','创食人','']
# brandlist = ['']
qrypinpai = "select max(日期) as 最近日期,product.品牌名称 as 品牌 from xiaoshoumingxi,product " \
            "where (product.商品全名 = xiaoshoumingxi.商品全名) group by 品牌 order by 最近日期"
dff = pd.read_sql_query(qrypinpai, cnx, parse_dates=['最近日期'])
print(dff)
# brandlist = list(dff[dff.最近日期 >= (dff.最近日期.max()+pd.Timedelta(days=-90))]['品牌'])
brandlist = list(dff['品牌'])
print(brandlist)
# brandlist = []
for br in brandlist:
    updatesection(cfp, 'guidfenbunb', br + 'kehuguidfenbu', inifilepath, token, note_store, br + '客户开发图表')
    updatesection(cfp, 'guidfenbunb', br + 'saleguidfenbu', inifilepath, token, note_store, br + '销售业绩图表')
    updatesection(cfp, 'guidleixingnb', br + 'kehuguidleixing', inifilepath, token, note_store, br + '客户开发图表')
    updatesection(cfp, 'guidleixingnb', br + 'saleguidleixing', inifilepath, token, note_store, br + '销售业绩图表')

    # notelxxsdf = ['']
    notelxxsdf = readinisection2df(cfp, br + 'saleguidleixing', br + '销售图表')
    notefbxsdf = readinisection2df(cfp, br + 'saleguidfenbu', br + '销售图表')
    # print(notefbxsdf)

    qrystr = "select 日期,strftime('%%Y%%m',日期) as 年月,customer.往来单位编号 as 客户编码," + \
             'sum(金额) as %s, substr(customer.往来单位编号,1,2) as 区域 ,substr(customer.往来单位编号,12,1) as 类型, ' \
             'product.品牌名称 as 品牌 from xiaoshoumingxi, customer, product ' \
             'where (customer.往来单位 = xiaoshoumingxi.单位全名) and (product.商品全名 = xiaoshoumingxi.商品全名) ' \
             '%s %s group by 日期,客户编码 order by 日期'  # % (xmclause,jineclause, brclause)
    xiangmu = ['销售金额', '退货金额']
    fenxiyueduibi(token, note_store, qrystr, xiangmu, notefbxsdf, notelxxsdf, cnx, pinpai=br, cum=True)
    # fenximonthduibi(token, note_store, cnx, notefbxsdf, notelxxsdf, '金额', pinpai=br, cum=True)

    # notelxkhdf = ['']
    notelxkhdf = readinisection2df(cfp, br+'kehuguidleixing', br+'客户图表')
    notefbkhdf = readinisection2df(cfp, br + 'kehuguidfenbu', br + '客户图表')
    # print(notefbkhdf)
    qrystr = "select 日期,strftime('%%Y%%m',日期) as 年月,customer.往来单位编号 as 客户编码," + \
             'count(*) as %s, substr(customer.往来单位编号,1,2) as 区域 ,' \
             'substr(customer.往来单位编号,12,1) as 类型, ' \
             'product.品牌名称 as 品牌 from xiaoshoumingxi, customer, product ' \
             'where (customer.往来单位 = xiaoshoumingxi.单位全名)  and (product.商品全名 = xiaoshoumingxi.商品全名) ' \
             '%s %s group by 日期,客户编码 order by 日期'  # % (xmclause,jineclause, brclause)
    xiangmu = ['销售客户数', '退货客户数']
    fenxiyueduibi(token, note_store, qrystr, xiangmu, notefbkhdf, notelxkhdf, cnx, pinpai=br)
    # fenximonthduibi(token, note_store, '退货客户数', notefbkhdf, notelxkhdf, cnx, pinpai=br)

# desclitedb(cnx)
# swissknife(cnx)
cnx.close()

writeini()
log.debug('程序结束！')
