# encoding:utf-8
"""
获取火界麻将的比赛结果并输出
"""

import pandas as pd
import requests
import re
from bs4 import BeautifulSoup

import pathmagic

with pathmagic.context():
    from func.logme import log
    from func.evernttest import trycounttimes2, getinivaluefromnote
    from func.first import getdirmain, touchfilepath2depth
    from func.configpr import getcfpoptionvalue, setcfpoptionvalue


def find_class_in_tag(key: str, tags):
    resultlst = [x for x in tags if x.has_attr('class') and key in x['class']]
    # print(resultlst)
    if len(resultlst) > 0:
        return resultlst


@trycounttimes2('火界麻将服务器', 5, 50)
def getsinglepage(url: str):
    mjhtml = requests.get(url)
    mjhtml.encoding = mjhtml.apparent_encoding
    log.info(f"网页内容编码为：\t{mjhtml.encoding}")
    soup = BeautifulSoup(mjhtml.text, 'lxml')
    if souptitle := soup.title.text == "404 Not Found":
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
    clnames = ['roomid', 'time', 'guest', 'guestid', 'client', 'zimo', 'jingding', 'dianpao', 'laizigang', 'score',
               'host']
    rstdf = pd.DataFrame(resultlst, columns=clnames)
    # print(clnames)

    return rstdf


def fetchmjurl(owner):
    filename = getdirmain() / 'data' / 'webchat' / f"chatitems({owner}).txt"
    # print(filename)
    # http://s0.lgmob.com/h5_whmj_qp/zhanji/index.php?id=fks0_eb81c193dea882941fe13dfa5be24a11
    ptn = re.compile("h5_whmj_qp/zhanji/index.php\\?id=")
    # rstlst = []
    with open(filename, "r", encoding='utf-8') as f:
        filelines = f.readlines()
        rstlst = [line.split('Text\t')[1].strip() for line in filelines if re.findall(ptn, line)]

    return list(tuple(rstlst))


def getfangitem(line):
    # http://s0.lgmob.com/h5_whmj_qp/?d=217426
    ptn = re.compile("h5_whmj_qp/\\?d=(\\d+)")
    rstlst = [pd.to_datetime(line.split('\t')[0].strip()), int(re.findall(ptn, line.split('\t')[-1])[0])]

    return rstlst


def fetchmjfang(owner):
    """
    从文本档案库中提取开房信息（发布时间和房号）
    :param owner: 文本档案库的所属主人
    :return: DataFrame 开房信息df
    """
    filename = getdirmain() / 'data' / 'webchat' / f"chatitems({owner}).txt"
    # print(filename)
    # http://s0.lgmob.com/h5_whmj_qp/?d=217426
    ptn = re.compile("h5_whmj_qp/\\?d=(\\d+)")
    # line in txt
    # 2020-02-13 11:27:21	True	搓雀雀(群)白晔峰	Text	http://s0.lgmob.com/h5_whmj_qp/?d=852734
    with open(filename, "r", encoding='utf-8') as f:
        filelines = f.readlines()
        fanglst = [line.strip() for line in filelines if re.search(ptn, line)]
        rstlst = [[pd.to_datetime(lnspt[0]), re.findall(r'\b\w+\b', lnspt[2])[-1], int(lnspt[-1].split('=')[-1])] for
                  line in fanglst if (lnspt := line.split('\t'))]

    rstdf = pd.DataFrame(rstlst, columns=['time', 'name', 'roomid'])
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


def updateurllst(url):
    excelpath = getdirmain() / 'data' / 'muse' / 'huojiemajiang.xlsx'
    touchfilepath2depth(excelpath)
    excelwriter = pd.ExcelWriter(excelpath)
    roomid: str = '已处理'
    if readfrominiurls := getcfpoptionvalue('evermuse', 'huojiemajiang', 'zhanjiurls'):
        # 用\t标记无效的链接，这里做对比的时候需要去掉tab
        urlsrecord = [x.strip('\t') for x in readfrominiurls.split(',')]
        if url not in urlsrecord:
            rstdf = getsinglepage(url)
            roomid = rstdf.iloc[0, 0]
            if rstdf.shape[0] != 0:
                urlsrecord.insert(0, url)
                recorddf = pd.read_excel(excelpath)
                rstdf = recorddf.append(getsinglepage(url))
                rstdf.drop_duplicates(['roomid', 'time', 'guestid'], inplace=True)
                rstdf.sort_values(by=['time', 'score'], ascending=[False, False], inplace=True)
                # 修正用户别名
                rstdf = fixnamealias(rstdf, 'guest')
                rstdf.to_excel(excelwriter, index=False, encoding='utf-8')
                excelwriter.close()
                log.info(f"{rstdf.shape[0]}条记录写入文件\t{excelpath}")

            else:
                log.critical(f"这个网页貌似无效\t{url}")
                urlsrecord.insert(0, f"\t{url}")
            log.info(f"此将链接加入列表（现数量为{len(urlsrecord)}\t{url}")
            setcfpoptionvalue('evermuse', 'huojiemajiang', 'zhanjiurls', ','.join(urlsrecord))
        else:
            # log.info(f"此链接已经存在于列表中\t{url}")
            pass
    else:
        firstdf = getsinglepage(url)
        roomid = firstdf.iloc[0, 0]
        if firstdf.shape[0] != 0:
            urlsrecord = [url]
            # 修正用户别名
            firstdf = fixnamealias(firstdf, 'guest')
            firstdf.to_excel(excelwriter, index=False, encoding='utf-8')
            excelwriter.close()
            log.info(f"{firstdf.shape[0]}条记录写入文件\t{excelpath}")
        else:
            log.critical(f"这个网页貌似无效\t{url}")
            urlsrecord = [f"\t{url}"]

        log.info(f"第一条链接加入列表\t{url}")
        setcfpoptionvalue('evermuse', 'huojiemajiang', 'zhanjiurls', ','.join(urlsrecord))

    return roomid


def fixnamealias(inputdf: pd.DataFrame, clname: str):
    '''
    更新df中的别名为规范名称
    :param inputdf:
    :param clname:
    :return:
    '''
    rstdf: pd.DataFrame = inputdf.copy(deep=True)
    print(rstdf.dtypes)
    print(rstdf.groupby(clname).first().index.values)
    for name in rstdf.groupby(clname).first().index.values:
        if namez := getinivaluefromnote('game', name):
            namedf = rstdf[rstdf[clname] == name]
            print(name, namez, namedf.shape[0])
            for ix in namedf.index:
                rstdf.loc[ix, [clname]] = namez

    return rstdf


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


def zhanjidesc(ownername, recentday: bool = True, simpledesc: bool = True):
    excelpath = getdirmain() / 'data' / 'muse' / 'huojiemajiang.xlsx'
    recorddf = pd.read_excel(excelpath)
    rstdf = recorddf.copy(deep=True)
    rstdf = fixnamealias(rstdf, 'guest')
    rstdf.drop_duplicates(['roomid', 'time', 'guestid'], inplace=True)
    rstdf.sort_values(by=['time', 'score'], ascending=[False, False], inplace=True)
    # print(rstdf.head())
    # print(rstdf.dtypes)

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
    fangfinaldf.to_csv(csvfile := touchfilepath2depth(getdirmain() / 'data' / 'game' / 'huojiemajiangfang.csv'))

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

    # 根据开关，选择输出当天或者全部数据结果
    if recentday:
        zuijindatestart = pd.to_datetime(rstdf['time'].max().strftime("%Y-%m-%d"))
        rstdf = rstdf[rstdf.time >= zuijindatestart]
        fangfilter = fangfdf.apply(lambda x: x['mintime'] >= zuijindatestart or x['closetime'] >= zuijindatestart,
                                   axis=1)
        # print(fangfilter)
        fangfinaldf = fangfdf[fangfilter]
    print(fangfinaldf)
    print(rstdf)
    outlst = list()
    rgp = rstdf.groupby(['guest']).count()
    timeend = rstdf['time'].max().strftime("%y-%m-%d %H:%M")
    timestart = rstdf['time'].min().strftime("%y-%m-%d %H:%M")
    titlestr = f"战果统计（{timestart}至{timeend}）"
    outlst.append(titlestr)

    outlst.append(f"参战人数：\t{rgp.shape[0]}")
    fangtotalstr = f"（共开房{fangfinaldf.shape[0]}次）"
    outlst.append(f"进行圈数：\t{rstdf.groupby(['roomid']).count().shape[0]}\t{fangtotalstr}")

    def formatdfstr(ddf):
        return '\n'.join(str(ddf).split('\n')[1:-1])

    if shownumber := getinivaluefromnote('game', 'huojieshow'):
        pass
    else:
        shownumber = 3
    kaifang = rstdf[rstdf.host == True].groupby(['guest']).count()['host'].sort_values(ascending=False)
    outlst.append(f"开房积极分子排名：\n{formatdfstr(kaifang[:shownumber])}")
    zimo = rstdf.groupby(['guest']).sum()['zimo'].sort_values(ascending=False)
    outlst.append(f"自摸技术能手排名：\n{formatdfstr(zimo[:shownumber])}")
    dianpao = rstdf.groupby(['guest']).sum()['dianpao'].sort_values(ascending=False)
    outlst.append(f"最被吐槽的炮王排名：\n{formatdfstr(dianpao[:shownumber])}")
    jingding = rstdf.groupby(['guest']).sum()['jingding'].sort_values(ascending=False)
    outlst.append(f"最有含金量的金顶排名：\n{formatdfstr(jingding[:shownumber])}")

    teams = list(set(rstdf['guest']))
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
        print(player, laomoindexlst, laomofangdf)
        ptime = laomofangdf.sum()['playmin']
        playtimelst.append([player, ptime])

    playtimedf = pd.DataFrame(playtimelst, columns=['name', 'mins']).sort_values(['mins'], ascending=False)
    print(playtimedf)
    outlst.append(f"劳模榜（作战分钟数）：\n{formatdfstr(playtimedf[['name', 'mins']].reset_index(drop=True)[:shownumber + 1])}")

    outlst.append(f"\n{showhighscore(rstdf, highbool=False)}")
    outlst.append(f"\n{showhighscore(rstdf)}")

    shuyingdf = rstdf.groupby(['guest']).sum()
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


def updateallurlfromtxt(owner: str):
    # sp1 = "http://s0.lgmob.com/h5_whmj_qp/zhanji/index.php?id=fks0_2ba66d661e4c7712d0e6bcd3a6df255f"
    # sp2 = "http://s0.lgmob.com/h5_whmj_qp/zhanji/index.php?id=fks0_46247683e1b6e744ad956041ab2579a6"
    # sp3 = "http://s0.lgmob.com/h5_whmj_qp/zhanji/index.php?id=fks0_62a635b6dc15b34b74527550cd88d83f"
    # splst = [sp1, sp2, sp3]
    splst = fetchmjurl(owner)
    for sp in splst[:4]:
        print(sp)

    for sp in splst:
        updateurllst(sp)


if __name__ == '__main__':
    log.info(f'运行文件\t{__file__}')

    own = '白晔峰'

    # fangdf = fetchmjfang(own)
    # print(fangdf)

    updateallurlfromtxt(own)
    rst = zhanjidesc(own, True, False)
    print(rst)

    log.info(f'文件{__file__}运行结束')
