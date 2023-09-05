# encoding:utf-8
# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     formats: ipynb,py:percent
#     notebook_metadata_filter: jupytext,-kernelspec,-jupytext.text_representation.jupytext_version
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
# ---

# %%
"""
处理放假休假请假等
['c1b8297a-2c3a-4afc-9faf-e36484495529', '武汉真元放假调休记录'],
['040509c2-a8bf-4af9-9296-3d41321889d9', '武汉真元员工请假记录']
['a582e11f-d6e6-4eb2-817f-196c70971f53', '武汉真元员工入职离职记录']
['72e6a107-0f78-4339-af6d-cbd927bf7713', '真元商贸员工打卡记录']
['e28fcbb1-1b8f-4384-a4d2-c5e234c1e602', '武汉高温纪录']
['e5d81ffa-89e7-49ff-bd4c-a5a71ae14320', '武汉雨天记录']
"""
import sqlite3 as lite
from threading import Timer
from pandas.tseries.offsets import *

# %%
import pathmagic

# %%
with pathmagic.context():
    from func.evernttest import *
    from func.pdtools import isworkday
    from func.first import dbpathworkplan
    from func.wrapfuncs import timethis
    from func.profilerlm import lpt_wrapper
    from work.fetchdata import fetch_dutyondata2lite


# %%
@timethis
# @lpt_wrapper()
def showdutyonfunc(dtlist: list = None, zglist: list = None):
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
    if '上班' in list(dfgzduty.columns):
        dfshangban = pd.DataFrame(dfgzduty['上班'].rename('出勤'))
    else:
        dfshangban = pd.DataFrame()
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
    # dfout.sort_values(['截止日期', '出勤'], ascending=[False, False], inplace=True)
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


# %%
@timethis
def showdutyon2note(monthnum:int = 3):
    recentdutyguid = '02540689-911d-4a2a-bd22-89fe44d41f2a'
    tday = pd.to_datetime(pd.to_datetime(datetime.datetime.today()).strftime('%F'))  # 罪魁祸首，日期中时间一定要归零

    # monthnum = 14
    dutytablelist = list()
    for i in range(1, monthnum + 1, 1):
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

    imglist2note(get_notestore(), [], recentdutyguid, f'真元商贸员工出勤统计表（最近{monthnum}个月）', dutytableliststr)

    alldutyonguid = '0d22c1f8-b92e-4c39-8d3e-7a6cb150e011'
    dfall, dfallfrom, dfallto = showdutyonfunc([pd.to_datetime('2010-10-22')])
    dutytableallstr = f"{dfallfrom.strftime('%F')}至{dfallto.strftime('%F')}" \
                      + tablehtml2evernote(dfall, dfallto.strftime('%Y-%m'), withindex=True)
    imglist2note(get_notestore(), [], alldutyonguid, '真元员工出勤大统计', dutytableallstr)


# %%
if __name__ == '__main__':
    # global log
    log.info(f'运行文件\t{__file__}')

    fetch_dutyondata2lite()
    monthnum = getinivaluefromnote('xingzheng', 'monthnum')
    showdutyon2note(monthnum)

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
    log.info(f'文件\t{__file__}执行结束。Done！')
