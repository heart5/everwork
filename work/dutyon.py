# encoding:utf-8
"""
处理放假休假请假等
['c1b8297a-2c3a-4afc-9faf-e36484495529', '武汉真元放假调休记录'],
['040509c2-a8bf-4af9-9296-3d41321889d9', '武汉真元员工请假记录']
['a582e11f-d6e6-4eb2-817f-196c70971f53', '武汉真元员工入职离职记录']
"""
import math
# import numpy as np
from threading import Timer

from pandas.tseries.offsets import *
import sqlite3 as lite
from bs4 import BeautifulSoup
from func.evernt import *
from func.pdtools import descdb, isworkday
from func.configpr import cfpworkplan as cfpworkplan, iniworkplanpath as iniworkplanpath
from func.first import dbpathworkplan


def chuliholidayleave_note(zhuti: list):
    note_store = get_notestore()
    guid = cfpworkplan.get('行政管理', f'{zhuti[0]}guid')
    note = note_store.getNote(guid, True, True, False, False)
    evernoteapijiayi()
    # print(timestamp2str(int(note.updated/1000)))
    # print(note.updateSequenceNum)
    if cfpworkplan.has_option('行政管理', f'{zhuti[0]}updatenum'):
        updatenumold = cfpworkplan.getint('行政管理', f'{zhuti[0]}updatenum')
    else:
        updatenumold = 0
    if note.updateSequenceNum <= updatenumold:
        log.info(f'{zhuti[0]}笔记内容无更新。')
        return False
    soup = BeautifulSoup(note.content, "html.parser").get_text().strip()
    # print(soup)
    # pattern = re.compile(u'(\d{4}-\d{2}-\d{2})[,，](\w+)[,，](\d{1,2}?)', re.U)
    pattern = re.compile(u'(\d{4}-\d{2}-\d{2})', re.U)
    splititems = re.split(pattern, soup)[1:]
    # print(splititems)
    resultlisthd = list()
    for i in range(int(len(splititems) / 2)):
        item = list()
        item.append(pd.to_datetime(splititems[i * 2]))
        *names, daynum = re.split('[,，]', splititems[i * 2 + 1])
        # print(sitems)
        if len(names) == 2:
            if names[1].find('上班') >= 0:
                names.append('上班')
            else:
                names.append('放假')
        # item.append(names[1:])
        item.append(names[1])
        item.append(names[2])
        item.append(daynum)
        resultlisthd.append(item)

    # print(resultlist)

    dfresult = None
    for [dtinfor, mingmu, xingzhiinfor, tian] in resultlisthd:
        numfloat = float(tian)
        numceil = math.ceil(numfloat)
        numfloor = math.floor(numfloat)
        driminfor = pd.date_range(dtinfor, dtinfor + datetime.timedelta(days=int(numceil) - 1), freq='D')
        if dfresult is None:
            dfresult = pd.DataFrame(index=driminfor)
            dfresult['mingmu'] = mingmu
            dfresult['xingzhi'] = xingzhiinfor
            dfresult['tianshu'] = 1
            # dfresult['tianshu'] = dfresult['tianshu'].astype(float)
            if numfloat > numfloor:
                xtian = numfloat - numfloor
                # print(f'{numfloat}\t{numceil}\t{numfloor}\t{mingmu}\t{xingzhi}\t{tian}\t{xtian}')
                dfresult.ix[-1, ['tianshu']] = xtian
        else:
            dftmp = pd.DataFrame(index=driminfor)
            dftmp['mingmu'] = mingmu
            dftmp['xingzhi'] = xingzhiinfor
            dftmp['tianshu'] = 1
            # dfresult['tianshu'] = dfresult['tianshu'].astype(float)
            if numfloat > numfloor:
                xtian = numfloat - numfloor
                # print(f'{numfloat}\t{numceil}\t{numfloor}\t{mingmu}\t{xingzhi}\t{tian}\t{xtian}')
                dftmp.ix[-1, ['tianshu']] = xtian
            dfresult = dfresult.append(dftmp)

    dfresult.sort_index(ascending=False, inplace=True)
    dfresult['date'] = dfresult.index
    # dfresult['idx'] = range(dfresult.shape[0])
    dfresult = dfresult.reset_index(drop=True)
    cnxp = lite.connect(dbpathworkplan)
    dfresult.to_sql(zhuti[1], cnxp, if_exists='replace')  # index, ['mingmu', 'xingzhi', 'tianshu', 'date']
    cnxp.close()
    log.info(f'{zhuti[0]}数据表更新了{dfresult.shape[0]}条记录。')
    cfpworkplan.set('行政管理', f'{zhuti[0]}updatenum', '%d' % note.updateSequenceNum)
    cfpworkplan.write(open(iniworkplanpath, 'w', encoding='utf-8'))
    return dfresult


def fetchattendance_from_evernote():
    try:
        zhutis = [['放假', 'holiday'], ['请假', 'leave']]
        for zhuti in zhutis:
            dfresult = chuliholidayleave_note(zhuti)
            if dfresult is not False:
                descdb(dfresult)
    except WindowsError as wine:
        log.critical(f'从evernote获取放假笔记信息时出现未名错误。{wine}')

    # global timer_holiday2datacenter
    # timer_holiday2datacenter = Timer(jiangemiao, fetchattendance_from_evernote, [jiangemiao])
    # timer_holiday2datacenter.start()


def chuliworkmateduty_note(zhuti: list):
    guid = cfpworkplan.get('行政管理', f'{zhuti[0]}guid')
    note = None
    try:
        note_store = get_notestore()
        note = note_store.getNote(guid, True, True, False, False)
        evernoteapijiayi()
    except ConnectionResetError as cre:
        log.critical(f'服务器发脾气，强行重置了！{cre}')
    # print(timestamp2str(int(note.updated/1000)))
    # print(note.updateSequenceNum)
    cnxp = lite.connect(dbpathworkplan)

    if cfpworkplan.has_option('行政管理', f'{zhuti[0]}updatenum'):
        updatenumold = cfpworkplan.getint('行政管理', f'{zhuti[0]}updatenum')
    else:
        updatenumold = 0
    if note.updateSequenceNum <= updatenumold:  # and False:
        log.info(f'{zhuti[0]}笔记内容无更新。')
        dfresult = pd.read_sql(f'select * from {zhuti[1]}', cnxp, parse_dates=['ruzhi', 'lizhi'])
        cnxp.close()
        return dfresult

    souporigin = BeautifulSoup(note.content, "html.parser")
    items = list()
    for item in souporigin.find_all('div'):
        pattern = re.compile(u'[,，]', re.U)
        itemtext = item.get_text().strip()
        ims = re.split(pattern, itemtext)
        if len(ims) == 3:
            im = list()
            im.append(ims[0])
            im.append(pd.to_datetime(ims[1]))
            im.append(pd.to_datetime(ims[2]))
            items.append(im)
    print(items)

    dfresult = pd.DataFrame(items, columns=['name', 'ruzhi', 'lizhi'])
    dfresult.sort_values(['ruzhi', 'lizhi'], ascending=[False, False])
    # print(dfresult)
    dfresult.to_sql(zhuti[1], cnxp, if_exists='replace', index=False)  # index, ['mingmu', 'xingzhi', 'tianshu', 'date']
    cnxp.close()
    log.info(f'{zhuti[0]}数据表更新了{dfresult.shape[0]}条记录。')
    cfpworkplan.set('行政管理', f'{zhuti[0]}updatenum', '%d' % note.updateSequenceNum)
    cfpworkplan.write(open(iniworkplanpath, 'w', encoding='utf-8'))

    return dfresult


def showdutyonfunc(dtlist: list = None, zglist: list = None):
    fetchattendance_from_evernote()
    zhutiss = ['入职', 'dutyon']
    dfduty = chuliworkmateduty_note(zhutiss)
    # print(dfduty)

    # 处理参数：空则从本月1日到今天；一个则默认是起始日期，到今天；数组则判断大小
    if dtlist is None:
        dtto = pd.to_datetime(datetime.datetime.today())
        dtfrom = pd.to_datetime(dtto.strftime('%Y-%m-01'))
    elif len(dtlist) == 1:
        dtto = pd.to_datetime(datetime.datetime.today())
        dtshuru = pd.to_datetime(dtlist[0])
        dtfrom = dtshuru
    else:
        dtto = max(dtlist)
        dtfrom = min(dtlist)
    # 首尾界限处理，最早公司创立日，最晚是今天
    if dtfrom < pd.to_datetime('2010-10-22'):
        dtfrom = pd.to_datetime('2010-10-22')
    if dtto > pd.to_datetime(datetime.datetime.today()):
        dtto = pd.to_datetime(datetime.datetime.today())
    dtlistinner = pd.date_range(dtfrom, dtto, freq='D')
    # print(dtfrom, type(dtfrom), dtto, type(dtto))
    if zglist:
        dfdutytarget = dfduty
        zaizhi = zglist
    else:
        dfdutytarget = dfduty[((pd.isnull(dfduty.lizhi)) | (dfduty.lizhi >= dtfrom))]
        # print(dfdutytarget)
        dfdutytarget = dfdutytarget[dfdutytarget.ruzhi <= dtto]
        # print(dfdutytarget)
        zaizhi = list(dfdutytarget.groupby('name').count().index)
    print(f'{len(zaizhi)}\t{zaizhi}')

    dfquanti = isworkday(list(dtlistinner))
    dtquanti = dfquanti.groupby('xingzhi').count()['date'].rename('公司')
    dtquanti['起始日期'] = dtfrom.strftime('%F')
    dtquanti['截止日期'] = dtto.strftime('%F')
    # print(list(dtquanti))
    dslist = [dtquanti]
    for zg in zaizhi:
        # print(zg)
        zgruzhimax = dfdutytarget[dfdutytarget.name == zg]['ruzhi'].max()
        dtfrom4 = dtfrom
        if dtfrom4 < pd.to_datetime(zgruzhimax):
            dtfrom4 = pd.to_datetime(zgruzhimax)
        dfgzmaxruizhi = dfdutytarget[(dfdutytarget.name == zg) & (dfdutytarget.ruzhi == zgruzhimax)]
        # print(dfgzmaxruizhi)
        zgruzhi, zglizhi = dfdutytarget.loc[dfgzmaxruizhi.index, ['ruzhi', 'lizhi']].values[0]
        # print(zgruzhi, type(zgruzhi), zglizhi, type(zglizhi))
        dfzgwork = isworkday(list(dtlistinner), zg, fromthen=True)
        # print(dfzgwork)
        dfzgwork = dfzgwork[dfzgwork.date >= zgruzhi]
        dtto4 = dtto
        if pd.notnull(zglizhi):
            if dtto4 > pd.to_datetime(zglizhi):
                dtto4 = pd.to_datetime(zglizhi)
            dfzgwork = dfzgwork[dfzgwork.date <= zglizhi]
        dszg = dfzgwork.groupby('xingzhi').sum()['tianshu']
        # print(dszg.name)
        dszg = pd.Series(dszg)
        dszg = dszg.rename(zg)
        dszg['起始日期'] = dtfrom4.strftime('%F')
        dszg['截止日期'] = dtto4.strftime('%F')
        # print(dszg.name)
        dslist.append(dszg)

    dfgzduty = pd.DataFrame(dslist)
    dfgzduty.fillna(0, inplace=True)
    # print(dfgzduty)

    # return dfgzduty, dtquanti, zaizhi

    dfshangban = pd.DataFrame(dfgzduty['上班'].rename('出勤'))
    # print(dfout)
    clsnames = list(dfgzduty.columns)
    # print(clsnames)
    clsjiaxiu = [x for x in clsnames if
                 (x.find('上班') < 0) & (x.find('请假') < 0) & (x.find('旷') < 0) & (x.find('日期') < 0)]
    # print(clsjiaxiu)
    # print(dfgzduty.loc[:, clsjiaxiu])
    dfjiaxiusum = dfgzduty.loc[:, clsjiaxiu].apply(lambda x: sum(x), axis=1).rename('放休年')
    # dfout.append(dfjiaxiusum)
    # clsqingjia = [x for x in clsnames if x.find('假') > 0]
    # dfqingjia = dfgzduty.loc[:, clsqingjia].apply(lambda x: sum(x), axis=1).rename('事年')
    # dfout.append(dfqingjia)
    # dfout = pd.concat([dfshangban, dfjiaxiusum, dfqingjia], axis=1)
    dfout = pd.concat([dfshangban, dfjiaxiusum], axis=1)
    if len([x for x in clsnames if x.find('旷工') >= 0]) > 0:
        dfkuangong = pd.DataFrame(dfgzduty['旷工'])
        dfout = pd.concat([dfout, dfkuangong], axis=1)
    if len([x for x in clsnames if x.find('请假') >= 0]) > 0:
        dfqingjia = pd.DataFrame(dfgzduty['请假'])
        dfout = pd.concat([dfout, dfqingjia], axis=1)
    dfout = pd.DataFrame(dfout)
    dfout['在职天数'] = dfout.apply(lambda x: sum(x), axis=1)
    # print(dfout)
    dfout = pd.concat([dfout, dfgzduty.loc[:, ['起始日期', '截止日期']]], axis=1)
    dfout = pd.DataFrame(dfout)
    # print(dfout)
    dfout.sort_values(['截止日期', '出勤', '请假'], ascending=[False, False, False], inplace=True)
    clsout = list(dfout.columns)
    clsnew = clsout[-2:] + [clsout[-3]] + clsout[:-3]
    # print(clsnew)
    dfout = dfout.loc[:, clsnew]
    return dfout, dtfrom, dtto


def showdutyon2note():
    recentdutyguid = '02540689-911d-4a2a-bd22-89fe44d41f2a'
    tday = pd.to_datetime(pd.to_datetime(datetime.datetime.today()).strftime('%F'))  # 罪魁祸首，日期中时间一定要归零

    dutytablelist = list()
    for i in range(1, 4, 1):
        thismonth = tday + MonthBegin((-1) * i)
        thismonthend = tday + MonthEnd((-1) * i + 1)
        print(thismonth.strftime('%F'), thismonthend.strftime('%F'))
        dtitemrange = list(pd.date_range(thismonth, thismonthend, freq='D'))
        # print(dtitemrange)
        dfitem, dfitemfrom, dfitemto = showdutyonfunc(dtitemrange)
        # print(dfitem)
        dutytablelist.append([dfitem, dfitemfrom, dfitemto])
    dutytableliststr = ''
    for i in range(len(dutytablelist)):
        dutytableliststr += f"{dutytablelist[i][1].strftime('%F')}至{dutytablelist[i][2].strftime('%F')}" \
                            + tablehtml2evernote(dutytablelist[i][0],
                                                 dutytablelist[i][1].strftime('%Y-%m'), withindex=True)

    imglist2note(get_notestore(), [], recentdutyguid, '真元商贸员工出勤统计表（最近三个月）', dutytableliststr)

    alldutyonguid = '0d22c1f8-b92e-4c39-8d3e-7a6cb150e011'
    dfall, dfallfrom, dfallto = showdutyonfunc([pd.to_datetime('2010-10-22')])
    dutytableallstr = f"{dfallfrom.strftime('%F')}至{dfallto.strftime('%F')}" \
                      + tablehtml2evernote(dfall, dfallto.strftime('%Y-%m'), withindex=True)
    imglist2note(get_notestore(), [], alldutyonguid, '真元员工出勤大统计', dutytableallstr)


def duty_timer(jiangemiao):
    showdutyon2note()

    global timer_duty2note
    timer_duty2note = Timer(jiangemiao, duty_timer, [jiangemiao])
    timer_duty2note.start()


if __name__ == '__main__':
    # global log
    log.info(f'测试文件\t{__file__}')

    # duty_timer(60 * 5)
    showdutyon2note()

    # df, dtf, dtt = showdutyonfunc(list(pd.date_range(pd.to_datetime('2018-7-1'), pd.to_datetime('2018-7-31'),
    # freq='D')),zglist=['徐志伟', '梅富忠', '周莉']) print(dtf.strftime('%F'), dtt.strftime('%F')) print(df)

    # df, dtf, dtt = showdutyon(zglist = ['徐志伟', '梅富忠', '甘微'])
    # print(dtf.strftime('%F'), dtt.strftime('%F'))
    # print(df)

    # df, dtf, dtt = showdutyonfunc(list(pd.date_range(pd.to_datetime('2017-6-1'), pd.to_datetime('2018-3-1'),
    # freq='D'))) print(dtf.strftime('%F'), dtt.strftime('%F')) print(df)

    # df, dtf, dtt = showdutyonfunc(list(pd.date_range(pd.to_datetime('2010-6-1'), pd.to_datetime('2018-12-1'),
    # freq='D'))) print(dtf.strftime('%F'), dtt.strftime('%F')) print(df) fetchattendance_from_evernote(60 * 12)
    # dtlist = ['2018-6-14', '2018-6-10', '2018-5-1', '2018-3-4'] reslist = isworkday(dtlist) print(dtlist) print(
    # reslist) dtfrom = pd.to_datetime('2018-6-1') tianshu = 25 drim = pd.date_range(dtfrom,
    # dtfrom + datetime.timedelta(days=tianshu), freq='D').values # print(drim) resultlist = isworkday([
    # pd.to_datetime('2018-7-16')], '梅富忠', fromthen=True).values weekdaychinese = ['日', '一', '二', '三', '四', '五',
    # '六'] for [dt, name, iswork, xingzhi, tianshu] in resultlist: print(f'{dt}\t{weekdaychinese[int(dt.strftime(
    # "%w"))]}\t{iswork}\t{xingzhi}')
    print('Done')
