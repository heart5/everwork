# encodin:utf-8
# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     formats: ipynb,py
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.10.1
# ---

"""
获取火界麻将的比赛结果并输出
"""

import pandas as pd
import matplotlib.pyplot as plt
import os
import requests
import re
from bs4 import BeautifulSoup
from xpinyin import Pinyin

import pathmagic

with pathmagic.context():
    from func.logme import log
    from func.evernttest import trycounttimes2, getinivaluefromnote
    from func.first import getdirmain, touchfilepath2depth
    from func.configpr import getcfpoptionvalue, setcfpoptionvalue, getcfp
    from func.datetimetools import getstartdate
    from func.sysfunc import not_IPython


def find_class_in_tag(key: str, tags):
    resultlst = [x for x in tags if x.has_attr('class') and key in x['class']]
    # print(resultlst)
    if len(resultlst) > 0:
        return resultlst


@trycounttimes2('火界麻将服务器', 17, 50)
def getsinglepage(url: str):
    mjhtml = requests.get(url)
    mjhtml.encoding = mjhtml.apparent_encoding
    log.info(f"网页内容编码为：\t{mjhtml.encoding}")
    soup = BeautifulSoup(mjhtml.text, 'lxml')
    if (souptitle := soup.title.text) == "404 Not Found":
        print(f"该网页无有效内容返回或者已经不存在\t{url}")
        return pd.DataFrame()
    else:
        print(souptitle)

    headdiv = soup.header.find_all('div')
    # print(headdiv)
    roomid = find_class_in_tag('title_num', headdiv)[0].text.split(':')[1].strip()
    roomtime = find_class_in_tag('title_time', headdiv)[0].text.split(':', 1)[1].strip()
    roomtime = pd.to_datetime(roomtime)
    # print(roomid, roomtime)
    t_c_tags = soup.find_all('div')
    gamelist = [x for x in t_c_tags if x.has_attr('class') and 'game_list' in x['class']]
    ptn = re.compile('^[+-]?\\d+$')
    resultlst = []
    for gl in gamelist:
        itemlst = list()
        itemlst.append(roomid)
        itemlst.append(roomtime)
        # 房间信息
        person_p = [x.text for x in find_class_in_tag('order_gInfor_p', gl.find_all('p'))]
        itemlst.extend(person_p)
        # 比赛结果
        person_t = [x.text.split(' ')[1].strip() for x in find_class_in_tag('order_gInfor_t', gl.find_all('p'))]
        # ['来源 微信登陆', '自摸 2', '金顶 2', '点炮 1', '赖子杠 ', '总分 114']
        # ['微信登陆', '1', '2', '1', '', '-14']
        # print(person_t)
        # person_t = [person_t[0]].extend([int(x) for x in person_t[1:]])
        # print(person_t)
        itemlst.extend(person_t)
        person_f = find_class_in_tag('main_img', gl.find_all('div'))
        if person_f:
            itemlst.append(True)
        else:
            itemlst.append(False)

        # print(itemlst)
        def toint(x):
            if type(x) != str:
                # print(x, type(x))
                return x
            if re.findall(ptn, x):
                return int(x)
            else:
                return x

        itemlstout = list(map(toint, itemlst))
        resultlst.append(itemlstout)
    # print(gamelist)
    # ['945901', '2020/02/12 12:05:31', '白晔峰', '1080972', '微信登陆', '2', '2', '1', '', '114', '房主']
    clnames = ['roomid', 'time', 'guest', 'guestid', 'client', 'zimo', 'jingding', 'dianpao', 'laizigang', 'score', 'host']
    rstdf = pd.DataFrame(resultlst, columns=clnames)
    # print(clnames)

    return rstdf


def splitmjurlfromtext(incontent:str):
    """
    从输入文本中提取有效的url链接，返回包含有效链接的list
    **正则中的贪婪和非贪婪搞得一头包，慎之慎之**
    """
    # http://s0.lgmob.com/h5_whmj_qp/zhanji/index.php?id=fks0_eb81c193dea882941fe13dfa5be24a11
    # ptn = re.compile("h5_whmj_qp/zhanji/index.php\\?id=")
    #  '微信【Text】信息中发现新的火界麻将战绩网页链接并处理，房间号为：\t806666\thttp://s0.lgmob.com/h5_whmj_qp/zhanji/index.php?id=fks0_9b8bd588d1d44ae2867aa1319241881b'
    # ptn = re.compile("h5_whmj_qp/(zhanji/index.php\\?id=|fks0_)")
    # reg .+? 限制为非贪婪模式，用于提取文本多个有效连接
    ptn = re.compile("(http://.+?h5_whmj_qp/(?:zhanji/index.php\\?id=|fks0_)\S+)\s*")
    # rstlst = [inurl for inurl in vurl if (vurl := re.findall(ptn, incontent))]
    if (vurl := re.findall(ptn, incontent)):
        return [url for url in vurl]
    else:
        return list()


def fetchmjurlfromfile(ownername):
    """
    fetch all zhanji urls from chatitems files
    """
    ownpy = Pinyin().get_pinyin(ownername, '')
    datapath = getdirmain() / 'data' / 'webchat'
    datafilelist = os.listdir(datapath)
    print(datapath)
    resultlst = list()
    for filenameinner in datafilelist:
        if not filenameinner.startswith('chatitems'):
            continue
        filename = datapath / filenameinner
        rstlst = []

        decode_set = ['utf-8', 'gb18030', 'ISO-8859-2', 'gb2312', 'gbk', 'Error']
        for dk in decode_set:
            try:
                with open(filename, "r", encoding='utf-8') as f:
                    filelines = f.readlines()
                    rstlstraw = [inurl for line in filelines for inurl in splitmjurlfromtext(line)]
                    # drops the duplicates url
                    rstlst = list(tuple(rstlstraw))
                    print(len(rstlst), len(rstlstraw), filename, dk)
                    break
            except UnicodeDecodeError as eef:
                continue
            except LookupError as eel:
                if dk == 'Error':
                    print(f"{filename}没办法用预设的集中字符集正确打开")
                break

        resultlst.extend(rstlst)

    resultlst = list(tuple(resultlst))
    # print(resultlst[:10])
    if (urlsnum:=getcfpoptionvalue(f'evermuse_{ownpy}',ownername, 'urlsnum')):
        if urlsnum == len(resultlst):
            changed = False
            log.info(f"战绩链接数量暂无变化, till then is {len(resultlst)}.")
        else:
            changed = True
            setcfpoptionvalue(f'evermuse_{ownpy}',ownername, 'urlsnum', f"{len(resultlst)}")
    else:
        urlsnumnew = len(resultlst)
        setcfpoptionvalue(f'evermuse_{ownpy}',ownername, 'urlsnum', f"{urlsnumnew}")
        changed = True
        log.info(f"战绩链接数 is set to {urlsnumnew} at first time.")

    return resultlst, changed


def getfangitem(line):
    # http://s0.lgmob.com/h5_whmj_qp/?d=217426
    ptn = re.compile("h5_whmj_qp/\\?d=(\\d+)")
    rstlst = [pd.to_datetime(line.split('\t')[0].strip()), int(re.findall(ptn, line.split('\t')[-1])[0])]

    return rstlst


def fetchmjfang(owner):
    """
    从数据目录中符合命名标准的文本档案库中提取开房信息（发布时间和房号）
    param owner: 文本档案库的所属主人
    return: DataFrame 开房信息df
    """
    datapath = getdirmain() / 'data' / 'webchat'
    datafilelist = os.listdir(datapath)
    resultlst = list()
    # http://s0.lgmob.com/h5_whmj_qp/?d=217426
    ptn = re.compile("h5_whmj_qp/\\?d=(\\d+)")
    for filenameinner in datafilelist:
        if not filenameinner.startswith('chatitems'):
            continue
        filename = datapath / filenameinner
        rstlst = []

        decode_set = ['utf-8', 'gb18030', 'ISO-8859-2', 'gb2312', 'gbk', 'Error']
        for dk in decode_set:
            try:
                with open(filename, "r", encoding=dk) as f:
                    filelines = f.readlines()
                    # 2020-02-13 11:27:21	True	搓雀雀(群)白晔峰	Text	http://s0.lgmob.com/h5_whmj_qp/?d=852734
                    fanglst = [line.strip() for line in filelines if re.search(ptn, line)]
                    rstlst = [[pd.to_datetime(lnspt[0]), re.findall(r'\b\w+\b', lnspt[2])[-1], int(lnspt[-1].split('=')[-1])] for
                              line in fanglst if (lnspt := line.split('\t'))]
                    print(filename, dk)
                    break
            except UnicodeDecodeError as eef:
                continue
            except LookupError as eel:
                if dk == 'Error':
                    print(f"{filename}没办法用预设的集中字符集正确打开")
                break

        resultlst.extend(rstlst)

    resultlst = list(tuple(resultlst))
    ownpy = Pinyin().get_pinyin(owner, '')
    if (urlsnum:=getcfpoptionvalue(f'evermuse_{ownpy}', 'huojiemajiang', 'fangsnum')):
        if urlsnum == len(resultlst):
            log.info(f"战绩链接数量暂无变化, till then is {lwn(urlsnum)}.")
        else:
            setcfpoptionvalue('evermuse_{ownpy}', 'huojiemajiang', 'fangsnum', f"{len(resultlst)}")
            log.info(f"战绩链接数量变化, from {urlsnum} to {len(resultlst)}.")
    else:
        urlsnum = len(resultlst)
        setcfpoptionvalue('evermuse_{ownpy}', 'huojiemajiang', 'fangsnum', f"{len(resultlst)}")
        log.info(f"战绩链接 size is set to {urlsnum} at fiest time.")

    rstdf = pd.DataFrame(resultlst, columns=['time', 'name', 'roomid'])
    # print(rstdf)
    # 房号发布次数
    countdf = rstdf.groupby('roomid')['time'].count()
    # print(countdf)
    # 房号发布最近时间
    maxtimedf = rstdf.groupby('roomid')['time'].max()
    # 房号发布最早时间
    mintimedf = rstdf.groupby('roomid')['time'].min()
    # 房号发布人
    namedf = rstdf.groupby('roomid')['name'].last()

    cdf = pd.concat([countdf, maxtimedf, mintimedf, namedf], axis=1)
    # print(cdf)
    cleandf = cdf
    cleandf.columns = ['count', 'maxtime', 'mintime', 'name']
    cleandf['consumemin'] = (cleandf['maxtime'] - cleandf['mintime']).map(lambda x: int(x.total_seconds() / 60))

    return cleandf.sort_values('mintime', ascending=False)


def updateurllst(ownername, urllst):
    """
    成组更新url列表
    """
    rstlst = list()
    for url in urllst:
        rstlst.append(updateurl2excelandini(ownername, url))

    return '\n'.join(rstlst)


def makeexcelfileownpy(ownername):
    """
    init excelpath, and ownername in pinyin
    """
    ownpy = Pinyin().get_pinyin(ownername, '')
    excelpath = getdirmain() / 'data' / 'muse' / f'huojiemajiang_{ownpy}.xlsx'
    touchfilepath2depth(excelpath)
    if not excelpath.exists():
        excelwriter = pd.ExcelWriter(excelpath)
        clnames = ['roomid', 'time', 'guest', 'guestid', 'client', 'zimo', 'jingding', 'dianpao', 'laizigang', 'score', 'host']
        rstdf = pd.DataFrame(list(), columns=clnames)
        rstdf.to_excel(excelwriter, index=False, encoding='utf-8')
        excelwriter.close()

    return excelpath, ownpy


def geturlcontentwrite2excel(ownername, url):
    """
    处理url，提取网页内容，有效数据写入数据文件，return url valid, if not valid, [url]
    """
    excelpath, ownpy = makeexcelfileownpy(ownername)
    tdf = getsinglepage(url)
    print(tdf)
    if tdf.shape[0] > 0:
        roomid = tdf.iloc[0, 0]
        recorddf = pd.read_excel(excelpath)
        #vdrop dupliceres at first, I studun there for many times
        recorddf.drop_duplicates(['roomid', 'time', 'guestid'], inplace=True)
        oldsize = recorddf.shape[0]
        rstdf = recorddf.append(tdf)
        # 修正用户别名
        rstdf = fixnamebyguestid(rstdf, 'guestid')
        rstdf.sort_values(by=['time', 'score'], ascending=[False, False], inplace=True)
        rstdf.drop_duplicates(['roomid', 'time', 'guestid'], inplace=True)
        print(rstdf)
        if rstdf.shape[0] == oldsize:
            descstr = f"room {roomid} is already recorded. till then the recordsize is {oldsize}"
            log.warning(descstr)
        else:
            excelwriter = pd.ExcelWriter(excelpath)
            rstdf.to_excel(excelwriter, index=False, encoding='utf-8')
            excelwriter.close()
            descstr = f"{rstdf.shape[0]}条记录写入文件\t{excelpath}, new roomid {roomid} record done now.\n{tdf[['guest', 'score']]}"
            log.info(descstr)
        outurl = url
    else:
        descstr = f"no valid content there, 这个网页貌似无效\t{url}"
        log.critical(descstr)
        outurl = f"[{url}]"

    return outurl, descstr


def updateurl2excelandini(ownername, url):
    """
    处理url，提取网页内容，有效数据写入数据文件，并更新相应配套ini辅助文件
    """
    ptn = re.compile("(http://.+?h5_whmj_qp/(?:zhanji/index.php\\?id=|fks0_)\S+)\s*")
    if (urlst := re.findall(ptn, url)):
        url = urlst[0]
    else:
        log.critical(f"无效网址连接：\t{url}, 不做处理，直接返回NOne")
        return

    excelpath, ownpy = makeexcelfileownpy(ownername)
    if (readfrominiurls:=getcfpoptionvalue(f'evermuse_{ownpy}', ownername, 'zhanjiurls')):
        readfrominiurlslst = list(tuple(readfrominiurls.split(','))) # drop duplicetes
    else:
        readfrominiurlslst = list() 
    # 用[]标记无效的链接，这里做对比的时候需要去掉
    urlsrecord = [x.strip('[]') for x in readfrominiurls]
    if (url not in urlsrecord):
        inurl, descstr = geturlcontentwrite2excel(ownername, url)
        readfrominiurlslst.insert(0, inurl)
        descstr += f"\n此链接加入列表（现数量为{len(readfrominiurls)})\t{url}"
        setcfpoptionvalue(f'evermuse_{ownpy}', ownername, 'zhanjiurls', ','.join(readfrominiurlslst))
    elif(url in urlsrecord):
        descstr = f"此链接已经存在于列表中（现数量为{len(readfrominiurls)})\t{url}"
        log.info(f"{descstr}")

    return descstr


def fixnamealias(inputdf: pd.DataFrame, clname: str):
    '''
    更新df中的别名为规范名称
    :param inputdf:
    :param clname:
    :return:
    '''
    rstdf1: pd.DataFrame = inputdf.copy(deep=True)
    # print(rstdf1.dtypes)
    namelst = rstdf1.groupby(clname).first().index.values
    # print(namelst)
    cfpini, cfpinipath = getcfp('everinifromnote')
    gamedict = dict(cfpini.items('game'))
    print(f"id to name correctring...")
    for name in namelst:
        if name in gamedict.keys():
            namez = gamedict[name]
            namedf = rstdf1[rstdf1[clname] == name].copy(deep=True)
            print(name, namez, namedf.shape[0])
            # print(namedf)
            for ix in namedf.index:
                rstdf1.loc[ix, [clname]] = namez

    return rstdf1


def fixnamebyguestid(inputdf: pd.DataFrame, guestidcl: str):
    rstdf1: pd.DataFrame = inputdf.copy(deep=True)
    # print(rstdf1.dtypes)
    guestidalllst = rstdf1.groupby(guestidcl).first().index.values
    # print(guestidalllst)
    gidds = rstdf1.groupby(['guestid', 'guest']).count().groupby(level='guestid').count()['roomid']
    guestidlst = [str(guestid) for guestid in gidds[gidds > 1].index]
    # print(guestidlst)
    cfpini, cfpinipath = getcfp('everinifromnote')
    gamedict = dict(cfpini.items('game'))
    print(f"name correctted by id from evernote ini...")
    for nameid in guestidlst:
        if nameid in gamedict.keys():
            namez = gamedict[nameid]
            needdf = rstdf1[rstdf1.guestid == int(nameid)]
            print(nameid, namez, needdf.shape[0])
            rstdf1.loc[list(needdf.index), 'guest'] = namez

    return rstdf1


def showhighscore(rstdf, highbool: bool = True):
    """
    统计输入df的赛事单局最高分或最低分对局信息
    :param rstdf:
    :param highbool:
    :return:
    """
    highscore = (rstdf['score'].min(), rstdf['score'].max())[highbool]
    outlst = list()
    title = ('赛事暗黑', '赛事高亮')[highbool]
    outlst.append(title)
    for idh in rstdf[rstdf['score'] == highscore]['roomid'].values:
        iddf = rstdf[rstdf.roomid == idh]
        outstr = '赛事时间：'
        outstr += iddf['time'].max().strftime('%m-%d %H:%M')
        dayingjialst = iddf[iddf.score == highscore]['guest'].values
        dayingjiastr = ('大输家', '大赢家')[highbool]
        outstr += f'，{dayingjiastr}：{dayingjialst}'
        highstr = ('输的最惨', '赢得高分')[highbool]
        outstr += f'，{highstr}：{highscore}'
        tongjuguest = iddf[~iddf['guest'].isin(dayingjialst)]['guest'].values
        tongjustr = ('同局共坑', '同局共奉')[highbool]
        outstr += f'，{tongjustr}兄：{tongjuguest}'
        outlst.append(outstr)
    outputstr = '\n'.join(outlst)

    return outputstr


def zhanjidesc(ownername, recentday: str = '日', simpledesc: bool = True):
    excelpath, ownpy = makeexcelfileownpy(ownername)
    print(excelpath, ownpy)
    recorddf = pd.read_excel(excelpath)
    rstdf = recorddf.copy(deep=True)
    # print(rstdf.groupby(['guestid', 'guest']).count())
    rstdf = fixnamebyguestid(rstdf, 'guestid')
    rstdf.drop_duplicates(['roomid', 'time', 'guestid'], inplace=True)
    rstdf.sort_values(by=['time', 'score'], ascending=[False, False], inplace=True)
    # print(rstdf.head())
    # print(rstdf.dtypes)
    # print(rstdf.groupby(['guestid', 'guest']).count())

    fangdf = fetchmjfang(ownername)
    fangdf = fixnamealias(fangdf, 'name')
    # print(fangdf.dtypes)
    fangclosedf = rstdf.groupby('roomid')['time'].max()
    # print(fangclosedf)
    # 以房号为索引进行数据合并，默认join='outer'
    fangfinaldf: pd.DataFrame = pd.concat([fangdf, fangclosedf], axis=1).sort_values(by=['mintime'], ascending=False)
    fangfinaldf = fangfinaldf.rename(columns={'time': 'closetime'})
    # print(fangfinaldf) fangfinaldf.loc[:, 'playmin'] = fangfinaldf.apply(lambda df: int((df['closetime'] - df[
    # 'maxtime']).total_seconds() / 60) if df['closetime'] else pd.NaT, axis=1)
    fangfinaldf.loc[:, 'playmin'] = fangfinaldf.apply(
        lambda df: (df['closetime'] - df['maxtime']).total_seconds() // 60 if df['closetime'] else pd.NaT, axis=1)
    # print(fangfinaldf[fangfinaldf['mintime'].isnull()])

    # 根据对局战绩修正房主信息
    rstdfroomhost = rstdf[rstdf.host].groupby('roomid')['guest'].first()
    for ix in list(rstdfroomhost.index.values):
        hostname = rstdfroomhost[ix]
        fangfinaldf.loc[ix, 'name'] = hostname

    # 代开房间房主信息处理
    dkds = rstdf.groupby(['roomid', 'host']).count()['guest']
    for r, h in list(dkds[dkds % 4 == 0].index):
        # 回填战绩df的host栏目
        luckyguy = rstdf.groupby('roomid').first()['guest'].loc[r]
        ixforluckguy = rstdf[(rstdf.roomid == r) & (rstdf.guest == luckyguy)].index
        rstdf.loc[ixforluckguy, 'host'] = True
        print(ixforluckguy)
        # 完善开房信息
        fangfinaldf.loc[r, 'name'] = luckyguy
        print(f"房间信息数据结构：\t{list(fangfinaldf.columns)}")
        print(f"代开房间号：\t{r}, 房间信息：\t{list(fangfinaldf.loc[r])}")

    # 中断牌局，只取最终结果
    zdds = rstdf.groupby('roomid').count()['time']
    for ix in list(zdds[zdds > 4].index):
        time2keep = rstdf.groupby('roomid').max()['time'].loc[ix]
        time2drop = rstdf.groupby('roomid').min()['time'].loc[ix]
        print(f"续局房号：\t{ix}，记录共有{zdds[ix]}条，需删除时间点\t{time2drop}，保留的终局时间点为：\t{time2keep}")
        rstdf = rstdf[rstdf.time != time2drop]

    fangfinaldf.to_csv(csvfile:=touchfilepath2depth(getdirmain() / 'data' / 'game' / 'huojiemajiangfang.csv'))

    fangfdf = fangfinaldf.copy(deep=True)

    # 找到那些没有开局链接的局，按照其他局的平均时间赋值，同时更新count、maxtime、mintime、consumemin、name的列值

    # 平均对局时长（分钟）
    playminmean = int(fangfdf['playmin'].mean())
    # 没有开局链接的局
    fangffix = fangfdf[fangfdf['playmin'].isnull() & fangfdf['count'].isnull()]
    # 用平均用时完善数据集
    for index in fangffix.index:
        fangfdf.loc[index, ['maxtime']] = fangfdf.loc[index, ['closetime']][0] - pd.to_timedelta(f'{playminmean}min')
        fangfdf.loc[index, ['mintime']] = fangfdf.loc[index, ['maxtime']][0]
        fangfdf.loc[index, ['count']] = 1
        fangfdf.loc[index, ['name']] = rstdf[rstdf.host].set_index('roomid').loc[index, ['guest']][0]
        fangfdf.loc[index, ['playmin']] = playminmean
        fangfdf.loc[index, ['consumemin']] = 0

    fangfinaldf = fangfdf.sort_values(['mintime'], ascending=False)

    if (zuijindatestart:=getstartdate(recentday, rstdf['time'].max())) != rstdf['time'].max():
        rstdf = rstdf[rstdf.time >= zuijindatestart]
        fangfilter = fangfdf.apply(lambda x: x['mintime'] >=
                                   zuijindatestart or x['closetime'] >= zuijindatestart, axis=1)
        # print(fangfilter)
        fangfinaldf = fangfdf[fangfilter]
    # print(fangfinaldf)
    # print(rstdf)
    outlst = list()
    rgp = rstdf.groupby(['guest']).count()
    timeend = rstdf['time'].max().strftime("%y-%m-%d %H:%M")
    timestart = rstdf['time'].min().strftime("%y-%m-%d %H:%M")
    titlestr = f"战果统计（{timestart}至{timeend}）"
    outlst.append(titlestr)
    outlst.append(f"{recentday}战报*" * 5)

    renshu = rgp.shape[0]
    print(f"人数共有：\t{renshu}")
    outlst.append(f"参战人数：\t{renshu}")
    fangtotalstr = f"（共开房{fangfinaldf.shape[0]}次）"
    outlst.append(f"进行圈数：\t{rstdf.groupby(['roomid']).count().shape[0]}\t{fangtotalstr}")

    def formatdfstr(ddf):
        return '\n'.join(str(ddf).split('\n')[1:-1])

    if simpledesc:
        if (shownumber:= getinivaluefromnote('game', 'huojieshow')):
            pass
        else:
            shownumber = 3
    else:
        shownumber = renshu

    kaifang = rstdf[rstdf.host == True].groupby(['guest']).count()['host'].sort_values(ascending=False)
    outlst.append(f"开房积极分子排名：\n{formatdfstr(kaifang[:shownumber])}")
    zimo = rstdf.groupby(['guest']).sum()['zimo'].sort_values(ascending=False)
    outlst.append(f"自摸技术能手排名：\n{formatdfstr(zimo[:shownumber])}")
    dianpao = rstdf.groupby(['guest']).sum()['dianpao'].sort_values(ascending=False)
    outlst.append(f"最被吐槽的炮王排名：\n{formatdfstr(dianpao[:shownumber])}")
    jingding = rstdf.groupby(['guest']).sum()['jingding'].sort_values(ascending=False)
    outlst.append(f"最有含金量的金顶排名：\n{formatdfstr(jingding[:shownumber])}")

    teams = list(tuple(rstdf['guest']))
    print(teams)
    playtimelst = []
    for player in teams:
        # playerindexlst = rstdf[rstdf.guest == player][['roomid']].values
        # print(playerindexlst)
        # """
        # [[498293]
        #  [891773]
        #  [891773]
        #  [800278]
        #  [800278]]
        # """
        # laomoindex = [x for item in playerindexlst for x in item]
        # # 用多层列表解析解决index提取问题，得到结果：[498293, 891773, 891773, 800278, 800278]

        # 愚蠢谨记！提取列数据时多套了一层方括号
        laomoindexlst = list(rstdf[rstdf.guest == player]['roomid'])
        laomofangdf = fangfinaldf.loc[laomoindexlst]
        # print(player, laomoindexlst, laomofangdf)
        ptime = laomofangdf.sum()['playmin']
        playtimelst.append([player, ptime])

    playtimedf = pd.DataFrame(playtimelst, columns=['name', 'mins']).sort_values(['mins'], ascending=False)
    print(playtimedf)
    outlst.append(f"劳模榜（作战分钟数）：\n{formatdfstr(playtimedf[['name', 'mins']].reset_index(drop=True)[:shownumber + 1])}")

    outlst.append(f"\n{showhighscore(rstdf, highbool=False)}")
    outlst.append(f"\n{showhighscore(rstdf)}")

    shuyingdf = rstdf.groupby(['guest']).sum()
    # 综合则输出全部输赢信息
    if simpledesc:
        shuyingdf = shuyingdf[shuyingdf.score > 0]
    shuying = shuyingdf['score'].sort_values(ascending=False)
    shuyingstr = f"大赢家光荣榜：\n{formatdfstr(shuying[:shownumber])}"
    outlst.append(shuyingstr)

    # 根据开关，输出简版输赢信息
    if simpledesc:
        outstr = titlestr + '\n' + shuyingstr
        return outstr

    outstr = '\n\n'.join(outlst)

    return outstr


def showzhanjiimg(ownername, recentday="日", jingdu: int = 300):
    excelpath, ownpy = makeexcelfileownpy(ownername)
    recorddf = pd.read_excel(excelpath)
    rstdf = recorddf.copy(deep=True)
    if (zuijindatestart:=getstartdate(recentday, rstdf['time'].max())) != rstdf['time'].max():
        rstdf = rstdf[rstdf.time >= zuijindatestart]
    zgridf = rstdf.groupby([pd.to_datetime(rstdf['time'].dt.strftime("%Y-%m-%d")), rstdf.guest]
                           ).sum().reset_index('guest', drop=False)[['guest', 'score']].sort_index()

    # register_matplotlib_converters()
    plt.style.use("ggplot")  # 使得作图自带色彩，这样不用费脑筋去考虑配色什么的；
    for person in set(list(zgridf.guest.values)):
        pzgr = zgridf[zgridf.guest == person]['score'].cumsum()
    #     print(person, pzgr)
        pzgr.name = person
        pzgr.plot(legend=True)

    plt.title(f"[[{recentday}]]战绩累积图")

    imgwcdelaypath = touchfilepath2depth(
        getdirmain() / "img" / "webchat" / "zhanjicum.png"
    )

    plt.savefig(imgwcdelaypath, dpi=jingdu)
    print(os.path.relpath(imgwcdelaypath))

    return imgwcdelaypath


def updateallurlfromtxt(owner: str, startnum=0, itemsnnm=10):
    """
    从文本文件中读取所有url并更新入数据表格文件
    """
    spls, change = fetchmjurlfromfile(owner)
    if splst and len(splst) != 0:
        print(len(splst), startnum, itemsnnm)
        endnum = tmpend if (tmpend := (startnum + itemsnnm)) < len(splst) else len(splst)
        print(len(splst), startnum, endnum)
        targetlst = splst[startnum:(endnum)]

        # print(f"\n\n\nwrite to excel using updateurllst fucntion\n\n\n")
        # updateurllst(owner, targetlst)

        # 强制更新所有链接数据
        print(f"\n\n\nwrite to excel using geturlcontentwrite2excel fucntion\n\n\n")
        for ii in range(startnum, endnum):
            url, desc = geturlcontentwrite2excel(owner, targetlst[ii])
            print(f"[{startnu}/{ii}/{endnum}]\t{desc}")


if __name__ == '__main__':
    if not_IPython():
        log.info(f'运行文件\t{__file__}')

    own = '白晔峰'
    own = 'heart5'

    # fangdf = fetchmjfang(own)
    # print(fangdf)

    # sp1 = "http://s0.lgmob.com/h5_whmj_qp/zhanji/index.php?id=fks0_5b4e07f2d3ef0c67735426b3239dfe96"
    # sp2 = "http://s0.lgmob.com/h5_whmj_qp/zhanji/index.php?id=fks0_bc3c4f643d3c5317202550bc17c4864c"
    # updateurl2excelandini(own, sp2)
    # geturlcontentwrite2excel(own, sp2)

    updateallurlfromtxt(own, 0, 5)

    # img = showzhanjiimg(own)

    if not_IPython():
        log.info(f'文件{__file__}运行结束')
