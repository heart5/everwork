# encoding:utf-8
"""
根据银行卡的流水记录，自动提取更新公司相关记录到共享笔记本中相应笔记中
笔记本：银行卡，guid：34b5423f-296f-4a87-b8c0-2ca0a6113053
笔记本：财务管理，guid：bec668cd-bc55-4496-83e3-660044042399

资金流水疑似问题条目：a8335080-9d3a-4f6d-8a05-9e88d5fa1eff
货款回笼流水账：4992b5bf-a81e-4b5a-aa4f-2a86ae420285
上游付款流水账：5eaf0153-816c-4def-b26e-439a21000be3

全纪录 to 公司相关流水
招行（9929）：0248c009-f709-40b2-9cf1-f28ed6b3a44e
农商行（6047：82e5d858-5fc5-4816-8cc0-f83eb261b4f2
工行（7520）：1fa53462-ba4b-42b3-87b1-d03f0dd7f432
农商行（2073）朱平：81a9c899-c960-4a64-ba02-0de9792df4a0
农行（8574）：f05636eb-12a7-4198-a652-b39e7f34d327
邮储（4824）：2e2cde17-447b-4d9b-833e-c5fb40230328
工行（8527）罗运辉：d86c3a51-e68d-4866-8b74-7cbd1d55ddfb
招行（6028）：12eedce8-ab24-495a-b987-dc4923627563
交行（5631）：054b9077-a866-4c1c-a7c7-943064dd75b4
中信（3391）：aa5acf2c-1395-43c6-a46a-82dda20a1ba9
招行（1568）朱平：328eda47-f199-4469-bdba-8b4df2426fbe
招行（4367）范小华：c38262ff-920a-4b60-b7ff-1918b6175ac2

"""
import datetime
import re
from threading import Timer

import pandas as pd
from bs4 import BeautifulSoup

from func.logme import log
from func.evernt import findnotefromnotebook, token, get_notestore, evernoteapijiayi, imglist2note, tablehtml2evernote
from func.nettools import trycounttimes
from func.configpr import cfpzysm, inizysmpath


def fetchfinacefromliushui():
    def getnote(targetguid):
        note_store = get_notestore()
        notereturn = note_store.getNote(targetguid, True, True, False, False)
        evernoteapijiayi()
        return notereturn

    rulambda = lambda x: True if x in ['入', 'True'] else False

    # 货款回笼和上游付款noteguid
    resultnoteguids = ['4992b5bf-a81e-4b5a-aa4f-2a86ae420285', '5eaf0153-816c-4def-b26e-439a21000be3']
    # 取得已经有的
    rstexistlst = list()
    for resultnoteguid in resultnoteguids:
        notechuru = trycounttimes(getnote, inputparam=resultnoteguid, returnresult=True, servname='evernote服务器')
        souporigin = BeautifulSoup(notechuru.content, 'html.parser')
        souptr = souporigin.find_all('tr')
        if len(souptr) == 0:
            continue
        # 用rulambda函数转换字符串的'True'为True，False一样；转换日期为datetime类型
        souptrtxtlst = [[datetime.datetime.strptime(x.get_text().split('\n')[1], '%Y-%m-%d')]
                        + [rulambda(x.get_text().split('\n')[2])] + x.get_text().split('\n')[3:-1]
                        for x in souptr[1:]]
        rstexistlst.extend(souptrtxtlst)
    # print(rstexistlst)

    rstexistlsthashhlst = [hash(tuple(x)) for x in rstexistlst]
    rstexistlsthashhlsthash = hash(tuple(rstexistlsthashhlst))
    resulthash = rstexistlsthashhlsthash

    financesection = '财务流水账'
    if not cfpzysm.has_section(financesection):
        cfpzysm.add_section(financesection)
        cfpzysm.write(open(inizysmpath, 'w', encoding='utf-8'))

    nbguid = '34b5423f-296f-4a87-b8c0-2ca0a6113053'
    finacenotefind = findnotefromnotebook(token, nbguid)
    print(finacenotefind)

    ptn = re.compile(u'^(\d{4}年\d{1,2}月\d{1,2}日)\s+([出入])\s+([\d.]+)[日美]?元\s*')
    dubiousitems = list()
    for item in finacenotefind:
        note = trycounttimes(getnote, inputparam=item[0], returnresult=True, servname='evernote服务器')
        if not cfpzysm.has_option(financesection, item[0]):
            updatenum = 0
        else:
            updatenum = cfpzysm.getint(financesection, item[0])
        if item[2] == updatenum:
            print(f'{item[0]}\t{item[1]}\t{len(rstexistlst)}\t无内容更新。')
            continue
        print(f'{item[0]}\t{item[1]}\t{len(rstexistlst)}', end='\t')
        rstexistlst = [x for x in rstexistlst if x[5] != item[0]]
        print(len(rstexistlst), end='\t')
        souporigin = BeautifulSoup(note.content, "html.parser")
        itemlist = list()
        for im in souporigin.find_all('div'):
            imtxt = im.get_text()
            if len(im.attrs) > 0:
                # print(f'{len(im.attrs)}\t{im.attrs}')
                continue
            if len(imtxt) == 0:
                continue
            imsplit = re.split(ptn, imtxt)
            if len(imsplit) != 5:
                if len(re.split('^(\d{4}年\d{1,2}月\d{1,2}日)\s+', imtxt)) > 1:
                    dubiousitem = f'{len(imsplit)}\t{imsplit}\t{imtxt}'
                    # print(dubiousitem)
                    dubiousitems.append([item[1], dubiousitem])
                continue
            imlst = list()
            try:
                imlst = [datetime.datetime.strptime(imsplit[1], '%Y年%m月%d日')] \
                        + [rulambda(imsplit[2])] + imsplit[3:] + [item[1], item[0]]
            except ValueError as ve:
                log.critical(f'出现日期范围错误：{item[0]}\t{item[1]}\t{imtxt}。{ve}')
                continue
            itemlist.append(imlst[:-2])
            rstexistlst.append(imlst)
        print(len(rstexistlst))
        # print(itemlist)
        cfpzysm.set(financesection, item[0], f'{item[2]}')
        cfpzysm.write(open(inizysmpath, 'w', encoding='utf-8'))

    rstexistlsthashhlst = [hash(tuple(x)) for x in rstexistlst]
    rstexistlsthashhlsthash = hash(tuple(rstexistlsthashhlst))

    if resulthash == rstexistlsthashhlsthash:
        updatable = False
    else:
        updatable = True

    return rstexistlst, dubiousitems, updatable


def chaijie2note():
    resultlst, dubiouslst, noteupdatable = fetchfinacefromliushui()
    # print(resultlst)
    if not noteupdatable:
        log.info('所有财务笔记都没有更新')
        return

    nowstr = datetime.datetime.now().strftime('%F %T')
    if len(dubiouslst) > 0:
        imglist2note(get_notestore(), list(), 'a8335080-9d3a-4f6d-8a05-9e88d5fa1eff', f'资金流水疑似问题条目（{nowstr}）',
                     tablehtml2evernote(pd.DataFrame(dubiouslst), tabeltitle='资金流水疑似问题条目', withindex=False))
    dfall = pd.DataFrame(resultlst, columns=['date', 'ru', 'jine', 'mingmu', 'card', 'guid'])
    dfall.sort_values(['date'], ascending=False, inplace=True)
    dfchuru = dfall[dfall.mingmu.str.startswith('货款') == True]
    imglist2note(get_notestore(), list(), '4992b5bf-a81e-4b5a-aa4f-2a86ae420285', f'货款回笼流水账（{nowstr}）',
                 tablehtml2evernote(dfchuru[dfchuru.ru],
                                    tabeltitle='货款回笼流水账', withindex=False))
    imglist2note(get_notestore(), list(), '5eaf0153-816c-4def-b26e-439a21000be3', f'上游付款流水账（{nowstr}）',
                 tablehtml2evernote(dfchuru[dfchuru.ru == False],
                                    tabeltitle='上游付款流水账', withindex=False))
    # print(dfall)


def financetimer(jiangemiao):
    chaijie2note()

    global timer_finace
    timer_finace = Timer(jiangemiao, financetimer, [jiangemiao])
    # print(timer_weather)
    timer_finace.start()

if __name__ == '__main__':
    log.info(f'运行文件\t{__file__}')
    # chaijie2note()
    financetimer(60 * 16)
    # finacetimer(60 * 60 * 2 + 60 * 48)
    print('Done.完毕。')
