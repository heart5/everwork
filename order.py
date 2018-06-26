#
# encoding:utf-8
#
"""
销售订单处理汇总

名称：业务计划总结    guid：2c8e97b5-421f-461c-8e35-0f0b1a33e91c    更新序列号：471364    默认笔记本：False
创建时间：2016-02-16 19:56:56    更新时间：2018-02-25 00:24:57    笔记本组：None

5830a2f2-7a76-4f1a-a167-1bd18818a141 业务推广日工作总结和计划——周莉

e4e9d529-1996-4701-8e5a-2b2add0abe9e    每日销售订单核对——陈益（2018-06-06 00:00:00）
d8720b96-a067-441f-8b46-654fdbe04e84    每日销售订单核对——耿华忠（2018-06-06 00:00:00）
03d0b2da-9e9d-45cc-a8a7-85e72be900e5    每日销售订单核对——梅富忠（2018-06-06 00:00:00）
161c093c-4603-4802-8c41-cf346eb002bc    每日销售订单核对——徐志伟（2018-06-06 00:00:00）
bba10885-fb93-4fce-bb3f-03d7dd43d189    每日销售订单核对——周莉


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
    ncols = sheet1.ncols
    print(ncols, end='\t')
    if ncols != 13:
        log.info(f'{orderfile}不是合格的日销售订单格式！')
        print()
        return
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
    dforder['日期'] = pd.to_datetime(dforder['日期'])
    dforder['订单编号'] = dforder['单据编号'].apply(lambda x: x.split('-')[-1])
    dforder['金额'] = dforder['金额'].apply(lambda x: float(x))
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
        dfresult = pd.read_sql('select * from \'%s\'' % tablename_order, cnxp, parse_dates=['日期'])
        log.info('订单数据表%s已存在， 从中读取%d条数据记录。' % (tablename_order, dfresult.shape[0]))
    else:
        log.info('订单数据表%s不存在，将创建之。' % tablename_order)
        dfresult = pd.DataFrame()

    files = os.listdir(pathorder)
    for fname in files[::-1]:
        if (fname.startswith('销售订单') > 0) and ((fname.endswith('xls')) or (fname.endswith('xlsx'))):
            yichulifilelist = list()
            if cfpzysm.has_option('销售订单', '已处理文件清单'):
                yichulifilelist = cfpzysm.get('销售订单', '已处理文件清单').split()
            if fname in yichulifilelist:
                continue
            print(fname, end='\t')
            dffname = chulixls_order(pathorder+'\\'+fname)
            if dffname is None:
                continue
            dfresult = dfresult.append(dffname)
            print(dffname.shape[0], end='\t')
            print(dfresult.shape[0])
            yichulifilelist.append(fname)
            cfpzysm.set('销售订单', '已处理文件清单', '%s' % '\n'.join(yichulifilelist))
            cfpzysm.write(open(inizysmpath, 'w', encoding='utf-8'))

    dfresult.drop_duplicates(['单据编号', '日期', '订单编号', '客户名称', '业务人员', '订单金额', '部门'], inplace=True)
    # descdb(dfresult)
    dfttt = dfresult.drop_duplicates()
    if cfpzysm.has_option('销售订单', '记录数'):
        jilucont = cfpzysm.getint('销售订单', '记录数')
    else:
        jilucont = 0
    if dfttt.shape[0] > jilucont:
        dfttt.to_sql(tablename_order, cnxp, index=None, if_exists='replace')
        cnxp.close()
        cfpzysm.set('销售订单', '记录数', '%d' % dfttt.shape[0])
        cfpzysm.write(open(inizysmpath, 'w', encoding='utf-8'))
        log.info('增加有效销售订单数据%d条。' % (dfttt.shape[0] - jilucont))

    return dfttt


def showorderstat():
    # xlsfile = 'data\\work\\销售订单\\销售订单20180606__20180607034848_480667.xls'
    # dforder = chulixls_order(xlsfile)
    pathor = 'data\\work\\销售订单'
    dforder = chulidataindir_order(pathor)
    dforder = dforder.loc[:, ['日期', '订单编号', '部门', '业务人员', '客户名称', '订单金额']]
    dforder.sort_values(by=['日期', '订单编号', '业务人员'], ascending=False, inplace=True)
    zuixinriqi = dforder.groupby(['日期'])['日期'].size().index.max()
    orderdatestr = zuixinriqi.strftime('%F')
    print(orderdatestr, end='\t')
    dforderzuixinriqi = dforder[dforder.日期 == zuixinriqi]
    print(dforderzuixinriqi.shape[0])
    persons = list(dforderzuixinriqi.groupby('业务人员')['业务人员'].count().index)
    # print(persons)
    notestr = '每日销售订单核对'
    if cfpzysm.has_section(notestr) is False:
        cfpzysm.add_section(notestr)
        cfpzysm.write(open(inizysmpath, 'w', encoding='utf-8'))
    for person in persons:
        if cfpzysm.has_option(notestr + 'guid', person) is False:
            try:
                notestore = get_notestore()
                plannote = Ttypes.Note()
                plannote.title = notestr + person
                nBody = '<?xml version="1.0" encoding="UTF-8"?>'
                nBody += '<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">'
                nBody += '<en-note>%s</en-note>' % plannote.title
                plannote.content = nBody
                global workplannotebookguid
                plannote.notebookGuid = workplannotebookguid
                token = cfp.get('evernote', 'token')
                note = notestore.createNote(token, plannote)
                evernoteapijiayi()
                cfpzysm.set(notestr + 'guid', person, '%s' % note.guid)
                cfpzysm.write(open(inizysmpath, 'w', encoding='utf-8'))
                log.info('成功创建%s的%s笔记' % (person, notestr))
            except Exception as ee:
                log.critical('创建%s的%s笔记时出现错误。%s' % (person, notestr, str(ee)))
                continue
        if cfpzysm.has_option(notestr + 'guid', person + '最新订单日期'):
            ordertoday = cfpzysm.get(notestr + 'guid', person + '最新订单日期')
            if zuixinriqi <= pd.to_datetime(ordertoday):
                continue
        dfperson = dforderzuixinriqi[dforderzuixinriqi.业务人员 == person]
        dfpersonsum = dfperson.groupby('业务人员').sum()['订单金额']
        dfperson.loc['合计', :] = None
        dfperson.loc['合计', '订单金额'] = dfpersonsum[0]
        dfperson.loc['合计', '订单编号'] = dfperson.shape[0] - 1
        print(person, end='\t')
        print(dfpersonsum[0], end='\t')
        personguid = cfpzysm.get(notestr + 'guid', person)
        print(personguid)
        neirong = tablehtml2evernote(dfperson, notestr)
        # print(neirong)
        try:
            notestore = get_notestore()
            imglist2note(notestore, [], personguid, '%s——%s（%s）' % (notestr, person, orderdatestr), neirong)
            cfpzysm.set(notestr + 'guid', person + '最新订单日期', '%s' % orderdatestr)
            cfpzysm.write(open(inizysmpath, 'w', encoding='utf-8'))
        except Exception as eeee:
            log.critical('更新笔记%s——%s（%s）时出现严重错误。%s' % (notestr, person, orderdatestr, str(eeee)))
    else:
        log.info('下列人员的销售订单正常处置完毕：%s' % persons)

    yuechuriqi = pd.to_datetime(f"{zuixinriqi.strftime('%Y')}-{zuixinriqi.strftime('%m')}-01")
    dfsales = dforder[dforder.日期 >= yuechuriqi]
    notestr = '销售订单金额（月）'
    if cfpzysm.has_section(notestr) is False:
        cfpzysm.add_section(notestr)
        cfpzysm.write(open(inizysmpath, 'w', encoding='utf-8'))
    for person in persons:
        if cfpzysm.has_option(notestr, person) is False:
            try:
                notestore = get_notestore()
                plannote = Ttypes.Note()
                plannote.title = notestr + person
                nBody = '<?xml version="1.0" encoding="UTF-8"?>'
                nBody += '<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">'
                nBody += '<en-note>%s</en-note>' % plannote.title
                plannote.content = nBody
                plannote.notebookGuid = workplannotebookguid
                token = cfp.get('evernote', 'token')
                note = notestore.createNote(token, plannote)
                evernoteapijiayi()
                cfpzysm.set(notestr, person, '%s' % note.guid)
                cfpzysm.write(open(inizysmpath, 'w', encoding='utf-8'))
                log.info('成功创建%s的%s笔记' % (person, notestr))
            except Exception as ee:
                log.critical('创建%s的%s笔记时出现错误。%s' % (person, notestr, str(ee)))
                continue
        if cfpzysm.has_option(notestr, person + '最新订单日期'):
            ordertoday = cfpzysm.get(notestr, person + '最新订单日期')
            if zuixinriqi <= pd.to_datetime(ordertoday):
                continue
        dfperson = dfsales[dfsales.业务人员 == person]
        dfpersonsum = dfperson.groupby('日期').sum()['订单金额'].sum()
        dfperson.loc['合计', :] = None
        dfperson.loc['合计', '订单金额'] = dfpersonsum
        dfperson.loc['合计', '订单编号'] = dfperson.shape[0] - 1
        print(person, end='\t')
        print(dfpersonsum, end='\t')
        personguid = cfpzysm.get(notestr, person)
        print(personguid)
        neirong = tablehtml2evernote(dfperson, notestr)
        # print(neirong)
        try:
            notestore = get_notestore()
            imglist2note(notestore, [], personguid, '%s——%s（%s）' % (notestr, person, orderdatestr), neirong)
            cfpzysm.set(notestr, person + '最新订单日期', '%s' % orderdatestr)
            cfpzysm.write(open(inizysmpath, 'w', encoding='utf-8'))
        except Exception as eeee:
            log.critical('更新笔记%s——%s（%s）时出现严重错误。%s' % (notestr, person, orderdatestr, str(eeee)))
    else:
        log.info('下列人员的销售订单金额正常处置完毕：%s' % persons)


def showorderstat2note(jiangemiao):
    global workplannotebookguid
    workplannotebookguid = '2c8e97b5-421f-461c-8e35-0f0b1a33e91c'
    try:
        showorderstat()
    except Exception as ee:
        log.critical('处理订单核对统计笔记时出现错误。%s' % str(ee))

    global timer_showorderstat
    timer_showorderstat = Timer(jiangemiao, showorderstat2note, [jiangemiao])
    timer_showorderstat.start()

if __name__ == '__main__':
    # chulidataindir_order()
    # showorderstat()
    showorderstat2note(60 * 10)
    # chulixls_order(get_notestore())
    # token = cfp.get('evernote', 'token')
    # guids = findnotefromnotebook(token, '2c8e97b5-421f-461c-8e35-0f0b1a33e91c', '销售订单')
    # for item in guids:
    #     print("%s = %s" %(item[1], item[0]))

    pass

