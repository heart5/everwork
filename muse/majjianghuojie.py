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
    from func.evernttest import trycounttimes2
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
        return
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
    ptn = re.compile('^[+-]?\d+$')
    resultlst = []
    for gl in gamelist:
        itemlst = []
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
    print(filename)
    ptn = re.compile("h5_whmj_qp/zhanji/index.php\?id=")
    # rstlst = []
    with open(filename, "r", encoding='utf-8') as f:
        filelines = f.readlines()
        rstlst = [line.split('Text\t')[1].strip() for line in filelines if re.findall(ptn, line)]

    return list(tuple(rstlst))


def updateurllst(url):
    excelpath = getdirmain() / 'data' / 'muse' / 'huojiemajiang.xlsx'
    touchfilepath2depth(excelpath)
    excelwriter = pd.ExcelWriter(excelpath)
    if readfrominiurls := getcfpoptionvalue('evermuse', 'huojiemajiang', 'zhanjiurls'):
        # 用\t标记无效的链接，这里做对比的时候需要去掉tab
        urlsrecord = [x.strip('\t') for x in readfrominiurls.split(',')]
        if url not in urlsrecord:
            if rstdf := getsinglepage(url):
                urlsrecord.insert(0, url)
                recorddf = pd.read_excel(excelpath)
                rstdf = recorddf.append(getsinglepage(url))
                rstdf.drop_duplicates(['roomid', 'time', 'guestid'], inplace=True)
                rstdf.sort_values(by=['time', 'score'], ascending=[False, False], inplace=True)
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

        if firstdf := getsinglepage(url):
            urlsrecord = [url]
            firstdf.to_excel(excelwriter, index=False, encoding='utf-8')
            excelwriter.close()
            log.info(f"{firstdf.shape[0]}条记录写入文件\t{excelpath}")
        else:
            log.critical(f"这个网页貌似无效\t{url}")
            urlsrecord = [f"\t{url}"]

        log.info(f"第一条链接加入列表\t{url}")
        setcfpoptionvalue('evermuse', 'huojiemajiang', 'zhanjiurls', ','.join(urlsrecord))


def zhanjidesc():
    excelpath = getdirmain() / 'data' / 'muse' / 'huojiemajiang.xlsx'
    recorddf = pd.read_excel(excelpath)
    rstdf = recorddf
    rstdf.drop_duplicates(['roomid', 'time', 'guestid'], inplace=True)
    rstdf.sort_values(by=['time', 'score'], ascending=[False, False], inplace=True)
    print(rstdf.describe())
    outlst = list()
    rgp = rstdf.groupby(['guest']).count()
    outlst.append(f"参战人数：\t{rgp.shape[0]}")
    outlst.append(f"进行局数：\t{rstdf.groupby(['roomid']).count().shape[0]}")

    def formatdfstr(ddf):
        return '\n'.join(str(ddf).split('\n')[1:-1])

    kaifang = rstdf[rstdf.host == True].groupby(['guest']).count()['host'].sort_values(ascending=False)
    outlst.append(f"开房积极分子排名：\n{formatdfstr(kaifang)}")
    zimo = rstdf.groupby(['guest']).sum()['zimo'].sort_values(ascending=False)
    outlst.append(f"自摸技术能手排名：\n{formatdfstr(zimo)}")
    dianpao = rstdf.groupby(['guest']).sum()['dianpao'].sort_values(ascending=False)
    outlst.append(f"最被吐槽的炮王排名：\n{formatdfstr(dianpao)}")
    jingding = rstdf.groupby(['guest']).sum()['jingding'].sort_values(ascending=False)
    outlst.append(f"最有含金量的金顶排名：\n{formatdfstr(jingding)}")

    outstr = '\n\n'.join(outlst)
    return outstr


if __name__ == '__main__':
    log.info(f'运行文件\t{__file__}')

    # sp1 = "http://s0.lgmob.com/h5_whmj_qp/zhanji/index.php?id=fks0_eb81c193dea882941fe13dfa5be24a11"
    # sp2 = "http://s0.lgmob.com/h5_whmj_qp/zhanji/index.php?id=fks0_f6d46cf8836b1898e63f5c0c2ecb699a"
    # sp3 = "http://s0.lgmob.com/h5_whmj_qp/zhanji/index.php?id=fks0_5e2380aff0e95d7003ca59d061f5a76f"
    # splst = [sp1, sp2, sp3]

    ownername = '白晔峰'
    splst = fetchmjurl(ownername)

    for sp in splst:
        updateurllst(sp)

    rst = zhanjidesc()
    print(rst)

    # eurl = "http://s0.lgmob.com/h5_whmj_qp/zhanji/index.php?id=fks0_eca8b4c6e0bc4313c3a4658fc5b85720"
    # edf = getsinglepage(eurl)
    # print(edf)

    # rstdf = pd.DataFrame()
    # for sp in splst[:20]:
    #     getinfo = getsinglepage(sp)
    #     # print(getinfo)
    #     rstdf = rstdf.append(getinfo)
    #
    # print(rstdf.reset_index(drop=True))

    log.info(f'文件{__file__}运行结束')
