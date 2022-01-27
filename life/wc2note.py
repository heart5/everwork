# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       jupytext_version: 1.13.4
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # 微信聊天记录文本文件智能远程存储 

# %% [markdown]
# - 文本文件：跑程序生成的txt存储的记录原始文件
# - 资源文件：提取并排序后按月拆分的记录存储文件，excel表格
# - 笔记：记录了分月统计和更新信息的云端笔记，附件为相应的资源文件

# %% [markdown]
# ## 库导入

# %%
import os
import re
import xlsxwriter
import pandas as pd
import sqlite3 as lite
from pathlib import Path
from datetime import datetime

import pathmagic
with pathmagic.context():
    from func.first import getdirmain, touchfilepath2depth
    from func.logme import log
    from etc.getid import getdevicename
    from func.wrapfuncs import timethis
    from func.sysfunc import not_IPython, execcmd
    from func.configpr import setcfpoptionvalue, getcfpoptionvalue
    from func.litetools import ifnotcreate, showtablesindb
    from func.evernttest import getinivaluefromnote, getnoteresource, \
        gettoken, get_notestore, getnotecontent, updatereslst2note, \
        createnotebook, makenote2, findnotebookfromevernote, \
        findnotefromnotebook, imglist2note
    from filedatafunc import getfilemtime as getfltime


# %% [markdown]
# ## 功能函数集

# %% [markdown]
# ### def items2df(fl)

# %%
def items2df(fl):
    """
    读取txt记录文件，格式化拆分并存储至DataFrame返回
    """
    try:
        content = open(fl, 'r').read()
    except Exception as e:
        log.critical(f"文件{fl}读取时出现错误，返回空的pd.DataFrame")
        return pd.DataFrame()
    ptn = re.compile("(^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\t(True|False)\t([^\t]+)\t(\w+)\t", re.M)
    itemlst = re.split(ptn, content)
    itemlst = [im.strip() for im in itemlst if len(im) > 0]
    step = 5
    itemlst4pd1 = [itemlst[i : i + step] for i in range(0, len(itemlst), step)]
    df2 = pd.DataFrame(itemlst4pd1, columns=['time', 'send', 'sender', 'type', 'content'])
    df2['time'] = pd.to_datetime(df2['time'])
    df2['send'] = df2['send'].apply(lambda x : True if x == 'True' else False)
    df2['content'] = df2['content'].apply(lambda x: re.sub("(\[\w+前\])?", "", x))
    dfout = df2.drop_duplicates().sort_values('time', ascending=False)
    
    return dfout


# %% [markdown]
# ### def getaccountowner()

# %%
def getownerfromfilename(fn):
    """
    从文件名中获取账号
    """
    ptn = re.compile("\((\w*)\)")
    ac = ac if (ac := re.search(ptn, fn).groups()[0]) not in ['', 'None'] else '白晔峰'
    return ac


# %% [markdown]
# ### def txtfiles2dfdict(wcdatapath)

# %%
@timethis
def txtfiles2dfdict(dpath, newfileonly=False):
    """
    读取传入目录下符合标准（固定格式文件名）所有文本文件并提取融合分账号的df，
    返回字典{name:dict}
    """

    fllst = [f for f in os.listdir(dpath) if f.startswith("chatitems")]
    names = list(set([getownerfromfilename(nm) for nm in fllst]))
    print(names)
    # 如果设置为new，则找到每个账号的最新文本文件处理，否则是全部文本文件
    if newfileonly:
        fl3lst = [[getownerfromfilename(fl), fl, getfltime(dpath / fl)] for fl in fllst]
        fllstout = list()
        for nm in names:
            fllstinner = [item for item in fl3lst if item[0] == nm]
            fllstout4name = sorted(fllstinner, key=lambda x :x[2])
            fllstout.extend(fllstout4name[-2:])
        fllst = [item[1] for item in fllstout]

#     print(fllst)
    dfdict = dict()
    for fl in fllst[::-1]:
        rs1 = re.search("\((\w*)\)", fl)
        if rs1 is None:
            log.critical(f"记录文件《{fl}》的文件名不符合规范，跳过")
            continue
        account = getownerfromfilename(fl)
        dfin = items2df(dpath / fl)
        print(f"{fl}\t{getfltime(dpath / fl).strftime('%F %T')}\t " \
            f"{account}\t{dfin.shape[0]}", end="\t")
        if account in dfdict.keys():
            dfall = dfdict[account].append(dfin)
            dfall = dfall.drop_duplicates().sort_values(['time'], ascending=False)
            print(f"{dfall.shape[0]}")
            dfdict.update({account:dfall})
        else:
            dfall = dfin.drop_duplicates().sort_values(['time'], ascending=False)
            print(f"{dfall.shape[0]}")
            dfdict[account] = dfall

    return dfdict


# %% [markdown]
# ### def getdaterange(start, end)

# %%
def getdaterange(start, end):
    """
    根据输入的起止时间按照月尾分割生成时间点列表返回
    """
    start = start + pd.Timedelta(-1, 'sec')
    if start.strftime("%Y-%m") == end.strftime('%Y-%m'):
        drlst = [start, end]
    else:
        dr = pd.date_range(pd.to_datetime(start.strftime("%F 23:59:59")), end, freq='M')
        drlst = list(dr)
#         drlst.pop()
        drlst.insert(0, start)
        drlst.append(end)
    
    return drlst


# %% [markdown]
# ### def splitdf(name, df, wcdatapath)

# %%
def txtdfsplit2xlsx(name, df, dpath, newfileonly=False):
    """
    按月份拆分指定账号的数据记录df，如果尚不存在本地相应资源文件，直接写入并更新ini中登记
    数量；如果存在相应本地资源文件，则读取并融合df中的记录，存入对应格式化名称的excel表格
    中，相应更新ini中登记数量
    """
    dftimestart = df['time'].min()
    dftimeend = df['time'].max()
    dr = getdaterange(dftimestart, dftimeend)
    if newfileonly:
        dr = dr[-2:]
    log.info(f"时间范围横跨{len(dr) - 1}个月")

    outlst = list()
    for i in range(len(dr) - 1):
        print(f"{'-' * 15}\t{name}\t【{i + 1}/{len(dr) - 1}】\tBegin\t{'-' * 15}")
        dfp = df[(df.time > dr[i]) & (df.time <= dr[i + 1])]
        if dfp.shape[0] != 0:
            ny = dfp['time'].iloc[0].strftime("%y%m")
            fn = f"wcitems_{name}_{ny}.xlsx" # 纯文件名称
            fna = os.path.abspath(dpath / fn) # 全路径文件名（绝对路径）
            if not os.path.exists(fna):
                logstr = f"创建文件{fn}，记录共有{dfp.shape[0]}条。"
                log.info(logstr)
                dfp.to_excel(fna, engine='xlsxwriter', index=False)
                setcfpoptionvalue('everwcitems', fn, 'itemsnumfromtxt',
                                  f"{dfp.shape[0]}")
            else:
                if (oldnum := getcfpoptionvalue('everwcitems', fn, 'itemsnumfromtxt')) is None:
                    oldnum = 0
                if oldnum != dfp.shape[0]:
                    dftmp = pd.read_excel(fna)
                    dfpall = dfp.append(dftmp).drop_duplicates().sort_values(['time'],
                                                                             ascending=False)
                    logstr = f"{fn}\t本地（文本文件）登记的记录数量为（{oldnum}），但新文本文件中" \
                        f"记录数量（{dfp.shape[0]}）条记录，" \
                        f"融合本地excel文件后记录数量为({dfpall.shape[0]})。覆盖写入所有新数据！"
                    log.info(logstr)
                    dfpall.to_excel(fna, engine='xlsxwriter', index=False)
                    setcfpoptionvalue('everwcitems', fn, 'itemsnumfromtxt',
                                      f"{dfp.shape[0]}")
                else:
                    print(f"{fn}已经存在，且文本文件中记录数量没有变化。")
            print(i, ny, dr[i], dr[i + 1], dfp.shape[0])
        print(f"{'-' * 15}\t{name}\t【{i + 1}/{len(dr) - 1}】\tDone!\t{'-' * 15}")


# %% [markdown]
# ### def getnotebookguid(notebookname)

# %%
def getnotebookguid(notebookname):
    """
    根据输入的笔记本名称返回相应的guid
    """
    ntfind =findnotebookfromevernote(notebookname)
    if ntfind.shape[0] == 0:
        notebookguid = createnotebook(notebookname)
#         print(notebookguid)
        setcfpoptionvalue('everwcitems', 'common', 'notebookguid', str(notebookguid))
    else:
        if (notebookguid := getcfpoptionvalue('everwcitems', 'common', 'notebookguid')) is None:
            notebookguid = ntfind.index[0]
#         print(notebookguid)
        setcfpoptionvalue('everwcitems', 'common', 'notebookguid', str(notebookguid))
        
    return notebookguid


# %% [markdown]
# ### def df2db(dftest, name, wcpath)

# %%
def df2db(dftest, name, wcpath):
    """
    把指定微信账号的记录df写入db相应表中
    """
    ny = dftest['time'].iloc[0].strftime("%y%m")
    dftfilename = f"wcitems_{name}_{ny}.xlsx"
    if (itemsnum_db := getcfpoptionvalue('everwcitems', dftfilename, 'itemsnum_db')) is None:
        itemsnum_db = 0
    itemnum = dftest.shape[0]
    if itemnum != itemsnum_db:
        starttime = dftest['time'].min().strftime("%F %T")
        endtime = dftest['time'].max().strftime("%F %T")
        loginstr = "" if (whoami := execcmd("whoami")) and (len(whoami) == 0) else f"{whoami}"
        dbfilename = f"wcitemsall_({getdevicename()})_({loginstr}).db".replace(" ", "_")
        dbname = wcpath / dbfilename
        with lite.connect(dbname) as conn:
            tablename = f"wc_{name}"
            csql = f"create table if not exists {tablename} " + f"(id INTEGER PRIMARY KEY AUTOINCREMENT, time DATETIME, send BOOLEAN, sender TEXT, type TEXT, content TEXT)"
            ifnotcreate(tablename, csql, dbname)
            cursor = conn.cursor()
            sql = f"select * from {tablename} where time between \'{starttime}\' and \'{endtime}\';"
            tb = cursor.execute(sql).fetchall()
            if len(tb) != itemnum:
                sqldel = f"delete from {tablename} where time between \'{starttime}\' and \'{endtime}\';"
                cursor.execute(sqldel)
                log.info(f"从数据库文件{dbname}的表{tablename}中删除{cursor.rowcount}条记录")
                dftest.to_sql(tablename, conn, if_exists="append", index=False)
                setcfpoptionvalue('everwcitems', dftfilename, 'itemsnum_db', str(itemnum))
                log.info(f"{dftfilename}的数据写入数据库文件（{dbname}）的（{tablename}）表中，并在ini登记数量（{itemnum}）") 


# %% [markdown]
# ### updatewcitemsxlsx2note(name, dftest, wcpath, notebookguid)

# %%
def updatewcitemsxlsx2note(name, dftest, wcpath, notebookguid):
    """
    处理从本地资源文件读取生成的df，如果和ini登记数量相同，则返回；如果不同，则从笔记端读取相应登记
    数量再次对比，相同，则跳过，如果不同，则拉取笔记资源文件和本地资源文件融合，更新笔记端资源文件并
    更新ini登记数量（用融合后的记录数量）
    """
    ny = dftest['time'].iloc[0].strftime("%y%m")
    dftfilename = f"wcitems_{name}_{ny}.xlsx"
    dftallpath = wcpath / dftfilename
    dftallpathabs = os.path.abspath(dftallpath)
    print(dftallpathabs)
    loginstr = "" if (whoami := execcmd("whoami")) and (len(whoami) == 0) else f"，登录用户：{whoami}"
    timenowstr =  pd.to_datetime(datetime.now()).strftime("%F %T")
    
    if (dftfileguid := getcfpoptionvalue('everwcitems', dftfilename, 'guid')) is None:
        findnotelst = findnotefromnotebook(notebookguid, dftfilename, notecount=1)
        if len(findnotelst) == 1:
            dftfileguid = findnotelst[0][0]
            log.info(f"数据文件《{dftfilename}》的笔记已经存在，取用")
        else:
            first_note_desc = f"账号\t{None}\n记录数量\t-1" # 初始化内容头部，和正常内容头部格式保持一致
            first_note_body = f"<pre>{first_note_desc}\n---\n\n本笔记创建于{timenowstr}，" \
                f"来自于主机：{getdevicename()}{loginstr}</pre>"
            dftfileguid = makenote2(dftfilename, notebody=first_note_body, parentnotebookguid=notebookguid).guid
        setcfpoptionvalue('everwcitems', dftfilename, 'guid', str(dftfileguid))

    df2db(dftest, name, wcpath)
    if (itemsnum_old := getcfpoptionvalue('everwcitems', dftfilename, 'itemsnum')) is None:
        itemsnum_old = 0
    itemnum = dftest.shape[0]
    if itemnum == itemsnum_old:
        log.info(f"{dftfilename}的记录数量（{itemnum}）和本地登记数量相同，跳过")
        return
    
    print(dftfileguid)
    if (itemsnum4net := getcfpoptionvalue('everwcitems', dftfilename, 'itemsnum4net')) is None:
        itemsnum4net = 0
    oldnotecontent = getnotecontent(dftfileguid).find("pre").text
    nrlst = oldnotecontent.split("\n---\n")
    itemsnumfromnet = int(re.search("记录数量\t(-?\d+)", nrlst[0]).groups()[0])
    if itemsnum4net == itemsnumfromnet == itemnum:
        log.info(f"本地资源的记录数量（{itemnum}），本地登记的记录数量（{itemsnum4net}）" \
                 f"和笔记中登记的记录数量（{itemsnumfromnet}）相同，跳过")
        return
    log.info(f"本地资源的记录数量（{itemnum}），登记的记录数量（{itemsnum4net}）" \
             f"和笔记中登记的记录数量（{itemsnumfromnet}）三不相同，从笔记端拉取融合")
    reslst = getnoteresource(dftfileguid)
    if len(reslst) != 0:
        dfromnote = pd.DataFrame()
        filetmp = wcpath / 'wccitems_from_net.xlsx'
        for res in reslst:
            fh = open(filetmp, 'wb')
            fh.write(res[1])
            fh.close()
            dfromnote = dfromnote.append(pd.read_excel(filetmp))
        dfcombine = dfromnote.append(dftest).drop_duplicates().sort_values(['time'], ascending=False)
        if dfcombine.shape[0] == itemsnumfromnet:
            log.info(f"本地数据文件记录有{itemnum}条，笔记中资源文件记录数为{itemsnumfromnet}条，合并后总记录数量{dfcombine.shape[0]}没变化，跳过")
            setcfpoptionvalue('everwcitems', dftfilename, 'itemsnum', str(itemsnumfromnet))
            setcfpoptionvalue('everwcitems', dftfilename, 'itemsnum4net', str(itemsnumfromnet))
            return
        log.info(f"本地数据文件记录数有{itemnum}条，笔记资源文件记录数为{itemsnumfromnet}条" \
                f"，合并后记录总数为：\t{dfcombine.shape[0]}")
        dftest = dfcombine
    df2db(dftest, name, wcpath)
    note_desc = f"账号\t{name}\n记录数量\t{dftest.shape[0]}"
    nrlst[0] = note_desc
    dftest_desc = f"更新时间：{timenowstr}\t" \
        f"记录时间自{dftest['time'].min()}至{dftest['time'].max()}，" \
        f"共有{dftest.shape[0]}条，来自主机：{getdevicename()}{loginstr}"
    nrlst[1] = f"{dftest_desc}\n{nrlst[1]}"
    resultstr = "\n---\n".join(nrlst)
    dftest.to_excel(dftallpathabs, engine='xlsxwriter', index=False)
    print(dftfileguid)
    updatereslst2note([dftallpathabs], dftfileguid, \
                      neirong=resultstr, filenameonly=True, parentnotebookguid=notebookguid)
    setcfpoptionvalue('everwcitems', dftfilename, 'itemsnum', str(dftest.shape[0]))
    setcfpoptionvalue('everwcitems', dftfilename, 'itemsnum4net', str(dftest.shape[0]))


# %% [markdown]
# ### def getnotelist(name)

# %%
@timethis
def getnotelist(name, wcpath, notebookguid):
    """
    根据传入的微信账号名称获得云端记录笔记列表
    """
    notelisttitle = f"微信账号（{name}）记录笔记列表"
    loginstr = "" if (whoami := execcmd("whoami")) and (len(whoami) == 0) else f"，登录用户：{whoami}"
    timenowstr =  pd.to_datetime(datetime.now()).strftime("%F %T")
    if (notelistguid := getcfpoptionvalue('everwcitems', "common", f"{name}_notelist_guid")) is None:
        findnotelst = findnotefromnotebook(notebookguid, notelisttitle, notecount=100)
        if len(findnotelst) == 1:
            notelistguid = findnotelst[0][0]
            log.info(f"文件列表《{notelisttitle}》的笔记已经存在，取用")
        else:
            nrlst = list()
            nrlst.append(f"账号\t{name}\n笔记数量\t-1") # 初始化内容头部，和正常内容头部格式保持一致
            nrlst.append("")
            nrlst.append(f"\n本笔记创建于{timenowstr}，来自于主机：{getdevicename()}{loginstr}")
            note_body_str = '\n---\n'.join(nrlst)
            note_body = f"<pre>{note_body_str}</pre>"
            notelistguid = makenote2(notelisttitle, notebody=note_body, parentnotebookguid=notebookguid).guid
            log.info(f"文件列表《{notelisttitle}》被首次创建！")
        setcfpoptionvalue('everwcitems', "common", f'{name}_notelist_guid', str(notelistguid))

    if (numatlocal := getcfpoptionvalue('everwcitems', "common", f"{name}_num_at_local")) is None:
        ptn = f"wcitems_{name}_" + "\d{4}.xlsx" # wcitems_heart5_2201.xlsx
        xlsxfllstfromlocal = [fl for fl in os.listdir(wcpath) if re.search(ptn, fl)]
        numatlocal = len(xlsxfllstfromlocal)
        setcfpoptionvalue('everwcitems', "common", f"{name}_num_at_local", str(numatlocal))
        log.info(f"首次运行getnotelist函数，统计微信账户《{name}》的本地资源文件数量存入本地ini变量中")
    notent = getnotecontent(notelistguid)
#     print(notent)
    if notent.find("pre") is None:
        nrlst = list()
        nrlst.append(f"账号\t{name}\n笔记数量\t-1") # 初始化内容头部，和正常内容头部格式保持一致
        nrlst.append("")
        nrlst.append(f"\n本笔记创建于{timenowstr}，来自于主机：{getdevicename()}{loginstr}")
        log.info(f"《{notelisttitle}》笔记内容不符合规范，重构之。【{nrlst}】")
    else:
        oldnotecontent = notent.find("pre").text
        nrlst = oldnotecontent.split("\n---\n")
#     print(nrlst)
    numinnotedesc = int(re.findall("\t(-?\d+)", nrlst[0])[0])
#     ptn = f"(wcitems_{name}_\d\d\d\d\.xlsx)\t(\S+)"
    ptn = f"(wcitems_{name}_" + "\d{4}.xlsx)\t(\S+)"
#     print(ptn)
    finditems = re.findall(ptn, nrlst[1])
    finditems = sorted(finditems, key=lambda x: x[0], reverse=True)
#     print(finditems)
    print(numinnotedesc, numatlocal, len(finditems))
    if numinnotedesc == numatlocal == len(finditems):
        log.info(f"《{notelisttitle}》中数量无更新，跳过。")
        return finditems
    findnotelstwithgtu = findnotefromnotebook(notebookguid, f"wcitems_{name}_", notecount=1000)
    findnotelst = [[nt[1], nt[0]] for nt in findnotelstwithgtu]
    findnotelst = sorted(findnotelst, key=lambda x: x[0], reverse=True)
    nrlst[0] = re.sub("\t(-?\d+)", "\t" + f"{len(findnotelst)}", nrlst[0])
    nrlst[1] = "\n".join(["\t".join(sonlst) for sonlst in findnotelst])
    nrlst[2] = f"更新于{timenowstr}，来自于主机：{getdevicename()}{loginstr}" + f"\n{nrlst[2]}"
    
    imglist2note(get_notestore(), [], notelistguid, notelisttitle,
                 neirong="<pre>" + "\n---\n".join(nrlst) + "</pre>", parentnotebookguid=notebookguid)
    numatlocal = len(finditems)
    setcfpoptionvalue('everwcitems', "common", f"{name}_num_at_local", str(numatlocal))
    
    return findnotelst


# %% [markdown]
# ### def merge2note(dfdict)

# %%
@timethis
def merge2note(dfdict, wcpath, notebookguid, newfileonly=False):
    """
    处理从文本文件读取生成的dfdict，分账户读取本地资源文件和笔记进行对照，并做相应更新或跳过
    """
    for name in dfdict.keys():
        fllstfromnote = getnotelist(name, wcpath, notebookguid=notebookguid)
        ptn = f"wcitems_{name}_" + "\d{4}.xlsx" # wcitems_heart5_2201.xlsx
        xlsxfllstfromlocal = [fl for fl in os.listdir(wcpath) if re.search(ptn, fl)]
        if len(fllstfromnote) != len(xlsxfllstfromlocal):
            print(f"{name}的数据文件本地数量\t{len(xlsxfllstfromlocal)}，云端笔记列表中为\t{len(fllstfromnote)}，" \
                  "两者不等，先把本地缺的从网上拉下来")
            misslstfromnote = [fl for fl in fllstfromnote if fl[0] not in xlsxfllstfromlocal]
            for fl, guid in misslstfromnote:
                reslst = getnoteresource(guid)
                if len(reslst) != 0:
                    for res in reslst:
                        flfull = wcpath / fl
                        fh = open(flfull, 'wb')
                        fh.write(res[1])
                        fh.close()
                        dftest = pd.read_excel(flfull)
                        setcfpoptionvalue('everwcitems', fl, 'guid', guid)
                        setcfpoptionvalue('everwcitems', fl, 'itemsnum', str(dftest.shape[0]))
                        setcfpoptionvalue('everwcitems', fl, 'itemsnum4net', str(dftest.shape[0]))
                        log.info(f"文件《{fl}》在本地不存在，从云端获取存入并更新ini（section：{fl}，guid：{guid}）")

        xlsxfllst = sorted([fl for fl in os.listdir(wcpath) if re.search(ptn, fl)])
        print(f"{name}的数据文件数量\t{len(xlsxfllst)}", end="，")
        if newfileonly:
            xlsxfllst = xlsxfllst[-2:]
        xflen = len(xlsxfllst)
        print(f"本次处理的数量为\t{xflen}")
        for xfl in xlsxfllst:
            print(f"{'-' * 15}\t{name}\t【{xlsxfllst.index(xfl) + 1}/{xflen}】\tBegin\t{'-' * 15}")
            dftest = pd.read_excel(wcpath / xfl).drop_duplicates()
            updatewcitemsxlsx2note(name, dftest, wcpath, notebookguid)
            print(f"{'-' * 15}\t{name}\t【{xlsxfllst.index(xfl) + 1}/{xflen}】\tDone!\t{'-' * 15}")


# %% [markdown]
# ### def refreshres(wcpath)

# %%
@timethis
def refreshres(wcpath):
    notebookname = "微信记录数据仓"
    notebookguid = getnotebookguid(notebookname)
    if (new := getinivaluefromnote('wcitems', 'txtfilesonlynew')) is None:
        new = False
#     new = True
    print(f"是否只处理新的文本文件：\t{new}")
    dfdict = txtfiles2dfdict(wcpath, newfileonly=new)
    for k in dfdict:
        dfinner = dfdict[k]
        print(f"{k}\t{dfinner.shape[0]}", end='\n\n')
        txtdfsplit2xlsx(k, dfinner, wcpath, newfileonly=new)

    merge2note(dfdict, wcpath, notebookguid, newfileonly=new)


# %% [markdown]
# ### def alldfdesc2note(name)

# %%
@timethis
def alldfdesc2note(wcpath):
    """
    读取本地所有资源文件的聊天记录到DataFrame中，输出描述性信息到相应笔记中
    """
    ptn4name = "wcitems_(\w+)_(\d{4}.xlsx)"
    names = list(set([re.search(ptn4name, fl).groups()[0] for fl in os.listdir(wcpath)
                if re.search(ptn4name, fl)]))
    print(names)
    loginstr = "" if (whoami := execcmd("whoami")) and (len(whoami) == 0) else f"{whoami}"
    dbfilename = f"wcitemsall_({getdevicename()})_({loginstr}).db".replace(" ", "_")
    dbname = wcpath / dbfilename
    resultdict = dict()
    for name in names[:]:
        with lite.connect(dbname) as conn:
            tbname = f"wc_{name}"
            sql = f"select * from {tbname}"
            finnaldf = pd.read_sql(sql, conn, 
                                   index_col=['id'], 
                                   parse_dates=['time'], 
                                   columns=['id', 'time', 'send' ,'sender', 'type', 'content'])
            finnaldf['send'] = finnaldf['send'].astype(bool)
            resultdict[name] = finnaldf
            print(f"{name}\t{finnaldf.shape[0]}")
    
    return resultdict


# %% [markdown]
# ## main，主函数

# %% jupyter={"outputs_hidden": true}
if __name__ == '__main__':
    if not_IPython():
        log.info(f'运行文件\t{__file__}')

    wcpath = getdirmain() / 'data' / 'webchat'
    refreshres(wcpath)
    mydict = alldfdesc2note(wcpath)

    if not_IPython():
        log.info(f"文件\t{__file__}\t运行结束。")

# %%
mydict = alldfdesc2note(wcpath)

# %%
name = 'heart5'
df = mydict[name]
df.dtypes

# %%
df.describe()

# %%
df.sort_values(['time'])
