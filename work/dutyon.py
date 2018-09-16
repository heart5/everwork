# encoding:utf-8
"""
处理放假休假请假等
['c1b8297a-2c3a-4afc-9faf-e36484495529', '武汉真元放假调休记录'],
['040509c2-a8bf-4af9-9296-3d41321889d9', '武汉真元员工请假记录']
['a582e11f-d6e6-4eb2-817f-196c70971f53', '武汉真元员工入职离职记录']
['72e6a107-0f78-4339-af6d-cbd927bf7713', '真元商贸员工打卡记录']
['e28fcbb1-1b8f-4384-a4d2-c5e234c1e602', '武汉高温纪录']
['e5d81ffa-89e7-49ff-bd4c-a5a71ae14320', '武汉雨天记录']
"""
import math
import ssl
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
    # print(zhuti)
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
    souporigin = BeautifulSoup(note.content, "html.parser")
    # print(soup)
    isjiaqi = False
    items = list()
    columns = list()
    for item in souporigin.find_all(['div', 'p']):
        itemtext = item.get_text().strip()
        if len(itemtext) == 0:
            continue
        patterntime = u'(\w*\s*\d+,\s*\d{4}\s*at\s*\d{2}:\d{2}[AP]M)\s*'
        splititems = re.split(patterntime, itemtext)
        if len(splititems) == 3:
            if splititems[2].startswith('：'):
                # rain
                columns = ['date', 'raintime', 'mingmu']
                itemtime = time.strptime(splititems[1], '%B %d, %Y at %I:%M%p')
                item = list()
                item.append(pd.to_datetime(time.strftime('%F', itemtime)))
                item.append(pd.to_datetime(time.strftime('%F %T', itemtime)))
                item.append('下雨')
                items.append(item)
                continue

            # hot
            columns = ['date', 'hottime', 'mingmu']
            itemtime = time.strptime(splititems[1], '%B %d, %Y at %I:%M%p')
            item = list()
            item.append(pd.to_datetime(time.strftime('%F', itemtime)))
            item.append(pd.to_datetime(time.strftime('%F %T', itemtime)))
            item.append('高温')
            items.append(item)
            continue
        pattern = re.compile(u'[,，\s]', re.U)
        ims = re.split(pattern, itemtext)
        if len(ims) == 0:
            continue
        if len(ims) == 3:
            item = list()
            dtpattern = re.compile(u'(\d{4}-\d{1,2}-\d{1,2})', re.U)
            if re.fullmatch(dtpattern, ims[0]):
                isjiaqi = True
                # holiday
                columns = ['date', 'mingmu', 'xingzhi', 'tianshu']
                item.append(pd.to_datetime(ims[0]))
                if ims[1].find('上班') >= 0:
                    item.append('上班')
                else:
                    item.append('放假')
                item.append(ims[1])
                item.append(ims[2])
                items.append(item)
            elif re.fullmatch(dtpattern, ims[1]):
                # duty
                columns = ['name', 'ruzhi', 'lizhi']
                item.append(ims[0])
                item.append(pd.to_datetime(ims[1]))
                item.append(pd.to_datetime(ims[2]))
                items.append(item)
        elif len(ims) == 4:
            item = list()
            dtpattern = re.compile(u'(\d{4}-\d{1,2}-\d{1,2})', re.U)
            if re.fullmatch(dtpattern, ims[0]):
                isjiaqi = True
                # leave
                columns = ['date', 'mingmu', 'xingzhi', 'tianshu']
                item.append(pd.to_datetime(ims[0]))
                item.append(ims[1])
                item.append(ims[2])
                item.append(ims[3])
                items.append(item)
            elif re.fullmatch(dtpattern, ims[1]):
                # checkin
                columns = ['date', 'name', 'mingmu', 'shenpi']
                item.append(pd.to_datetime(ims[1]))
                item.append(ims[0])
                item.append(ims[2])
                item.append(ims[3])
                items.append(item)

    print(items)
    if isjiaqi:
        resultlisthd = items
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
        # holiday, ['date', 'mingmu', 'xingzhi', 'tianshu']
        dfresult = dfresult.reset_index(drop=True)
    else:
        dfresult = pd.DataFrame(items, columns=columns)
    # print(dfresult)
    cnxp = lite.connect(dbpathworkplan)
    dfresult.to_sql(zhuti[1], cnxp, if_exists='replace', index=None)  # index, ['mingmu', 'xingzhi', 'tianshu', 'date']
    cnxp.close()
    log.info(f'{zhuti[0]}数据表更新了{dfresult.shape[0]}条记录。')
    cfpworkplan.set('行政管理', f'{zhuti[0]}updatenum', '%d' % note.updateSequenceNum)
    cfpworkplan.write(open(iniworkplanpath, 'w', encoding='utf-8'))
    return dfresult


def fetchattendance_from_evernote():
    zhutis = [
        ['放假', 'holiday'],
        ['请假', 'leave'],
        ['打卡', 'checkin'],
        ['入职', 'dutyon'],
        ['高温', 'hot'],
        ['下雨', 'rain']
    ]
    try:
        for zhuti in zhutis:
            dfresult = chuliholidayleave_note(zhuti)
            if dfresult is not False:
                descdb(dfresult)
    except (WindowsError, Exception) as wine:
        topic = [x for [x, *y] in zhutis]
        log.critical(f'从evernote获取{topic}笔记信息时出现未名错误。{wine}')

    # global timer_holiday2datacenter
    # timer_holiday2datacenter = Timer(jiangemiao, fetchattendance_from_evernote, [jiangemiao])
    # timer_holiday2datacenter.start()


def showdutyonfunc(dtlist: list = None, zglist: list = None):
    fetchattendance_from_evernote()
    cnxwp = lite.connect(dbpathworkplan)
    dfduty = pd.read_sql('select * from dutyon', cnxwp, parse_dates=['ruzhi', 'lizhi'])
    # print(dfduty)
    if dfduty is None:
        return

    # 处理参数：空则从本月1日到今天；一个则默认是起始日期，到今天；数组则判断大小
    if len(dtlist) == 0:
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
    # 挂接高温记录统计
    dfhot = pd.read_sql('select * from hot', cnxwp, parse_dates=['date'])
    # print(dfhot)
    dfhotgrp = dfhot.groupby('date', as_index=False).count()[['date', 'mingmu']]
    # print(dfhotgrp)
    dfhotworkday = isworkday(list(dfhotgrp['date']))
    dfhotworkday = dfhotworkday[dfhotworkday.work]
    dfhotdone = dfhotworkday[(dfhotworkday.date >= dtfrom) & (dfhotworkday.date <= dtto)]
    dtquanti['高温'] = dfhotdone.shape[0]
    # 挂接雨天记录统计
    dfrain = pd.read_sql('select * from rain', cnxwp, parse_dates=['date'])
    # print(dfhot)
    dfraingrp = dfrain.groupby('date', as_index=False).count()[['date', 'mingmu']]
    # print(dfhotgrp)
    dfrainworkday = isworkday(list(dfraingrp['date']))
    dfrainworkday = dfrainworkday[dfrainworkday.work]
    dfraindone = dfrainworkday[(dfrainworkday.date >= dtfrom) & (dfrainworkday.date <= dtto)]
    dtquanti['下雨'] = dfraindone.shape[0]

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
        # 挂接高温记录统计
        dfhotworkday = isworkday(list(dfhotgrp['date']), zg, fromthen=True)
        dfhotworkday = dfhotworkday[dfhotworkday.work]
        dfhotdone = dfhotworkday[(dfhotworkday.date >= dtfrom4) & (dfhotworkday.date <= dtto4)]
        # 修正上了半天班的情况
        xiuzheng = dfhotdone[(dfhotdone.xingzhi == '上班') & (dfhotdone.tianshu < 1)].shape[0]
        # print(xiuzheng)
        dszg['高温'] = dfhotdone.shape[0] - xiuzheng
        # 挂接高温记录统计
        dfrainworkday = isworkday(list(dfraingrp['date']), zg, fromthen=True)
        dfrainworkday = dfrainworkday[dfrainworkday.work]
        dfraindone = dfrainworkday[(dfrainworkday.date >= dtfrom4) & (dfrainworkday.date <= dtto4)]
        # 修正上了半天班的情况
        xiuzheng = dfraindone[(dfraindone.xingzhi == '上班') & (dfraindone.tianshu < 1)].shape[0]
        # print(xiuzheng)
        dszg['下雨'] = dfraindone.shape[0] - xiuzheng

        # print(f'{dszg.name}：{list(dszg)}')
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
                 (x.find('上班') < 0) & (x.find('请假') < 0) & (x.find('旷') < 0) & (x.find('日期') < 0)
                 & (x.find('高温') < 0) & (x.find('下雨') < 0)]
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
    dfout.fillna(0, inplace=True)
    dfout['在职天数'] = dfout.apply(lambda x: sum(x), axis=1)
    # print(dfout)
    dfout = pd.concat([dfout, dfgzduty.loc[:, ['起始日期', '截止日期']]], axis=1)
    dfout = pd.DataFrame(dfout)
    # print(dfout)
    dfout.sort_values(['截止日期', '出勤'], ascending=[False, False], inplace=True)
    clsout = list(dfout.columns)
    # print(clsout)
    clsnew = clsout[-2:] + [clsout[-3]] + clsout[:-3]
    # print(clsnew)
    dfout = dfout.loc[:, clsnew]
    # 挂接打卡记录统计
    dfcheckin = pd.read_sql_query('select * from checkin', cnxwp, parse_dates=['date'])
    # dfcheckin.columns = ['date', 'name', 'mingmu', 'shenpi']
    cnxwp.close()
    dfcheckin = dfcheckin[(dfcheckin.date >= dtfrom) & (dfcheckin.date <= dtto)]
    dfcheckinout = dfcheckin[dfcheckin['shenpi'] == ''].groupby(['name', 'mingmu']).count()['shenpi'].unstack()
    if dfcheckinout.shape[0] > 0:
        print(dfcheckinout)
        dfout = pd.concat([dfout, dfcheckinout], axis=1)
    dfout = pd.concat([dfout, pd.DataFrame(dfgzduty['高温'])], axis=1)
    dfout = pd.concat([dfout, pd.DataFrame(dfgzduty['下雨'])], axis=1)
    dfout = pd.DataFrame(dfout)
    # print(dfout.columns)
    dfout.fillna(0, inplace=True)
    dfout.index.names = [f'{dfout.shape[0] - 1}']
    return dfout, dtfrom, dtto


def showdutyon2note():
    recentdutyguid = '02540689-911d-4a2a-bd22-89fe44d41f2a'
    tday = pd.to_datetime(pd.to_datetime(datetime.datetime.today()).strftime('%F'))  # 罪魁祸首，日期中时间一定要归零

    monthnum = 14
    dutytablelist = list()
    for i in range(1, monthnum, 1):
        if tday.day == 1:
            tday = pd.to_datetime(tday.strftime('%Y-%m-02'))
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

    imglist2note(get_notestore(), [], recentdutyguid, f'真元商贸员工出勤统计表（最近{monthnum-1}个月）', dutytableliststr)

    alldutyonguid = '0d22c1f8-b92e-4c39-8d3e-7a6cb150e011'
    dfall, dfallfrom, dfallto = showdutyonfunc([pd.to_datetime('2010-10-22')])
    dutytableallstr = f"{dfallfrom.strftime('%F')}至{dfallto.strftime('%F')}" \
                      + tablehtml2evernote(dfall, dfallto.strftime('%Y-%m'), withindex=True)
    imglist2note(get_notestore(), [], alldutyonguid, '真元员工出勤大统计', dutytableallstr)


def duty_timer(jiangemiao):
    try:
        showdutyon2note()
    except TypeError as te:
        log.critical(f'类型错误。{te}')
    except EDAMUserException as eue:
        log.critical(f'evernote用户错误。{eue}')

    global timer_duty2note
    timer_duty2note = Timer(jiangemiao, duty_timer, [jiangemiao])
    timer_duty2note.start()


if __name__ == '__main__':
    # global log
    log.info(f'运行文件\t{__file__}')

    # fetchattendance_from_evernote()
    # duty_timer(60 * 60 * 3 + 60 * 37)
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
