# encoding:utf-8
# %%
"""
DataFrame功能应用函数库
"""
import os
import evernote.edam.type.ttypes as ttypes
import numpy as np
import pandas as pd
import sqlite3 as lite
import time
import datetime
from configparser import ConfigParser
# from matplotlib.ticker import FuncFormatter
from pandas.tseries.offsets import *
from numpy import float64, int64, dtype
from pylab import plt, FuncFormatter
from PIL import Image, ImageFont, ImageDraw
# import matplotlib.pyplot as plt

import pathmagic
with pathmagic.context():
    from func.evernttest import evernoteapijiayi, makenote, getinivaluefromnote
    from func.first import dbpathworkplan, dbpathquandan, dirmainpath, ywananchor, touchfilepath2depth
    from func.logme import log
    from func.nettools import trycounttimes2
    from func.wrapfuncs import timethis
#    from func.profilerlm import lpt_wrapper

# print(f"{__file__} is loading now...")

# %%
# plot中显示中文
# mpl.rcParams['font.sans-serif'] = ['SimHei']
# mpl.rcParams['axes.unicode_minus'] = False

# %%
def db2img(inputdf: pd.DataFrame, title=None, showincell=True, fontsize=12, dpi=300, debug=False):
    dflines = inputdf.to_string(justify='left', show_dimensions=True).split('\n')
    
    return lststr2img(dflines, title=title, dpi=dpi, showincell=showincell, fontsize=fontsize, debug=debug)


# %%
def lststr2img(inputcontent, fontpath=dirmainpath / 'font' / 'msyh.ttf', title=None, showincell=False, fontsize=12, dpi=300, debug=False) :
    if type(inputcontent) == str:
        dflines = inputcontent.split('\n')
    elif type(inputcontent) == list:
        dflines = inputcontent
    else:
        logstr = f"传入参数类型为：\t{type(inputcontent)}，既不是str也不是list，暂不做处理返回None"
        log.critical(logstr)
        return 
    
    rows = len(dflines)
    collenmax = max([len(x) for x in dflines])
    print(f"行数和行最长长度（字符）：\t{(rows, collenmax)}")
    font = ImageFont.truetype(str(fontpath), fontsize)
    print(str(fontpath))
    colwidthmax = max([font.getsize(x)[0] for x in dflines])
    rowwidth = max([font.getsize(x)[1] for x in dflines])
    print(f"行高度、所有行总高度和所有列宽度（像素）：\t{(rowwidth, rowwidth * len(dflines), colwidthmax)}")

    print(f"画布宽高（像素）：\t{(colwidthmax, rowwidth * len(dflines))}")
    im = Image.new("RGB", (colwidthmax, rowwidth * len(dflines)), (255, 255, 255))
    dr = ImageDraw.Draw(im)

    i = 0
    for line in dflines:
        dr.text((0, 0 + rowwidth * i), line, font=font, fill="#000000")
        i += 1

    if not debug:
        if (notedpi := getinivaluefromnote('webchat', 'imgdpi')):
            dpi = notedpi
        
    # im.show()
    figdefaultdpi = plt.rcParams.get('figure.dpi')
    figwinchs = round(colwidthmax * (dpi / figdefaultdpi) / figdefaultdpi / 10, 3)
    fighinchs = round(rowwidth * len(dflines) * (dpi / figdefaultdpi) / figdefaultdpi / 10, 3)
    print(f"输出图片的画布宽高（英寸）：\t{(figwinchs, fighinchs)}")
    plt.figure(figsize=(figwinchs, fighinchs), dpi=dpi)
    plt.axis('off') 
    # font = ImageFont.truetype("../msyh.ttf", 12)
    if title:
        plt.title(title)
    plt.imshow(im)
    imgtmppath = dirmainpath / 'img'/ 'dbimgtmp.png'
    plt.axis('off') 
    plt.savefig(imgtmppath)
    if not showincell:
        plt.close()
    
    return imgtmppath


# 显示DataFrame或Series的轮廓信息
# df，DataFrame或Series
def descdb(df):
    print(df.shape[0])
    # print(df.head(5))
    print(df.head(10))
    print(df.dtypes)
    if type(df) == pd.DataFrame:
        print(df.columns)
    print(df.describe())


# 显示SQlite数据库的各种信息
# cnx，数据库连接
def desclitedb(cnx):
    cur = cnx.cursor()
    result = cur.execute("select * from sqlite_master")
    for ii in result.fetchall():
        print(str(ii) + '\n')

    result = cur.execute("select name from sqlite_master where type = 'table' order by name")
    table_name_list = [tuple1[0] for tuple1 in result.fetchall()]
    print(table_name_list)
    # for table1 in table_name_list:
        # #        result = cur.execute("PRAGMA table_info(%s)" % table)
        # #        for jj in result.fetchall():
        # #            print(jj,end='\t')
        # print("%s" % table1, end='\t')
        # result = cur.execute("select * from %s" % table1)
        # print(len(result.fetchall()), end='\t')
        # # print(cur.description)
        # col_name_list = [tuple1[0] for tuple1 in cur.description]
        # print(col_name_list)


def dftotal2top(df: pd.DataFrame):
    """
    给DataFrame增加汇总行，并将汇总行置顶
    :param df: pd.DataFrame
    :return: pd.DataFrame
    """
    # print(df.dtypes)
    if df.shape[0] == 0:  # 传入DataFrame为空则直接返回
        return
    dfslicesingle = df.loc[:, :]
    # print(dfslicesingle.dtypes)
    numtypelist = [float, float64, int, int64]
    # dfslicesingle.loc['汇总'] = dfslicesingle.apply(lambda x: x.sum() if dtype(x) in numtypelist else None)
    # print(dfslicesingle)
    dfslicesingle.loc['汇总'] = dfslicesingle.apply(lambda x: x.sum() if x.name.find('日期') < 0 else None)
    # print(list(dfslicesingle.columns))
    # print(list(dfslicesingle.loc['汇总']))
    firstcltotal = False
    hasjun = False
    cls = dfslicesingle.columns
    # print(df.dtypes)
    for cl in cls:
        # print(cl)
        if cl.find('日期') >= 0:
            continue
        if cl.find('有效月均') >= 0:
            hasjun = True
        if dtype(dfslicesingle[cl]) in numtypelist:
            # dfslicesingle.loc['汇总', cl] = dfslicesingle[cl].sum()
            continue
        else:
            if firstcltotal:
                dfslicesingle.loc['汇总', cl] = len(set(list(dfslicesingle[cl]))) - 1
            else:
                firstcltotal = True
                dfslicesingle.loc['汇总', cl] = '汇总'
    # print(list(dfslicesingle.loc['汇总']))
    if hasjun:
        first = start = end = -1
        for i in range(len(cls)):
            if (cls[i].find('有效月均') >= 0) or (cls[i].find('总金额') >= 0):
                break
            if dtype(dfslicesingle[cls[i]]) in numtypelist:
                if first < 0:
                    first = i
                if dfslicesingle.loc['汇总', cls[i]] > 0:
                    if start < 0:
                        start = i
                    end = i
        # print(f'{first}\t{start}\t{end}')
        # print(list(dfslicesingle.loc['汇总'])[start:(end + 1)])
        # 除数出现了为零的可能，try包围之。所有错误，皆为逻辑。
        # 此try包围在逻辑问题解决后有冗余之嫌，但工作需要，正常运转为第一要务，姑且存之。
        try:
            dfslicesingle.loc['汇总', '有效月均'] = int(sum(list(dfslicesingle.loc['汇总'])[start:(end + 1)]) / (end - start + 1))
        except Exception as e:
            print(dfslicesingle)
            print(f"{start}\t{end}\t{first}")
            print(f"{e}")
            log.critical(f"给DataFrame添加汇总行时出现运算错误.\t有效数据起始位：{start},结束位：{end},首位：{first}.\t{e}")
            raise
    idxnew = list(dfslicesingle.index)
    idxnew = [idxnew[-1]] + idxnew[:-1]
    dfout = dfslicesingle.loc[idxnew]
    return dfout


@timethis
#@lpt_wrapper()
def isworkday(dlist: list, person: str = '全体', fromthen=False):
    if fromthen and (len(dlist) == 1):
        dlist = pd.date_range(dlist[0], datetime.datetime.today(), freq='D')
    cnxpi = lite.connect(dbpathworkplan)
    dfholiday = pd.read_sql('select distinct * from holiday', cnxpi, index_col='date', parse_dates=['date'])
    # del dfholiday['index']
    # print(dfholiday)
    dfleave = pd.read_sql('select distinct date,mingmu,xingzhi,tianshu from leave', cnxpi, parse_dates=['date'])
    # print(dfleave)
    cnxpi.close()
    resultlist = list()
    for dt in dlist:
        item = list()
        dtdate = pd.to_datetime(dt)
        item.append(dtdate)
        if person != '全体':
            item.append(person)
            dfperson = dfleave[dfleave.mingmu == person]
            dfperson.index = dfperson['date']
            dttuple = tuple(dfperson[dfperson.xingzhi == '上班'].index)
            if dtdate in dttuple:
                item.append(True)
                item.append('上班')
                item.append(dfperson.loc[dtdate, ['tianshu']][0])
                resultlist.append(item)
                continue
            if dtdate in tuple(dfperson[dfperson.xingzhi != '上班'].index):
                item.append(False)
                item.append(dfperson.loc[dtdate, ['xingzhi']][0])
                item.append(dfperson.loc[dtdate, ['tianshu']][0])
                resultlist.append(item)
                tianshu = dfperson.loc[dtdate, ['tianshu']][0]
                # print(item, resultlist)
                if tianshu < 1:
                    itemnew = list()
                    itemnew.append(dtdate)
                    itemnew.append(person)
                    itemnew.append(True)
                    itemnew.append('上班')
                    itemnew.append(1 - tianshu)
                    # item[2] = True
                    # item[3] = '上班'
                    # item[4] = 1-tianshu
                    resultlist.append(itemnew)
                    # print(item, resultlist)
                continue
        else:
            item.append('全体')
        if dtdate in tuple(dfholiday[dfholiday.mingmu == '上班'].index):
            item.append(True)
            item.append('上班')
            item.append(dfholiday.loc[dtdate, ['tianshu']][0])
            resultlist.append(item)
            continue
        if dtdate in tuple(dfholiday[dfholiday.mingmu != '上班'].index):
            item.append(False)
            item.append(dfholiday.loc[dtdate, ['mingmu']][0])
            item.append(dfholiday.loc[dtdate, ['tianshu']][0])
            resultlist.append(item)
            continue
        if int(dtdate.strftime('%w')) == 0:
            item.append(False)
            item.append('周日')
            item.append(1)
            resultlist.append(item)
            continue
        item.append(True)
        item.append('上班')
        item.append(1)
        resultlist.append(item)
    dfout = pd.DataFrame(resultlist, columns=['date', 'name', 'work', 'xingzhi', 'tianshu'])
    dfout.sort_values(['date'], ascending=[False], inplace=True)
    # print(dfout)
    return dfout


def gengxinfou(filename, conn, tablename='fileread'):
    try:
        create_tb_cmd = "CREATE TABLE IF NOT EXISTS %s " \
                        "('文件名' TEXT," \
                        "'绝对路径' TEXT, " \
                        "'修改时间' TIMESTAMP," \
                        "'设备编号' INTEGER," \
                        "'文件大小' INTEGER," \
                        "'登录时间' TIMESTAMP); " % tablename
        conn.execute(create_tb_cmd)
    except Exception as eee:
        log.critical("创建数据表%s失败！" % tablename)
        raise eee

    fna = os.path.abspath(filename)
    fn = os.path.basename(fna)
    fstat = os.stat(filename)
    # print(fn)

    # sql = "delete from %s where 文件大小 > 0" %tablename
    # print(sql)
    # result = conn.cursor().execute(sql)
    # conn.commit()
    # print(('共删除了'+str(result.fetchone())[0])+'条记录')

    c = conn.cursor()
    sql = "select count(*) from %s where 文件名 = \'%s\'" % (tablename, fn)
    result = c.execute(sql)
    # print(result.lastrowid)
    # conn.commit()
    fncount = (result.fetchone())[0]
    if fncount == 0:
        print("文件《" + fn + "》无记录，录入信息！\t", end='\t')
        c.execute("insert into %s values(?,?,?,?,?,?)"
                  % tablename, (fn, fna,
                                time.strftime('%Y-%m-%d %H:%M:%S',
                                              time.localtime(fstat.st_mtime)),
                                str(fstat.st_dev), str(fstat.st_size),
                                time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())))
        print('添加成功。')
        log.info('文件《%s》无记录，录入信息。' % fn)
        rt = True
    else:
        print("文件《" + fn + "》已有 " + str(fncount) + " 条记录，看是否最新？\t", end='\t')
        sql = "select max(修改时间) as xg from %s where 文件名 = \'%s\'" % (tablename, fn)
        result = c.execute(sql)
        if time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(fstat.st_mtime)) > (result.fetchone())[0]:
            c.execute("insert into %s values(?,?,?,?,?,?)" % tablename, (
                fn, fna, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(fstat.st_mtime)), str(fstat.st_dev),
                str(fstat.st_size), time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())))
            print('更新成功！')
            log.info('文件《%s》已有%d条记录，有新文件，更新之。' % (fn, fncount))
            rt = True
        else:
            print('无需更新。')
            rt = False
    conn.commit()

    return rt


def dataokay(cnx):
    # global dirmainpath
    pathxitongbiaoxls = str(dirmainpath / 'data' / '系统表.xlsx')
    if gengxinfou(pathxitongbiaoxls, cnx, 'fileread'):  # or True:
        df = pd.read_excel(pathxitongbiaoxls, sheet_name='区域')
        df['区域'] = pd.DataFrame(df['区域']).apply(lambda r: '%02d' % r, axis=1)
        # print(df)
        df = df.loc[:, ['区域', '区域名称', '分部']]
        df.to_sql(name='quyu', con=cnx, if_exists='replace')

        df = pd.read_excel(pathxitongbiaoxls, sheet_name='小区')
        df['小区'] = pd.DataFrame(df['小区']).apply(lambda r: '%03d' % r, axis=1)
        # print(df)
        df.to_sql(name='xiaoqu', con=cnx, if_exists='replace')

        df = pd.read_excel(pathxitongbiaoxls, sheet_name='终端类型')
        # print(df)
        df.to_sql(name='leixing', con=cnx, if_exists='replace')

        df = pd.read_excel(pathxitongbiaoxls, sheet_name='产品档案', )
        # print(df)
        df.to_sql(name='product', con=cnx, if_exists='replace')

        df = pd.read_excel(pathxitongbiaoxls, sheet_name='客户档案')
        df = df.loc[:, ['往来单位', '往来单位编号', '地址']]
        # print(df)
        df.to_sql(name='customer', con=cnx, if_exists='replace')

    pathquandantongjixls = str(dirmainpath / 'data' / '2018年全单统计管理.xlsm')
    if gengxinfou(pathquandantongjixls, cnx, 'fileread'):  # or True:
        df = pd.read_excel(pathquandantongjixls, shee_tname='全单统计管理', na_values=[0])
        # descdb(df)
        df = df.loc[:, ['订单日期', '单号', '配货人', '配货准确', '业务主管', '终端编码', '终端名称', '积欠', '送货金额',
                        '实收金额', '收款方式', '优惠', '退货金额', '客户拒收', '无货金额', '少配金额', '配错未要',
                        '送达日期', '车辆', '送货人', '收款日期', '收款人', '拒收品项', '少配明细']]
        df_dh = df.pop('单号')
        df.insert(1, '订单编号', df_dh)
        df['订单编号'] = df['订单编号'].apply(lambda x: str.strip(x) if type(x) == str else x)
        df['配货人'] = df['配货人'].apply(lambda x: str.strip(x) if type(x) == str else x)
        df['业务主管'] = df['业务主管'].apply(lambda x: str.strip(x) if type(x) == str else x)
        df['终端编码'] = df['终端编码'].apply(lambda x: str.strip(x) if type(x) == str else x)
        df['收款方式'] = df['收款方式'].apply(lambda x: str.strip(x) if type(x) == str else x)
        df['车辆'] = df['车辆'].apply(lambda x: str.strip(x) if type(x) == str else x)
        df['送货人'] = df['送货人'].apply(lambda x: str.strip(x) if type(x) == str else x)
        df['收款人'] = df['收款人'].apply(lambda x: str.strip(x) if type(x) == str else x)
        df['拒收品项'] = df['拒收品项'].apply(lambda x: str.strip(x) if type(x) == str else x)
        df['少配明细'] = df['少配明细'].apply(lambda x: str.strip(x) if type(x) == str else x)
        # df['无货金额'] = df['无货金额'].astype(int)
        # df = df.apply(lambda x:str.strip(x) if type(x) == str else x)
        df.to_sql(name='quandan', con=cnx, if_exists='replace', chunksize=100000)

    pathjiaqitxt = str(dirmainpath / 'data' / 'jiaqi.txt')
    if gengxinfou(pathjiaqitxt, cnx, 'fileread'):
        df = pd.read_csv(pathjiaqitxt, sep=',', header=None)
        dfjiaqi = []
        for ii in df[0]:
            slist = ii.split('，')
            slist[0] = pd.to_datetime(slist[0])
            slist[2] = int(slist[2])
            dfjiaqi.append(slist)
        df = pd.DataFrame(dfjiaqi)
        df.sort_values(by=[0], ascending=[1], inplace=True)
        df.columns = ['日期', '假休', '天数']
        # df.index = df['日期']
        # descdb(df)
        sql_df = df.loc[:, df.columns]
        df.to_sql(name='jiaqi', con=cnx, schema=sql_df, if_exists='replace')


def biaozhukedu(dfc, weibiao):
    if weibiao == dfc.index.max():
        kedus = [dfc.loc[weibiao]]
    else:
        kedus = [dfc.loc[weibiao], dfc.loc[dfc.index.max()]]
    # print(type(kedus[0]))
    for ii in range(len(kedus)):
        kedu = kedus[ii]
        if (len(dfc.index)) > 12:
            idx = kedu.name
        else:
            idx = list(dfc.index).index(kedu.name)
        if not np.isnan(kedu.iloc[0]):
            plt.plot([idx, idx], [0, kedu.iloc[0]], 'c--')
            plt.annotate(str(kedu.name), xy=(idx, 0), xycoords='data', xytext=(-20, -20),
                         textcoords='offset points', color='r',
                         arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"))
        for i in range(len(kedu)):
            if np.isnan(kedu.iloc[i]):
                # print(kedu.iloc[i])
                # print(type(kedu.iloc[i]))
                continue
            plt.scatter([idx, ], [kedu.iloc[i]], 50, color='Wheat')
            # global ywananchor
            if kedu.map(lambda x: abs(x)).max() >= ywananchor:
                kedubiaozhi = "%.1f万" % (kedu.iloc[i] / 10000)
                plt.gca().yaxis.set_major_formatter(
                    FuncFormatter(lambda x, pos: "%d万" % int(x / 10000)))  # 纵轴主刻度文本用y_formatter函数计算
            else:
                kedubiaozhi = "%d" % kedu.iloc[i]
            fontsize = 8
            if (i % 2) == 0:
                zhengfu = -1
            else:
                zhengfu = 0.4
            plt.annotate(kedubiaozhi, xy=(idx, kedu.iloc[i]), xycoords='data',
                         xytext=(
                             len(kedubiaozhi) * fontsize * zhengfu,
                             int(len(kedubiaozhi) * fontsize * (-1) * zhengfu / 2)),
                         textcoords='offset points', fontsize=fontsize,
                         arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2", color='Purple'))


def readinisection2df(cfpp: ConfigParser, section: object, biaoti: object):
    """
    读取ini中的section，返回df
    :param cfpp:
    :param section:
    :param biaoti:
    :return: ['guid','title']，index是fenbu，title是fenbu+标题
    """
    namelist = cfpp.options(section)
    valuelist = []
    for nameitem in namelist:
        valueitem = cfpp.get(section, nameitem)
        valuelist.append(valueitem)
    df = pd.DataFrame(valuelist, index=namelist)
    df.columns = ['guid']
    df['fenbu'] = df.index
    df['title'] = df['fenbu'].map(lambda x: x + biaoti)
    del df['fenbu']
    return df


def chutuyuezhexian(ds, riqienddate, xiangmu, cum=False, quyu='', leixing='', pinpai='', nianshu=3,
                    imgpath=dirmainpath / 'img'):
    """
    月度（全年，自然年度）累积对比图，自最早日期起，默认3年
    :param ds: 数据表，必须用DateTime做index
    :param riqienddate: 数据记录的最近日期，可以是DateTIme的各种形式，只要pd能识别成功，形如2017-10-06
    :param xiangmu: 主题，画图时写入标题
    :param cum:
    :param quyu: 销售区域或区域聚合（分部）
    :param leixing: 终端类型
    :param pinpai:
    :param nianshu: 用来对比的年份数，从当前年份向回数
    :param imgpath: 图片存储路径
    :return:
    """
    # print(df.tail(10))
    # monthcur = riqienddate + MonthBegin(-1) # 2017-10-01
    nianshushiji = ds.index.max().year - ds.index.min().year + 1
    if nianshushiji > nianshu:
        nianshushiji = nianshu
    nianlist = []
    for i in range(nianshushiji):
        nianlist.append(riqienddate + YearBegin(-(i + 1)))  # 2017-01-01,2016-01-01,2015-01-01

    # if xiangmu == '退货客户数' :
    #     print(df)
    dfn = pd.DataFrame(ds)  # 取出日期索引的数据列

    # 分年份生成按照每天日期重新索引的数据列
    dslist = []
    for i in range(nianshushiji):
        # dfnian = pd.DataFrame()
        if i == 0:
            periods = int(riqienddate.strftime('%j'))
        else:
            periods = 365
        dstmp = dfn.reindex(pd.date_range((riqienddate + YearBegin(-1 - (1 * i))), periods=periods, freq='D'),
                            fill_value=0)
        # if xiangmu == '退货客户数':
        #     print(dstmp.tail(30))
        if cum:
            dfnian = dstmp.resample('M').sum()
        else:
            dfnian = dstmp.resample('M').max()
        dfnian.columns = ['%04d' % nianlist[i].year]
        dfnian.index = range(len(dfnian.index))
        dslist.append(dfnian)
    # 连接年份DataFrame
    if len(dslist) == 0:
        log.info('年度对比数据为空！')
        return None
    dfy = pd.DataFrame(dslist[0])  # 0,0 1 2 3 4
    for i in range(1, len(dslist)):  # 1 2 3 4
        dfy = dfy.join(dslist[i], how='outer')  # 0 1 2 3 4

    # print(dfy)
    zuobiao = pd.Series(range(1, len(dfy.index) + 1))  # 从1开始生成序列，配合月份，日期的话是自动从1开始的，不用特别处理
    dfy.index = zuobiao.apply(lambda x: '%02d' % x)

    nianyue = '%04d年' % riqienddate.year
    biaoti = leixing + quyu + pinpai + nianyue + xiangmu
    dslistmax = []
    # dslistabs = [abs(x) for x in dslist]
    dfyabs = dfy.apply(lambda x: abs(x))
    # print(dfyabs.max())
    for clname in dfyabs.columns:
        dslistmax.append(dfyabs[clname].max())  # 取绝对值的最大，涵盖退货的负值金额
    # print(type(dslistmax))
    # print(dslistmax)
    # global ywananchor
    imglist = []
    if cum:
        cumstr = '月累积'
        dfjieguo = dfy.cumsum()
        dfjieguo.plot(title=biaoti + cumstr)
        if max(map(abs, dslistmax)) > ywananchor:
            plt.gca().yaxis.set_major_formatter(
                FuncFormatter(lambda x, pos: "%d万" % int(x / 10000)))  # 纵轴主刻度文本用y_formatter函数计算
        biaozhukedu(dfjieguo, '%02d' % riqienddate.month)
        imgpathstr = str(imgpath)
        if not os.path.exists(imgpathstr):
            os.mkdir(imgpathstr)
            log.info('%s不存在，将被创建' % imgpathstr)
        itemimgpath = str(imgpath / f'{biaoti}{cumstr}.png')
        plt.savefig(itemimgpath)
        imglist.append(itemimgpath)
        plt.close()
    cumstr = '月折线'
    dfy.plot(title='%s%s' % (biaoti, cumstr))
    if max(map(abs, dslistmax)) > ywananchor:
        plt.gca().yaxis.set_major_formatter(
            FuncFormatter(lambda x, pos: "%d万" % int(x / 10000)))  # 纵轴主刻度文本用y_formatter函数计算
    biaozhukedu(dfy, '%02d' % riqienddate.month)
    itemimgpath = str(imgpath / f'{biaoti}{cumstr}.png')
    plt.savefig(itemimgpath)
    imglist.append(itemimgpath)
    plt.close()

    return imglist


def chuturizhexian(df, riqienddate, xiangmu, cum=False,
                   quyu='', leixing='', pinpai='', imgpath=dirmainpath / 'img'):
    """
    日数据（月份）累积对比图，当月、环比、同期比
    riqienddate形如2017-12-08，代表数据结束点的日期
    :param df:
    :param riqienddate:
    :param xiangmu:
    :param cum:
    :param quyu:
    :param leixing:
    :param pinpai:
    :param imgpath:
    :return:
    """
    riqicurmonthfirst = riqienddate + MonthBegin(-1)  # 日期格式的当月1日
    riqibeforemonthfirst = riqienddate + MonthBegin(-2)  # 日期格式的上月1日
    riqilastmonthfirst = riqienddate + MonthBegin(-13)  # 日期格式的去年当月1日
    tianshu = (riqienddate + MonthEnd(-1)).day  # 当月的天数

    # print(df)
    ds = pd.DataFrame(df)
    datesb = pd.date_range(riqibeforemonthfirst, periods=tianshu, freq='D')  # 上月日期全集，截止到当月最后一天为止
    if ds.index.min() <= datesb.max():  # 存在有效数据则生成按全月每天索引的DataFrame，否则置空
        ds1 = ds.reindex(datesb, fill_value=0)  # 重新索引，补全所有日期，空值用0填充
        ds1.index = (range(1, len(datesb) + 1))  # 索引天日化
        ds1.columns = f'{riqibeforemonthfirst.year:04d}{riqibeforemonthfirst.month:02d}' + ds1.columns  # 列命名，形如201709
    else:
        ds1 = pd.DataFrame()

    datesl = pd.date_range(riqilastmonthfirst, periods=tianshu, freq='D')  # 处理去年当月数据
    if ds.index.min() <= datesl.max():  # 存在有效数据则生成按全月每天索引的DataFrame，否则置空
        ds3 = ds.reindex(datesl, fill_value=0)
        ds3.index = range(1, len(datesl) + 1)
        ds3.columns = ('%04d%02d' % (riqilastmonthfirst.year, riqilastmonthfirst.month)) + ds3.columns
    else:
        ds3 = pd.DataFrame()

    datesc = pd.date_range(riqicurmonthfirst, periods=riqienddate.day, freq='D')  # 处理当月数据，至截止日期
    if ds.index.min() <= datesc.max():  # 存在有效数据则生成按按照每天索引的DataFrame，否则置空并退出，避免空转
        ds2 = ds.reindex(datesc, fill_value=0)
        ds2.index = range(1, len(datesc) + 1)
        ds2.columns = ('%04d%02d' % (riqicurmonthfirst.year, riqicurmonthfirst.month)) + ds2.columns
    else:
        return

    dff = ds2.join(ds1, how='outer').join(ds3, how='outer')

    nianyue = '%04d%02d' % (riqicurmonthfirst.year, riqicurmonthfirst.month)
    biaoti = leixing + quyu + pinpai + nianyue + xiangmu
    # clnames = []
    # for ct in range(0, len(dff.columns), 2):
    #     clnames.append(dff.columns[ct])
    dfc = dff
    if cum:
        dfc = dfc.cumsum()  # 数据累积求和
        biaoti = biaoti + '日累积'
    # print(dfc)
    dfc.plot(title=biaoti)
    # plt.ylim(0) #设定纵轴从0开始

    biaozhukedu(dfc, riqienddate.day)
    imgsavepath = imgpath / (biaoti + '（日累积月）.png')
    touchfilepath2depth(imgsavepath)
    plt.savefig(str(imgsavepath))
    plt.close()
    imglistctrz = list()
    imglistctrz.append(str(imgsavepath))

    return imglistctrz


def dfin2imglist(dfin, cum, leixingset='', fenbuset='', pinpai='', imgmonthcount=1):
    # print(dfin.tail())
    imglists = []
    for cln in dfin.columns:
        imglist = []
        dfmoban = dfin[cln]
        dfmoban = dfmoban.dropna()  # 除去空值，避免折线中断，fillna(0)在reindex的时候再上
        if dfmoban.shape[0] == 0:  # 跳过空列，新品推广还没有退货发生时这种样子的数据可能出现，再就是数据起始日前放弃的产品，只有退货了
            continue
        # print(dfmoban)
        dangqianyueri = dfmoban.index.max()
        if (datetime.datetime.now() - dangqianyueri).days < 60:  # 近两个月还有数据的才做日累计分析
            for k in range(dangqianyueri.month):
                if k == 0:
                    riqiendwith = dangqianyueri
                else:
                    riqiendwith = dangqianyueri + MonthEnd(k * (-1))
                # print(riqiendwith)
                imglistson = chuturizhexian(dfmoban, riqiendwith, cln, cum=cum, leixing=leixingset, quyu=fenbuset,
                                            pinpai=pinpai, imgpath=dirmainpath / 'img' / fenbuset)
                if imglistson is not None:
                    imglist += imglistson
            if len(imglist) >= imgmonthcount:
                imglist = imglist[:imgmonthcount]
        nianshu = dfmoban.index.max().year - dfmoban.index.min().year + 1
        imglistson = chutuyuezhexian(dfmoban, dangqianyueri, cln, cum=cum, leixing=leixingset, quyu=fenbuset,
                                     pinpai=pinpai, nianshu=nianshu, imgpath=dirmainpath / 'img' / fenbuset)
        imglist += imglistson
        imglists.append(imglist)
    imglistreturn = []
    for i in range(len(imglists)):
        imglistreturn += imglists[i]
    # print(imglistreturn)
    return imglistreturn


def updatesection(cfpp, fromsection, tosection, inifile, token, note_store, zhuti='销售业绩图表'):
    """
    根据fromsection中的值构建新的tosection，fenbu、guid
    :param cfpp:
    :param fromsection:
    :param tosection:
    :param inifile:
    :param token:
    :param note_store:
    :param zhuti:
    :return:
    """
    if not cfpp.has_section(tosection):
        cfpp.add_section(tosection)
    nbfbdf = readinisection2df(cfpp, fromsection, zhuti)
    # print(nbfbdf)
    for aa in nbfbdf.index:
        @trycounttimes2('evernote服务器')
        def setguid():
            try:
                guid = cfpp.get(tosection, aa)
                if len(guid) > 0:
                    # print('笔记《' + str(aa) + zhuti + '》已存在，guid为：' + guid)
                    return
            except Exception as ee:
                log.info('笔记《' + str(aa) + zhuti + '》不存在，将被创建……%s' % str(ee))
            note = ttypes.Note()
            note.title = nbfbdf.loc[aa]['title']
            # print(aa + '\t\t' + note.title, end='\t\t')
            parentnotebook = note_store.getNotebook(nbfbdf.loc[aa]['guid'])
            evernoteapijiayi()
            note = makenote(token, note_store, note.title, parentnotebook=parentnotebook)
            # print(note.guid + '\t\t' + note.title)
            cfpp.set(tosection, aa, note.guid)

        setguid()

    cfpp.write(open(inifile, 'w', encoding='utf-8'))


# %%
if __name__ == '__main__':
    log.info(f'运行文件\t{__file__}')
    isworkday(['2019-10-15'])
    dtlist = list(pd.date_range('2019-01-01', '2019-10-07', freq='D'))
    dfresult = isworkday(dtlist, '梅富忠')
    print(dfresult)
    # cnxp = lite.connect(dbpathquandan)
    # dataokay(cnxp)
    log.info(f'文件{__file__}运行结束！')
