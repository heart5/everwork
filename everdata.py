# encoding:utf-8
# 整理并导入原始数据
from imp4nb import *


def saledetails2db(filenamenoext):
    # 2017.8.29-2017.9.30职员销售明细表.xls
    # 2017.10.1-2017.10.10职员销售明细表.xls
    # 2017.10.11-2017.10.19职员销售明细表.xls
    # 2017.10.20-2017.10.23职员销售明细表.xlsx
    # 2017.10.24-2017.11.26职员销售明细表.xls
    # 2017.11.27-2017.11.30职员销售明细表.xls
    # 2017.12.1-2017.12.8职员销售明细表.xls
    # 2017.12.9-2017.12.16职员销售明细表.xls
    # 2017.12.17-2017.12.26职员销售明细表.xls
    df = pd.read_excel('data\\%s.xls' % filenamenoext, sheetname='%s' % filenamenoext, index_col=0, parse_dates=True)
    log.info('读取%s')
    # print(list(df.columns))  # ['日期', '单据编号', '摘要', '单据类型', '备注', '商品备注', '商品编号', '商品全名', '规格', '型号', '产地', '单位', '数量', '单价', '金额', '含税单价', '价税合计', '成本金额', '毛利', '毛利率', '单位全名', '仓库全名', '部门全名']
    totalin = [df.loc[df.index.max()]['数量'], df.loc[df.index.max()]['金额']]  # 从最后一行获取数量合计和金额合计，以备比较
    df['职员名称'] = None
    df = df.loc[:, ['日期', '单据编号', '单据类型', '职员名称', '摘要', '备注', '商品备注', '商品编号', '商品全名',
                    '单价', '单位', '数量', '金额', '单位全名', '仓库全名', '部门全名']]
    df['日期'] = pd.to_datetime(df['日期'])
    df['备注'] = df['备注'].astype(object)
    dfdel = df[
        (df.单位全名.isnull().values == True) & ((df.单据编号.isnull().values == True) | (df.单据编号 == '小计') | (df.单据编号 == '合计'))]
    hangdel = list(dfdel.index)
    df1 = df.drop(hangdel)  # 丢掉小计和合计行，另起DataFrame
    dfzhiyuan = df1[df1.单位全名.isnull().values == True]  # 提取出职员名称行号
    zyhang = list(dfzhiyuan.index)
    zyming = list(dfzhiyuan['单据编号'])  # 职员名称

    # 每次填充df到最后一行，依次滚动更新之
    for i in range(len(zyhang)):
        df.loc[zyhang[i]:, '职员名称'] = zyming[i]

    # 丢掉职员名称行，留下纯数据
    dfdel = df[df.单位全名.isnull().values == True]
    # print(dfdel[['日期', '单据编号', '数量', '金额']])
    hangdel = list(dfdel.index)
    # print(hangdel)
    dfout = df.drop(hangdel)
    dfout.index = range(len(dfout))
    log.info('共有%d条有效记录' % len(dfout))

    # 读取大数据的起止日期，不交叉、不是前置则可能是合法数据，二次检查后放行
    cnx = lite.connect('data\\quandan.db')

    if ((totalin[0] == dfout.sum()['数量']) & (totalin[1] == dfout.sum()['金额'])):
        dfall = pd.read_sql_query('select 日期, sum(金额) as 销售额 from xiaoshoumingxi group by 日期 order by 日期', cnx,
                                  parse_dates=['日期'])
        datestr4data = '【待插入S：%s，E：%s】【目标数据S：%s，E：%s】' % (
        dfout['日期'].min(), dfout['日期'].max(), dfall['日期'].min(), dfall['日期'].max())
        if ((dfall['日期'].max() >= dfout['日期'].min()) or (dfall['日期'].min() >= dfout['日期'].max())):
            log.warning('时间交叉了，请检查数据！%s' % datestr4data)
            exit(2)
        else:
            print('请仔细检查！%s' % datestr4data)
            print('如果确保无误，请放行下面两行代码')
        # dfout.to_sql(name='xiaoshoumingxi', con=cnx, if_exists='append', chunksize=10000)
        # log.info('成功从数据文件《%s》中添加%d条记录到总数据表中。' %(filenamenotext, len(dfout)))
    else:
        log.warning('对读入文件《%s》的数据整理有误！总数量和总金额对不上！' % filenamenoext)

    cnx.close()


def customerweihu2systable():
    '''
    处理客户档案维护记录，规整（填充日期、取有效数据集、板块排序、拆分内容后取有效信息并填充、抽取改编码客户、抽出重复录入纪录）后输出，对改编码客户进行条码更新，手工进入《系统表》
    :return:
    '''

    writer = pd.ExcelWriter('data\\结果输出.xlsx')

    df = pd.read_csv('data\\kehudanganweihu.txt', sep=']', header=None, names=['日期', '内容'], na_filter=True,
                     skip_blank_lines=True, skipinitialspace=True)
    # print(df)
    df.to_excel(writer, sheet_name='原始数据整理', freeze_panes={1, 2})
    dfriqi = df[df['内容'].isnull().values == True]  # 找到日期行，获取日期、索引（即行号）
    # print(dfriqi)
    # print(dfriqi.index.values)

    dfout = df
    for i in list(dfriqi.index):
        dfout.loc[i:, ['日期']] = dfriqi.loc[i, '日期']  # 滚动填充日期

    dfout = dfout[df['内容'].isnull().values == False]  # 获取填充日期后的有效数据
    print(len(dfout))

    # print(dfout.dtypes)
    # print(dfout.columns)

    # 转换日期格式，从形如2017年8月/10日转换成标准日期
    # 传入参数为Series
    def riqi2std(dsin):
        ds = dsin
        itempattern = re.compile('\s*(?P<year>\d{4})\s*年(?P<month>\d+)月/?(?P<day>\d+)日')
        for i in list(ds.index):
            # print(str(i)+'\t'+dsin[i],end='\t\t')
            riqiokay = None  # 置空
            for j in re.findall(itempattern, ds[i]):  # 形如('2017','8','10')
                # print(j)
                riqiokay = pd.to_datetime(str(j[0]) + '-' + str(j[1]) + '-' + str(j[2]))
            ds[i] = riqiokay

        return ds

    dfout['日期'] = riqi2std(dfout['日期'])
    dfout.loc[:, '索引'] = dfout.index
    dfout.to_excel(writer, sheet_name='档案整理', freeze_panes={1, 2})
    dfoutsort = dfout.sort_values(by=['日期', '索引'], ascending=True)
    dfoutsort.index = range(len(dfoutsort))  # 重新索引，固化排序
    # dfoutsort.info()
    # print(dfoutsort)
    # print(dfoutsort.head(3))

    dfoutsort['往来单位'] = None
    dfoutsort['往来单位编号'] = None
    dfoutsort['动作'] = None
    dfoutsort['往来单位老'] = None
    dfoutsort['往来单位编号老'] = None
    # dfoutsort.columns = list(list(dfoutsort.columns)+['n1','n2','n3'])
    lsbianma = list()  # 改编码的需要单独处理，索引存入list
    for i in list(dfoutsort.index):
        # 22100430030SXXD/天富（后湖五路） 13871189017 /改成/天富（后湖五路） 13018016563/改店名
        nrsp = ((dfoutsort['内容'])[i]).split('/')
        # print(nrsp)
        if len(nrsp) == 3:
            # ['02300320000SXXD', '小七便利店 18636004123', '新店']
            dfoutsort.loc[i, ['往来单位编号', '往来单位', '动作']] = [nrsp[0].strip(), nrsp[1].strip(), nrsp[2].strip()]
        elif len(nrsp) == 5:
            if '编码' in (nrsp[4].strip()):
                lsbianma.append(i)
                # ['05200100000XXXD', '同丰泰副食 86828538', '改成', '05200100000PXXD', '改编码']
                dfoutsort.loc[i, ['往来单位编号', '往来单位', '动作', '往来单位编号老']] = [nrsp[3].strip(), nrsp[1].strip(),
                                                                         nrsp[4].strip(), nrsp[0].strip()]
                # print(dfoutsort.loc[i])
            else:
                # ['22200680030SXXD', '新北门超市 82310216', '改成', '雅堂小超新北门超市 82310216', '改店名']
                dfoutsort.loc[i, ['往来单位编号', '往来单位', '动作', '往来单位老']] = [nrsp[0].strip(), nrsp[3].strip(),
                                                                       nrsp[4].strip(), nrsp[1].strip()]
    # dfoutsort.info()
    # print(dfoutsort)
    # print(dfoutsort.head(3))
    print(lsbianma)
    dfoutsort.to_excel(writer, sheet_name='档案整理排序', freeze_panes={1, 2})
    dfbm = dfoutsort.loc[lsbianma]
    dfbm.to_excel(writer, sheet_name='编码调整客户', freeze_panes={1, 2})

    lszc = list(set(dfoutsort.index) - set(lsbianma))  # 去掉改编码的纪录
    dfzh = dfoutsort.loc[lszc, ['往来单位', '往来单位编号']]
    # dfzh.info()

    cnx = lite.connect('data\\quandan.db')
    dfys = pd.read_excel('data\\系统表.xlsx', sheetname='客户档案')
    # dfys.info()

    dfzh = pd.concat([dfys, dfzh])
    # dfzh.info()
    dfzh.to_excel(writer, sheet_name='合并客户全集', freeze_panes={1, 2})
    dfzh.index = range(len(dfzh))

    dddd = dfzh.duplicated(['往来单位', '往来单位编号'])
    ffff = dddd[dddd == True]
    dfzhcm = dfzh.loc[list(ffff.index)]
    dfzhcm.to_excel(writer, sheet_name='重复录入客户', freeze_panes={1, 2})
    dfzh.info()
    dfzh = dfzh.drop_duplicates(['往来单位', '往来单位编号'])  # 去重
    dfzh.info()
    dfzh = dfzh.drop_duplicates('往来单位')  # 去重
    dfzh.info()

    for i in list(lsbianma):
        print(dfoutsort.loc[i]['往来单位'] + '\t' + dfoutsort.loc[i]['往来单位编号'], end='\t')
        idx = list(dfzh[dfzh.往来单位 == dfoutsort.loc[i]['往来单位']].index)
        print(idx, end='\t')
        print(dfzh.loc[idx, '往来单位编号'].values, end='\t')
        dfzh.loc[idx, '往来单位编号'] = dfoutsort.loc[i, '往来单位编号']
        print(dfzh.loc[idx, '往来单位编号'].values)

    dfzh = dfzh[['往来单位', '往来单位编号', '地址', '助记码', '传真', '联系电话', '联系人', '停用']]
    dfzh.to_excel(writer, sheet_name='整理输出', freeze_panes={1, 2})

    writer.save()
    writer.close()
    pass


filenamenoext = '2018.1.7-2018.1.12职员销售明细表.xls'
saledetails2db(filenamenoext)

# customerweihu2systable()
