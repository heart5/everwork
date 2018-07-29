# encoding:utf-8
"""
处理放假休假请假等
['c1b8297a-2c3a-4afc-9faf-e36484495529', '武汉真元放假调休记录'],
['040509c2-a8bf-4af9-9296-3d41321889d9', '武汉真元员工请假记录']
['a582e11f-d6e6-4eb2-817f-196c70971f53', '武汉真元员工入职离职记录']
"""
import math
import numpy as np
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
    note_store = get_notestore()
    guid = cfpworkplan.get('行政管理', f'{zhuti[0]}guid')
    note = None
    try:
        note = note_store.getNote(guid, True, True, False, False)
        evernoteapijiayi()
    except ConnectionResetError as cre:
        log.critical(f'服务器发脾气，强行断线！{cre}')
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


def showdutyon():
    zhutiss = ['入职', 'dutyon']
    dfduty = chuliworkmateduty_note(zhutiss)
    # print(dfduty)
    zaizhi = list(dfduty[pd.isnull(dfduty.lizhi)].groupby('name').count().index)
    print(f'{len(zaizhi)}\t{zaizhi}')
    dfquanti = isworkday(['2016-1-1'], fromthen=True)
    dtquanti = dfquanti.groupby('xingzhi').count()['date'].rename('公司')
    print(dtquanti)
    dslist = [dtquanti]
    for zg in zaizhi:
        # print(zg)
        zgruzhimax = dfduty[dfduty.name == zg]['ruzhi'].max()
        dfgzmaxruizhi = dfduty[(dfduty.name == zg) & (dfduty.ruzhi == zgruzhimax)]
        print(dfgzmaxruizhi)
        zgruzhi, zglizhi = dfduty.loc[dfgzmaxruizhi.index, ['ruzhi', 'lizhi']].values[0]
        print(zgruzhi, zglizhi)
        dfzgwork = isworkday([pd.to_datetime('2016-1-1')], zg, fromthen=True)
        dfzgwork = dfzgwork[dfzgwork.date >= zgruzhi]
        if pd.notnull(zglizhi):
            dfzgwork = dfzgwork[dfzgwork.date <= zglizhi]
        dszg = dfzgwork.groupby('xingzhi').count()['date']
        # print(dszg.name)
        dszg = pd.Series(dszg)
        dszg = dszg.rename(zg)
        # print(dszg.name)
        dslist.append(dszg)

    dfgzduty = pd.DataFrame(dslist)
    dfgzduty.fillna(0, inplace=True)
    print(dfgzduty)

    dfout = pd.DataFrame()
    clsnames = list(dfgzduty.columns)
    clsjiaxiu = [x for x in clsnames if (x.find('班') < 0) & (x.find('假') < 0) & (x.find('旷') < 0)]
    dfjiaxiusum = dfgzduty.loc[:, clsjiaxiu].apply(lambda x : sum(x), axis=1).rename('假休')
    clsqingjia = [x for x in clsnames if x.find('假') > 0]
    dfqingjia = dfgzduty.loc[:, clsqingjia].apply(lambda x : sum(x), axis=1).rename('请假')
    dfkuanggong = None
    if len([x for x in clsnames if x.find('旷') >= 0]) > 0:
        dfkuanggong = dfgzduty['旷工']
    dfout = pd.DataFrame([dfgzduty['上班'], dfjiaxiusum, dfqingjia, dfkuanggong]).T
    return dfout


if __name__ == '__main__':
    # global log
    log.info(f'测试文件\t{__file__}')

    df = showdutyon()
    print(df)
    # fetchattendance_from_evernote(60 * 12)
    # dtlist = ['2018-6-14', '2018-6-10', '2018-5-1', '2018-3-4']
    # reslist = isworkday(dtlist)
    # print(dtlist)
    # print(reslist)
    # dtfrom = pd.to_datetime('2018-6-1')
    # tianshu = 25
    # drim = pd.date_range(dtfrom, dtfrom + datetime.timedelta(days=tianshu), freq='D').values
    # # print(drim)
    # resultlist = isworkday([pd.to_datetime('2018-7-16')], '梅富忠', fromthen=True).values
    # weekdaychinese = ['日', '一', '二', '三', '四', '五', '六']
    # for [dt, name, iswork, xingzhi, tianshu] in resultlist:
    #     print(f'{dt}\t{weekdaychinese[int(dt.strftime("%w"))]}\t{iswork}\t{xingzhi}')
    print('Done')
