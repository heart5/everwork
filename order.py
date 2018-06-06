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


def chulidata_order():
    pass


def chulixls_order(notestore):
    pathlog = 'data\\work\\销售订单'
    files = os.listdir(pathlog)
    print(files)
    ordernames = []
    for fname in files[::-1]:
        if fname.startswith(''):
            ordernames.append(fname)

    print(ordernames)

    xlsfile = 'data\\work\\销售订单\\销售订单20180605.xls'
    book = xlrd.open_workbook(xlsfile, encoding_override='gb18030')
    sheet_name = book.sheet_names()[0]  # 获得指定索引的sheet表名字
    print(sheet_name)
    sheet1 = book.sheet_by_name(sheet_name)  # 通过sheet名字来获取，当然如果知道sheet名字就可以直接指定
    nrows = sheet1.nrows  # 获取行总数
    # ncols = sheet1.ncols
    biglist = []
    for i in range(nrows):
        rowlist = []
        for j in [2, 5, 7, 9, 10]:
            rowlist.append(sheet1.cell_value(i, j))
        biglist.append(rowlist)

    print(biglist[0])
    print(biglist[1])
    orderdatestr = biglist[1][0][3:13]
    print(orderdatestr)
    orderdate = pd.to_datetime(orderdatestr)
    print(orderdate)
    dforder = pd.DataFrame(biglist[1:-2], columns=biglist[0])
    dforder['金额'] = dforder['金额'].apply(lambda x: int(x[:-3]))
    dforder['单据编号'] = dforder['单据编号'].apply(lambda x: x[14:])
    dforder = dforder.loc[:, ['单据编号', '往来单位', '经办人', '金额', '部门全名']]
    dfordergengming = pd.DataFrame(dforder, copy=True)
    dfordergengming.columns = ['订单编号', '客户名称', '业务人员', '订单金额', '部门']
    print(dfordergengming)
    persons = list(dfordergengming.groupby('业务人员').count().index)
    print(persons)
    notestr = '每日销售订单核对'
    for person in persons:
        dfperson = dfordergengming[dfordergengming.业务人员 == person]
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
    token = cfp.get('evernote', 'token')
    chulixls_order(get_notestore())
    # guids = findnotefromnotebook(token, '2c8e97b5-421f-461c-8e35-0f0b1a33e91c', '销售订单')
    # print(guids)
    pass

