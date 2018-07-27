# 综合销售分析

from imp4nb import *


def guanlianall(cnx):
    #关联客户档案、产品档案，获得区域信息和品牌信息
    tm0 = time.clock()
    df = pd.read_sql_query(
        "select 日期,职员名称 as 业务主管,单据编号 as 销售单号,商品备注 as 订单单号,单据类型,"
        "摘要,xiaoshoumingxi.单位全名 as 客户,customer.往来单位编号 as 编码,"
        "xiaoshoumingxi.商品全名 as 商品全名,数量,xiaoshoumingxi.单价,金额,"
        "substr(customer.往来单位编号,1,2) as 大区 ,substr(customer.往来单位编号,1,3) as 小区,"
        "substr(customer.往来单位编号,12,1) as 类型编码, leixing.类型 as 客户类型 ,仓库全名 as 仓库, product.品牌名称 as 品牌,"
        "product.品牌分类 as 品牌分类 from xiaoshoumingxi, customer, product,leixing "
        "where (customer.往来单位 = xiaoshoumingxi.单位全名) "
        "and (product.商品全名 = xiaoshoumingxi.商品全名) and (类型编码 = leixing.编码) "
        "order by 日期 desc", cnx)
    tm1 = time.clock()
    # descdb(df)
    tm2 = time.clock()

    # df['日期'] = df['日期'].apply(lambda x: pd.to_datetime(x))
    # descdb(df)
    readytablename = "alldata"
    df.to_sql(name=readytablename, con=cnx, if_exists='replace')
    tm3 = time.clock()
    print("起始：%f，关联客户编码、产品品牌和客户类型：%f，描述：%f，写入%s数据表：%f" %(tm0,tm1-tm0,tm2-tm1,readytablename,tm3-tm2))


def zashua():
    now = datetime.datetime.now()
    nexthour = now + datetime.timedelta(hours=1)
    print(nexthour)
    pass


def timetest():
    '''
    用时测试；删除数据表并压缩数据库占用空间；
    :return:
    '''
    tms = []
    tms.append(time.clock())

    cnx = lite.connect(dbpathquandan)
    tms.append(time.clock())
    # df = pd.read_sql_query("select * from xiaoshoumingxi order by 日期",cnx)
    # print(len(df))
    #
    # guanlianall(cnx)
    desclitedb(cnx)
    tms.append(time.clock())

    # cur = cnx.cursor()
    # result = cur.execute('select * from xiaoshoumingxi where (单据编号=\'XT-2017-08-14-00061\')')
    # for row in result:
    #     print(row)
    # cur.execute('update xiaoshoumingxi set 职员名称=\'梅富忠\' where (单据编号=\'XT-2017-08-14-00061\') and (职员名称=\'耿华忠\')')

    # cnx.cursor().execute('drop table alldata')  # 删除alldata数据表
    # cnx.cursor().execute('VACUUM')  # 压缩
    tms.append(time.clock())

    # desclitedb(cnx)

    df = pd.read_sql_query("select * from xiaoshoumingxi order by 日期", cnx)
    print(len(df))
    tms.append(time.clock())

    cnx.close()

    for i in range(len(tms)):
        print(tms[i], end='\t')

    mons = (datetime.datetime.now() - pd.to_datetime('2010-02-01'))
    print(mons.days)
    print(mons)


def getapitimesfromlog():
    df = pd.read_csv(os.path.join('log', 'everwork.log'), sep='\t',  # index_col= False,
                     header=None, usecols=[0, 1, 2, 3, 4],
                     names=['asctime', 'name', 'filenamefuncName', 'threadNamethreadprocess', 'levelnamemessage'],
                     na_filter=True, parse_dates=[0],
                     skip_blank_lines=True, skipinitialspace=True)
    dfapi2 = df[df.levelnamemessage.str.contains('动用了Evernote API').values == True][['asctime', 'levelnamemessage']]
    # print(dfapi2.tail())
    dfapi2['counts'] = dfapi2['levelnamemessage'].apply(lambda x: int(re.findall('(?P<counts>\d+)', x)[0]))
    # del dfapi2['levelnamemessage']
    jj = dfapi2[dfapi2.asctime == dfapi2.asctime.max()]['counts']
    result = [dfapi2.asctime.max(), int(jj)]
    print(dfapi2[dfapi2.asctime == dfapi2.asctime.max()])
    print(result)
    return result


cnx = lite.connect(dbpathquandan)
# guanlianall(cnx)

# zashua()
# timetest()
getapitimesfromlog()


cnx.close()
