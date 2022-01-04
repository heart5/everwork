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
# ## 库导入

# %%
import os
import re
import xlsxwriter
import pandas as pd
from pathlib import Path
from datetime import datetime

import pathmagic
with pathmagic.context():
    from func.first import getdirmain, touchfilepath2depth
    from func.logme import log
    from etc.getid import getdevicename
    from func.sysfunc import not_IPython, execcmd
    from func.configpr import setcfpoptionvalue, getcfpoptionvalue
    from func.evernttest import getinivaluefromnote, getnoteresource, \
        gettoken, get_notestore, getnotecontent, updatereslst2note, \
        createnotebook, makenote2, findnotebookfromevernote, findnotefromnotebook
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
#     ptn = re.compile("(^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\t(True|False)\t(\S+)\t(\S+)\t", re.M)
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
# ### def txtfiles2dfdict(wcdatapath)

# %%
def txtfiles2dfdict(dpath):
    fllst = [f for f in os.listdir(dpath) if f.startswith("chatitems")]
    
    def getownerfromfilename(fn):
        """
        从文件名中获取账号
        """
        ptn = re.compile("\((\w*)\)")
        ac = ac if (ac := re.search(ptn, fn).groups()[0]) not in ['', 'None'] else '白晔峰'
        return ac

    names = list(set([getownerfromfilename(nm) for nm in fllst]))
    print(names)
    # 如果设置为new，则找到每个账号的最新记录文件处理，否则是全部记录文件
    if (datafilesnew := getinivaluefromnote('wcitems', 'datafiles')) == 'new':
        nametimedict = dict()
        for nm in names:
            nametimedict[f"{nm}_newtime"] = datetime.fromtimestamp(0)
        for fl in fllst:
            flmtime = getfilemtime(dpath / fl)
            accounttmp = getownerfromfilename(fl)
            if flmtime > nametimedict[f"{accounttmp}_newtime"]:
                nametimedict[f"{accounttmp}_newtime"] = flmtime
                nametimedict[f"{accounttmp}_filename"] = fl
        fllst = [nametimedict[f"{nm}_filename"] for nm in names]
        fllst = [v for (k, v) in nametimedict.items() if k.endswith('filename')]

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
    start = start + pd.Timedelta(-1, 'sec')
    if start.strftime("%Y-%m") == end.strftime('%Y-%m'):
        drlst = [start, end]
    else:
        dr = pd.date_range(pd.to_datetime(start.strftime("%F 23:59:59")), end, freq='M')
        drlst = list(dr)
#         drlst.pop()
        drlst.insert(0, start)
        drlst.append(end)
    
    log.info(f"时间范围横跨{len(drlst) - 1}个月")
    return drlst


# %% [markdown]
# ### def splitdf(name, df, wcdatapath)

# %%
def txtdfsplit2xlsx(name, df, dpath):
    """
    按月份拆分从文本文件读取的指定账号的数据记录，存入对应格式化名称的excel表格中
    """
    dftimestart = df['time'].min()
    dftimeend = df['time'].max()
    dr = getdaterange(dftimestart, dftimeend)

    outlst = list()
    for i in range(len(dr) - 1):
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


# %% [markdown]
# ### def getnotebookguid(notebookname)

# %%
def getnotebookguid(notebookname):
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
# ### updatewcitemsxlsx2note(name, dftest, wcpath, notebookguid)

# %%
def updatewcitemsxlsx2note(name, dftest, wcpath, notebookguid):
    ny = dftest['time'].iloc[0].strftime("%y%m")
    dftfilename = f"wcitems_{name}_{ny}.xlsx"
    dftallpath = wcpath / dftfilename
    dftallpathabs = os.path.abspath(dftallpath)
    print(dftallpathabs)
    timenowstr =  pd.to_datetime(datetime.now()).strftime("%F %T")
    loginstr = "" if (whoami := execcmd("whoami")) and (len(whoami) == 0) else f"，登录用户：{whoami}"
    dftest_desc = f"更新时间：{timenowstr}\t" \
        f"记录时间自{dftest['time'].min()}至{dftest['time'].max()}，" \
        f"共有{dftest.shape[0]}条，来自主机：{getdevicename()}{whoami}"
    
    if (dftfileguid := getcfpoptionvalue('everwcitems', dftfilename, 'guid')) is None:
        findnotelst = findnotefromnotebook(notebookguid, dftfilename, notecount=1)
        if len(findnotelst) == 1:
            dftfileguid = findnotelst[0][0]
            log.info(f"数据文件《{dftfilename}》的笔记已经存在，取用")
        else:
            first_note_desc = f"账号\t{None}\n记录数量\t0" # 初始化内容头部，和正常内容头部格式保持一致
            first_note_body = f"<pre>{first_note_desc}\n---\n\n本笔记创建于{timenowstr}，来自于主机：{getdevicename()}</pre>"
            dftfileguid = makenote2(dftfilename, notebody=first_note_body, parentnotebookguid=notebookguid).guid
        setcfpoptionvalue('everwcitems', dftfilename, 'guid', str(dftfileguid))
    if (itemsnum_old := getcfpoptionvalue('everwcitems', dftfilename, 'itemsnum')) is None:
        itemsnum_old = 0
    itemnum = dftest.shape[0]
    if itemnum == itemsnum_old:
        log.info(f"{dftfilename}的记录数量和笔记相同，跳过")
        return
    
    print(dftfileguid)
    reslst = getnoteresource(dftfileguid)
    if len(reslst) != 0:
        dfromnote = pd.DataFrame()
        filetmp = wcpath / 'wccitems_from_net.xlsx'
        for res in reslst:
            fh = open(filetmp, 'wb')
            fh.write(res[1])
            fh.close()
            dfromnote = dfromnote.append(pd.read_excel(filetmp))
        numfromnet = dfromnote.drop_duplicates().shape[0]
        dfromnote = dfromnote.append(dftest).drop_duplicates().sort_values(['time'], ascending=False)
        if dfromnote.shape[0] == dftest.shape[0]:
            log.info(f"笔记中资源文件和本地文件合并后总记录数量{dftest.shape[0]}没变化，跳过")
            return
        log.info(f"本地数据文件记录数有{dftest.shape[0]}条，笔记资源文件记录数为{numfromnet}" \
                f"，合并后记录总数为：\t{dfromnote.shape[0]}")
        dftest = dfromnote
    oldnotecontent = getnotecontent(dftfileguid).find("pre").text
    nrlst = oldnotecontent.split("\n---\n")
    note_desc = f"账号\t{name}\n记录数量\t{dftest.shape[0]}"
    nrlst[0] = note_desc
    nrlst[1] = f"{dftest_desc}\n{nrlst[1]}"
    resultstr = "\n---\n".join(nrlst)
    dftest.to_excel(dftallpathabs, engine='xlsxwriter', index=False)
    print(dftfileguid)
    updatereslst2note([dftallpathabs], dftfileguid, \
                      neirong=resultstr, filenameonly=True, parentnotebookguid=notebookguid)
    setcfpoptionvalue('everwcitems', dftfilename, 'itemsnum', str(itemnum))


# %% [markdown]
# ### def merge2note(dfdict)

# %%
def merge2note(dfdict, wcpath, notebookguid):
    for name in dfdict.keys():
        ptn = f"wcitems_{name}_\d\d\d\d.xlsx"
        xlsxfllst = sorted([fl for fl in os.listdir(wcpath) if re.search(ptn, fl)])
        print(f"{name}的数据文件数量\t{len(xlsxfllst)}")
        for xfl in xlsxfllst:
            dftest = pd.read_excel(wcpath / xfl)
            updatewcitemsxlsx2note(name, dftest, wcpath, notebookguid)
    


# %% [markdown]
# ## main，主函数

# %%
if __name__ == '__main__':
    if not_IPython():
        log.info(f'运行文件\t{__file__}')

    wcpath = getdirmain() / 'data' / 'webchat'
    notebookname = "微信记录数据仓"
    notebookguid = getnotebookguid(notebookname)
    dfdict = txtfiles2dfdict(wcpath)
    for k in dfdict:
        dfinner = dfdict[k]
        print(f"{k}\t{dfinner.shape[0]}", end='\n\n')
        txtdfsplit2xlsx(k, dfinner, wcpath)
        
    merge2note(dfdict, wcpath, notebookguid)
    
    if not_IPython():
        log.info(f"文件\t{__file__}\t运行结束。")
