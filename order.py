#
# encoding:utf-8
#
"""
销售订单处理汇总

名称：业务计划总结    guid：2c8e97b5-421f-461c-8e35-0f0b1a33e91c    更新序列号：471364    默认笔记本：False
创建时间：2016-02-16 19:56:56    更新时间：2018-02-25 00:24:57    笔记本组：None

5830a2f2-7a76-4f1a-a167-1bd18818a141 业务推广日工作总结和计划——周莉


名称：人事管理    guid：3d927c7e-98a6-4761-b0c6-7fba1348244f    更新序列号：47266    默认笔记本：False
创建时间：2015-07-14 13:50:09    更新时间：2015-07-14 13:50:09    笔记本组：origin
992afcfb-3afb-437b-9eb1-7164d5207564 在职业务人员名单
"""
from imp4nb import *
import xlrd


def chulixls_order(orderfile):
    book = xlrd.open_workbook(orderfile, encoding_override='gb18030')
    sheet_name = book.sheet_names()[0]  # 获得指定索引的sheet表名字
    print(sheet_name, end='\t')
    sheet1 = book.sheet_by_name(sheet_name)  # 通过sheet名字来获取，当然如果知道sheet名字就可以直接指定
    nrows = sheet1.nrows  # 获取行总数
    # ncols = sheet1.ncols
    biglist = []
    for i in range(nrows):
        rowlist = []
        for j in [1, 2, 5, 7, 9, 10]:
            rowlist.append(sheet1.cell_value(i, j))
        biglist.append(rowlist)

    # print(biglist[0])
    # print(biglist[1])
    orderdatestr = biglist[1][0]
    # print(orderdatestr)
    orderdate = pd.to_datetime(orderdatestr)
    print(orderdate)
    dforder = pd.DataFrame(biglist[1:-2], columns=biglist[0])
    # dforder['日期'] = dforder['单据编号'].apply(lambda x: pd.to_datetime(x[3:13]))
    dforder['订单编号'] = dforder['单据编号'].apply(lambda x: x.split('-')[-1])
    dforder['金额'] = dforder['金额'].apply(lambda x: int(x[:-3]))
    dforder = dforder.loc[:, ['单据编号', '日期', '订单编号', '往来单位', '经办人', '金额', '部门全名']]
    dfordergengming = pd.DataFrame(dforder, copy=True)
    dfordergengming.columns = ['单据编号', '日期', '订单编号', '客户名称', '业务人员', '订单金额', '部门']
    # print(dfordergengming)

    return dfordergengming


def chulidataindir_order(pathorder):
    cnxp = lite.connect('data\\workplan.db')
    tablename_order = 'salesorder'
    sqlstr = "select count(*)  from sqlite_master where type='table' and name = '%s'" % tablename_order
    tablexists = pd.read_sql_query(sqlstr, cnxp).iloc[0, 0] > 0
    if tablexists:
        dfresult = pd.read_sql('select * from \'%s\'' % tablename_order, cnxp)
        log.info('订单数据表%s已存在， 从中读取%d条数据记录。' % (tablename_order, dfresult.shape[0]))
    else:
        log.info('订单数据表%s不存在，将创建至。' % tablename_order)
        dfresult = pd.DataFrame()

    files = os.listdir(pathorder)
    for fname in files[::-1]:
        if fname.startswith('销售订单') > 0:
            yichulifilelist = list()
            # if cfpzysm.has_option('销售订单', '已处理文件清单'):
            #     yichulifilelist = cfpzysm.get('销售订单', '已处理文件清单').split()
            if fname in yichulifilelist:
                continue
            print(fname, end='\t')
            dffname = chulixls_order(pathorder+'\\'+fname)
            if dfresult.shape[0] == 0:
                dfresult = dffname
            else:
                dfresult.append(dffname, ignore_index=True)
            print(dffname.shape[0])
            yichulifilelist.append(fname)
            cfpzysm.set('销售订单', '已处理文件清单', '%s' % '\n'.join(yichulifilelist))
            cfpzysm.write(open(inizysmpath, 'w', encoding='utf-8'))

    # dfresult.drop_duplicates(['单据编号', '日期', '订单编号', '客户名称', '业务人员', '订单金额', '部门'], inplace=True)
    descdb(dfresult)
    dfttt = dfresult.drop_duplicates()
    dfttt.to_sql(tablename_order, cnxp, if_exists='replace')
    if cfpzysm.has_option('销售订单', '记录数'):
        jilucont = cfpzysm.getint('销售订单', '记录数')
    else:
        jilucont = 0
    if dfttt.shape[0] > jilucont:
        cfpzysm.set('销售订单', '记录数', '%d' % dfttt.shape[0])
        cfpzysm.write(open(inizysmpath, 'w', encoding='utf-8'))
        log.info('增加有效销售订单数据%d条。' % (dfttt.shape[0] - jilucont))

    return dfttt


def showorderstat():
    # xlsfile = 'data\\work\\销售订单\\销售订单20180606__20180607034848_480667.xls'
    # dforder = chulixls_order(xlsfile)
    pathor = 'data\\work\\销售订单'
    dforder = chulidataindir_order(pathor)
    dforder = dforder.loc[:, ['日期', '订单编号', '往来单位', '经办人', '金额', '部门全名']]
    zuixinriqi = dforder.groupby('日期').max().index[0]
    orderdatestr = zuixinriqi
    print(orderdatestr, end='\t')
    dforderzuixinriqi = dforder[dforder.日期 == zuixinriqi]
    persons = list(dforder.groupby('业务人员').count().index)
    print(persons)
    notestore = get_notestore()
    notestr = '每日销售订单核对'
    for person in persons:
        dfperson = dforderzuixinriqi[dforderzuixinriqi.业务人员 == person]
        dfpersonsum = dfperson.groupby('业务人员').sum()['订单金额']
        dfperson.loc[dfpersonsum[0]] = None
        dfperson.loc[dfpersonsum[0], '订单金额'] = dfpersonsum[0]
        dfperson.loc[dfpersonsum[0], '订单编号'] = dfperson.shape[0]-1
        print(person, end='\t')
        print(dfpersonsum[0], end='\t')
        personguid = cfpzysm.get('%sguid' % notestr, person)
        print(personguid)
        neirong = tablehtml2evernote(dfperson, notestr)
        # print(neirong)
        imglist2note(notestore, [], personguid, '%s——%s（%s）' % (notestr, person, orderdatestr), neirong)
        pass


if __name__ == '__main__':
    # chulidataindir_order()
    showorderstat()
    # chulixls_order(get_notestore())
    # guids = findnotefromnotebook(token, '2c8e97b5-421f-461c-8e35-0f0b1a33e91c', '销售订单')
    # print(guids)

    pass

