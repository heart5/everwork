#
# encoding:utf-8
#
"""
销售订单明细处理汇总

名称：人事管理    guid：3d927c7e-98a6-4761-b0c6-7fba1348244f    更新序列号：47266    默认笔记本：False
创建时间：2015-07-14 13:50:09    更新时间：2015-07-14 13:50:09    笔记本组：origin
992afcfb-3afb-437b-9eb1-7164d5207564 在职业务人员名单
"""
import os
import datetime
# import xlrd
import pandas as pd
import sqlite3 as lite
import evernote.edam.type.ttypes as Ttypes
from threading import Timer
from func.configpr import cfp, cfpzysm, inizysmpath, cfpdata, inidatanotefilepath
from func.evernt import get_notestore, imglist2note, tablehtml2evernote, evernoteapijiayi
from func.logme import log
from func.first import dirmain, dirmainpath, dbpathworkplan, dbpathquandan
from func.pdtools import dftotal2top


def chulixls_order(orderfile):
    df = pd.read_excel(str(dirmainpath / 'data' / 'work' / '订单明细' / orderfile), index_col=0, parse_dates=True)
    log.info('读取%s' % orderfile)
    print(list(df.columns))
    # ['日期', '单据编号', '摘要', '单位全名', '仓库全名', '商品编号', '商品全名', '规格', '型号', '产地', '单位', '数量', '单价', '金额', '数量1', '单价1',
    # '金额1', '数量2', '单价2', '金额2']
    totalin = ['%.2f' % df.loc[df.index.max()]['数量'], '%.2f' % df.loc[df.index.max()]['金额']]  # 从最后一行获取数量合计和金额合计，以备比较
    print(totalin)
    # df[xiangmu[0]] = None
    # df = df.loc[:, ['日期', '单据编号', '单据类型', xiangmu[0], '摘要', '备注', '商品备注', xiangmu[1],
    #                 '单价', '单位', '数量', '金额', '单位全名', '仓库全名', '部门全名']]
    df = df.loc[:, df.columns[:-6]]
    df['日期'] = pd.to_datetime(df['日期'])
    # df['备注'] = df['备注'].astype(object)
    dfdel = df[
        (df.单位全名.isnull().values == True) & ((df.单据编号.isnull().values == True) | (df.单据编号 == '小计') | (df.单据编号 == '合计'))]
    hangdel = list(dfdel.index)
    print(hangdel)
    df1 = df.drop(hangdel)  # 丢掉小计和合计行，另起DataFrame
    dfzhiyuan = df1[df1.单位全名.isnull().values == True]  # 提取出项目名称行号
    zyhang = list(dfzhiyuan.index)
    zyming = list(dfzhiyuan['单据编号'])  # 项目名称

    # 每次填充df到最后一行，依次滚动更新之
    df['员工名称'] = None
    for i in range(len(zyhang)):
        df.loc[zyhang[i]:, '员工名称'] = zyming[i]

    # 丢掉项目名称行，留下纯数据
    dfdel = df[df.单位全名.isnull().values == True]
    # print(dfdel[['日期', '单据编号', '数量', '金额']])
    hangdel = list(dfdel.index)
    print(hangdel)
    dfout = df.drop(hangdel)
    dfout.index = range(len(dfout))
    dfout = pd.DataFrame(dfout)
    # print(dfout)
    print(dfout.head(10))
    log.info('共有%d条有效记录' % len(dfout))

    print(dfout.groupby(['员工名称']).sum())
    return dfout


def chulidataindir_order(pathorder):
    cnxp = lite.connect(dbpathworkplan)
    tablename_order = 'salesorder'
    sqlstr = "select count(*)  from sqlite_master where type='table' and name = '%s'" % tablename_order
    tablexists = pd.read_sql_query(sqlstr, cnxp).iloc[0, 0] > 0
    if tablexists:
        dfresult = pd.read_sql('select * from \'%s\'' % tablename_order, cnxp, parse_dates=['日期'])
        log.info('订单数据表%s已存在， 从中读取%d条数据记录。' % (tablename_order, dfresult.shape[0]))
    else:
        log.info('订单数据表%s不存在，将创建之。' % tablename_order)
        dfresult = pd.DataFrame()

    notestr = '销售订单'
    if cfpzysm.has_section(notestr) is False:
        cfpzysm.add_section(notestr)
        cfpzysm.write(open(inizysmpath, 'w', encoding='utf-8'))
    files = os.listdir(str(pathorder))
    for fname in files[::-1]:
        if fname.startswith('销售订单') and (fname.endswith('xls') or fname.endswith('xlsx')):
            yichulifilelist = list()
            if cfpzysm.has_option('销售订单', '已处理文件清单'):
                yichulifilelist = cfpzysm.get('销售订单', '已处理文件清单').split()
            if fname in yichulifilelist:
                continue
            print(fname, end='\t')
            dffname = chulixls_order(str(pathorder / fname))
            if dffname is None:
                continue
            dfresult = dfresult.append(dffname)
            print(dffname.shape[0], end='\t')
            print(dfresult.shape[0])
            yichulifilelist.append(fname)
            cfpzysm.set('销售订单', '已处理文件清单', '%s' % '\n'.join(yichulifilelist))
            cfpzysm.write(open(inizysmpath, 'w', encoding='utf-8'))

    # dfresult.drop_duplicates(['单据编号', '日期', '订单编号', '客户名称', '业务人员', '订单金额', '部门'], inplace=True)
    print(f'除重前有{dfresult.shape[0]}条记录，', end='\t')
    dfresult.drop_duplicates(inplace=True)
    # descdb(dfresult)
    dateqiyu = min(dfresult['日期'])
    datezhiyu = max(dfresult['日期'])
    print(f'除重后有{dfresult.shape[0]}条记录；数据起于{dateqiyu}，止于{datezhiyu}')
    dfttt = dfresult.drop_duplicates()
    if cfpzysm.has_option('销售订单', '记录数'):
        jilucont = cfpzysm.getint('销售订单', '记录数')
    else:
        jilucont = 0
    if dfttt.shape[0] > jilucont:
        dfttt.to_sql(tablename_order, cnxp, index=False, if_exists='replace')
        cfpzysm.set('销售订单', '记录数', '%d' % dfttt.shape[0])
        cfpzysm.write(open(inizysmpath, 'w', encoding='utf-8'))
        log.info('增加有效销售订单数据%d条。' % (dfttt.shape[0] - jilucont))

    dfdanjusuoyin = dfresult.loc[:, ['日期', '订单编号', '客户名称', '业务人员', '订单金额', '部门']]
    # descdb(dfdanjusuoyin)
    dfdanjusuoyin.to_sql('tmptable', cnxp, index=True, if_exists='replace')
    cursor = cnxp.cursor()
    global dbpathquandan
    cursor.execute(f'attach database \'{dbpathquandan}\' as \'C\'')
    dfhanqu = pd.read_sql_query(
        'select tmptable.*,C.customer.往来单位编号 as 单位编号, substr(C.customer.往来单位编号, 1,2) as 区域,  '
        'substr(C.customer.往来单位编号, 12, 1) as 类型 from tmptable, C.customer '
        'where (tmptable.客户名称 = C.customer.往来单位) order by 日期 desc',
        cnxp, parse_dates=['日期'])
    # descdb(dfhanqu)
    dfout = dfhanqu.loc[:, ['日期', '订单编号', '区域', '类型', '单位编号', '客户名称', '业务人员', '订单金额', '部门']]
    # descdb(dfout)

    cnxp.close()

    return dfout


def dingdanxiaoshouyuedufenxi(dforder):
    dfall = dforder.loc[:, :]
    dfall['年月'] = dfall['日期'].apply(lambda x: x.strftime('%Y%m'))
    # descdb(dfall)
    zuijinchengjiaori = max(dfall['日期'])
    print(f'数据集最新日期：{zuijinchengjiaori}')
    if cfpdata.has_option('ordersaleguidquyu', '数据最新日期'):
        daterec = pd.to_datetime(cfpdata.get('ordersaleguidquyu', '数据最新日期'))
        if daterec >= zuijinchengjiaori:  # and False:
            log.info(f'订单数据集无更新，返回')
            return
    zuiyuanriqi = zuijinchengjiaori + datetime.timedelta(days=-365)
    zuiyuanyuechu = pd.to_datetime(f"{zuiyuanriqi.strftime('%Y-%m')}-01")
    print(zuiyuanyuechu)
    dfkehu = dfall.groupby(['单位编号', '客户名称', '区域', '类型'], as_index=False).count()
    dfkehu.drop_duplicates(['单位编号'], keep='last', inplace=True)
    dfkehuzhengli = dfkehu[['单位编号', '客户名称', '区域', '类型']]
    dfkehuzhengli.index = dfkehuzhengli['单位编号']
    del dfkehuzhengli['单位编号']
    # descdb(dfkehuzhengli)
    dsquyuzuixinriqi = pd.Series(dfall[dfall.日期 == zuijinchengjiaori].groupby('区域').count().index.values)
    # print(dsquyuzuixinriqi.values)
    dfyuetongji = dfall[dfall.日期 >= zuiyuanyuechu].groupby(by=['年月', '单位编号'], as_index=False, sort=True)['订单金额'].sum()
    dfyuetongji['订单金额'] = dfyuetongji['订单金额'].astype(int)
    # descdb(dfyuetongji)
    dfpivot = dfyuetongji.pivot(index='单位编号', values='订单金额', columns='年月')
    dfpivot = pd.DataFrame(dfpivot)
    cls = list(dfpivot.columns)
    # print(cls)
    # for cl in cls:
    #     dfpivot[cl] = dfpivot[cl].astype(int)
    dfpivot['单位编号'] = dfpivot.index
    dfpivot['客户名称'] = dfpivot['单位编号'].apply(lambda x: dfkehuzhengli.loc[x][0])
    dfpivot['区域'] = dfpivot['单位编号'].apply(lambda x: dfkehuzhengli.loc[x][1])
    dfpivot['类型'] = dfpivot['单位编号'].apply(lambda x: dfkehuzhengli.loc[x][2])
    clsnew = ['客户名称', '区域', '类型'] + cls
    # print(clsnew)
    dfpivot = dfpivot.loc[:, clsnew]
    dfpivot['成交月数'] = dfpivot.apply(lambda x: x[-13:].count(), axis=1)

    def shouciyuefen(xx):
        for i in range(len(xx)):
            # print(xx[i])
            if xx[i] > 0:
                return i
        else:
            return 12

    dfpivot['首次成交月份'] = dfpivot.apply(lambda x: clsnew[shouciyuefen(x[3:16]) + 3], axis=1)
    dfpivot['首交月数'] = dfpivot.apply(lambda x: 13 - shouciyuefen(x[3:16]), axis=1)

    def zuijinyuefen(xx):
        for i in range(len(xx) - 1, -1, -1):
            # print(f'{xx[i]}\t{i}')
            if xx[i] > 0:
                return i
        else:
            return 12

    dfpivot['最近成交月份'] = dfpivot.apply(lambda x: clsnew[zuijinyuefen(x[3:16]) + 3], axis=1)
    dfpivot['尾交月数'] = dfpivot.apply(lambda x: 13 - zuijinyuefen(x[3:16]), axis=1)
    dfpivot['有效月数'] = dfpivot['首交月数'] - dfpivot['尾交月数'] + 1
    dfpivot.fillna(0, inplace=True)
    dfpivot['年总金额'] = dfpivot.apply(lambda x: sum(x[3:16]), axis=1)
    # print(dfpivot.iloc[0, :])
    dfpivot['年总金额'] = dfpivot['年总金额'].astype(int)

    def youxiaoyuejun(jine, yueshu):
        if yueshu == 0:
            return 0
        else:
            return jine / yueshu

    dfpivot['有效月均'] = dfpivot.apply(lambda x: youxiaoyuejun(x.年总金额, x.有效月数), axis=1)
    dfpivot['有效月均'] = dfpivot['有效月均'].astype(int)
    dfpivot.sort_values(['区域', '有效月均'], ascending=[True, False], inplace=True)
    # descdb(dfpivot)
    # clsnewnew = clsnew + ['有效月均', '年总金额']
    # dfout = dfpivot[(dfpivot.有效月均 > 300) | (dfpivot.首交月数 < 5)]
    # print(dfout[dfout.首交月数 < 5])
    dfout = dfpivot
    # dfshow = dfout.loc[:, clsnewnew]
    dfshow = dfout.loc[:, :]
    dfshow.fillna(0, inplace=True)
    for cl in cls:
        dfshow[cl] = dfshow[cl].astype(int)
    # print(dfshow[dfshow.类型 == 'I'])
    # descdb(dfshow)

    cnx = lite.connect(dbpathworkplan)
    # dfshow.to_sql('tmptable', cnx, index=True, if_exists='replace')
    cursor = cnx.cursor()
    cursor.execute(f'attach database \'{dbpathquandan}\' as \'C\'')
    dfquyu = pd.read_sql('select * from C.quyu', cnx, index_col='index')
    dfquyu.drop_duplicates(['区域'], keep='first', inplace=True)
    dfquyu.index = dfquyu['区域']
    del dfquyu['区域']
    # descdb(dfquyu)
    dfleixing = pd.read_sql('select * from C.leixing', cnx, index_col='index')
    dfleixing.index = dfleixing['编码']
    del dfleixing['编码']
    # descdb(dfleixing)

    dfshow['区域名称'] = dfshow['区域'].apply(lambda x: dfquyu.loc[x][0])
    # print(dfshow[dfshow.类型 == '0'])
    dfshow['类型小类'] = dfshow['类型'].apply(lambda x: dfleixing.loc[x][0])
    dfshow['类型大类'] = dfshow['类型'].apply(lambda x: dfleixing.loc[x][1])

    # descdb(dfshow)
    cnx.close()

    dfzhongduan = dfshow[dfshow.类型大类 == '终端客户']
    # descdb(dfzhongduan)

    targetlist = list()
    dfzdall = dfzhongduan.loc[:, :]
    # descdb(dfzdall)

    notestore = get_notestore()
    quyuset = set(dsquyuzuixinriqi.apply(lambda x: dfquyu.loc[x][0]).values)
    print(quyuset)
    # quyuset = set(list(dfzdall['区域名称']))
    for qy in quyuset:
        dfslice = dfzdall[dfzdall.区域名称 == qy]
        dfslicesingle = dfslice.loc[:, :]
        del dfslicesingle['区域名称']
        # descdb(dfslicesingle)
        print(qy, end='\t')
        print(dfslicesingle.shape[0], end='\t')
        # descdb(dfslicesingle)
        if cfpdata.has_option('guidquyunb', qy):
            nbguid = cfpdata.get('guidquyunb', qy)
        else:
            try:
                notebook = Ttypes.Notebook()
                notebook.name = qy
                notebook = notestore.createNotebook(notebook)
                nbguid = notebook.guid
                cfpdata.set('guidquyunb', qy, nbguid)
                cfpdata.write(open(inidatanotefilepath, 'w', encoding='utf-8'))
            except Exception as eeeee:
                nbguid = None
                log.critical(f'创建《{qy}》笔记本时出现错误。{eeeee}')
        print(nbguid, end='\t')
        if cfpdata.has_option('ordersaleguidquyu', qy + 'guid'):
            ntguid = cfpdata.get('ordersaleguidquyu', qy + 'guid')
        else:
            try:
                note = Ttypes.Note()
                note.title = qy + "订单金额年度分析"
                note.content = '<?xml version="1.0" encoding="UTF-8"?>' \
                               '<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">'
                note.content += '<en-note>专营休闲美食</en-note>'
                note.notebookGuid = nbguid
                note = notestore.createNote(note)
                evernoteapijiayi()
                ntguid = note.guid
                cfpdata.set('ordersaleguidquyu', qy + 'guid', ntguid)
                cfpdata.write(open(inidatanotefilepath, 'w', encoding='utf-8'))
            except Exception as ee:
                ntguid = None
                log.critical(f'创建《{qy}订单金额年度分析》笔记时出现错误。{ee}')
        print(ntguid)
        target = list()
        target.append(qy)
        target.append(ntguid)
        target.append(dfslicesingle)
        targetlist.append(target)

    # descdb(dfshow[dfshow.index.str.find('XF') >= 0])
    lqzlist = [['连锁客户', '0e8ba322-4874-4627-a6de-13c69fffc88d'],
               ['渠道客户', '4AC03027-5929-415B-9711-0A8170263189'.lower()],
               ['直销客户', 'B0731D74-C268-417E-A8B7-7BE3EE590FAE'.lower()]
               ]
    for [mingmu, mmguid] in lqzlist:
        dfls = dfshow.loc[:, :]
        dfls = dfls[dfls.类型大类 == mingmu]
        # dfls = dfls[str(dfls.index)[7:9] == 'XF']
        del dfls['类型大类']
        dfls.sort_values(['有效月均'], ascending=False, inplace=True)
        target = list()
        target.append(mingmu)
        target.append(mmguid)
        target.append(dfls)
        targetlist.append(target)
    lslist = [['学府超市', 'XF', 'ce26a763-81cc-421f-8430-22dab21ba43e'],
              ['红生超市', 'HS', '1F0995DA-1DEC-4333-8EA6-8C85B54E2B71'.lower()],
              ['五分钟', 'WF', '41518B63-FF81-4719-BFE0-0E5BBFBC295A'.lower()]
              ]
    for [mingcheng, bianma, guid] in lslist:
        dfls = dfshow.loc[:, :]
        dfls = dfls[dfls.index.str.find(bianma) >= 0]
        del dfls['类型大类']
        if dfls.shape[0] == 0:
            log.info(f'连锁超市{mingcheng}没有数据记录，跳过')
            continue
        dfls.sort_values(['有效月均'], ascending=False, inplace=True)
        target = list()
        target.append(mingcheng)
        target.append(guid)
        target.append(dfls)
        targetlist.append(target)

    # print(targetlist)
    for [qy, ntguid, dfslicesingle] in targetlist:
        try:
            dfzdclnames = list(dfslicesingle.columns)
            # print(dfzdclnames)
            dfzdclnames3 = dfzdclnames[3:16]
            dfzdclnamesnew = [dfzdclnames[0]] + [dfzdclnames[-2]] + dfzdclnames3 + [dfzdclnames[23]] + [dfzdclnames[22]]
            # print(dfzdclnamesnew)

            stattitle = f'总客户：{dfslicesingle.shape[0]}，' \
                        f'在线客户（前三个月有成交记录）：{dfslicesingle[dfslicesingle.尾交月数 <= 4].shape[0]}，' \
                        f'本月成交客户：{dfslicesingle[dfslicesingle.尾交月数 == 1].shape[0]}'
            imglist2note(notestore, [], ntguid, qy + '订单金额年度分析',
                         tablehtml2evernote(dftotal2top(dfslicesingle.loc[:, dfzdclnamesnew]), stattitle,
                                            withindex=False))
            cfpdata.set('ordersaleguidquyu', qy + 'count', f'{dfslicesingle.shape[0]}')
            cfpdata.write(open(inidatanotefilepath, 'w', encoding='utf-8'))
            log.info(f'{qy}数据项目成功更新')
        except Exception as eee:
            log.critical(f'《{qy}订单金额年度分析》笔记更新时出现错误。{eee}')
        # print(dfslicesingle.shape[0])
    else:
        cfpdata.set('ordersaleguidquyu', '数据最新日期', f'{zuijinchengjiaori}')
        cfpdata.write(open(inidatanotefilepath, 'w', encoding='utf-8'))


def showorderstat():
    # xlsfile = 'data\\work\\销售订单\\销售订单20180606__20180607034848_480667.xls'
    # dforder = chulixls_order(xlsfile)
    pathor = dirmainpath / 'data' / 'work' / '销售订单'
    dforder = chulidataindir_order(pathor)
    dingdanxiaoshouyuedufenxi(dforder)
    dforder = dforder.loc[:, ['日期', '订单编号', '区域', '类型', '客户名称', '业务人员', '订单金额']]
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
                nbody = '<?xml version="1.0" encoding="UTF-8"?>'
                nbody += '<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">'
                nbody += '<en-note>%s</en-note>' % plannote.title
                plannote.content = nbody
                global workplannotebookguid
                plannote.notebookGuid = workplannotebookguid
                global cfp
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
            if zuixinriqi <= pd.to_datetime(ordertoday):  # and False:
                continue
        dfperson = dforderzuixinriqi[dforderzuixinriqi.业务人员 == person]
        dfpersonsum = dfperson.groupby('业务人员').sum()['订单金额']
        del dfperson['业务人员']
        del dfperson['日期']
        print(person, end='\t')
        print(dfpersonsum[0], end='\t')
        personguid = cfpzysm.get(notestr + 'guid', person)
        print(personguid)
        neirong = tablehtml2evernote(dftotal2top(dfperson), f'{orderdatestr}{notestr}——{person}', withindex=False)
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
    dfsales = pd.DataFrame(dforder[dforder.日期 >= yuechuriqi])
    dfsales = dfsales.groupby(['区域', '类型', '客户名称', '业务人员'], as_index=False).sum()
    dfsales.sort_values(['区域', '订单金额'], inplace=True)
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
                nbody = '<?xml version="1.0" encoding="UTF-8"?>'
                nbody += '<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">'
                nbody += '<en-note>%s</en-note>' % plannote.title
                plannote.content = nbody
                plannote.notebookGuid = workplannotebookguid
                # cfp, cfppath = getcfp('everwork')
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
            if zuixinriqi <= pd.to_datetime(ordertoday):  # and False:
                continue
        dfperson = dfsales[dfsales.业务人员 == person]
        dfpersonsum = dfperson['订单金额'].sum()
        del dfperson['业务人员']
        print(person, end='\t')
        print(dfpersonsum, end='\t')
        personguid = cfpzysm.get(notestr, person)
        print(personguid)
        neirong = tablehtml2evernote(dftotal2top(dfperson), f'{orderdatestr[:-3]}{notestr}', withindex=False)
        # print(neirong)
        try:
            notestore = get_notestore()
            imglist2note(notestore, [], personguid, '%s——%s（%s）' % (notestr, person, orderdatestr[:-3]), neirong)
            cfpzysm.set(notestr, person + '最新订单日期', '%s' % orderdatestr)
            cfpzysm.write(open(inizysmpath, 'w', encoding='utf-8'))
        except Exception as eeee:
            log.critical('更新笔记%s——%s（%s）时出现严重错误。%s' % (notestr, person, orderdatestr, str(eeee)))
    else:
        log.info('下列人员的销售订单金额月度分析正常处置完毕：%s' % persons)


def showorderstat2note(jiangemiao):
    global workplannotebookguid
    workplannotebookguid = '2c8e97b5-421f-461c-8e35-0f0b1a33e91c'
    try:
        showorderstat()
    except Exception as ee:
        log.critical('处理订单核对统计笔记时出现错误。%s' % str(ee))
        raise ee

    global timer_showorderstat
    timer_showorderstat = Timer(jiangemiao, showorderstat2note, [jiangemiao])
    timer_showorderstat.start()


if __name__ == '__main__':
    log.info(f'测试文件\t{__file__}')
    chulixls_order('订单明细20180614.xls.xls')
    print('Done.测试完毕。')
