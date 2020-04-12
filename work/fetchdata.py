# encoding:utf-8
"""
获取数据
"""
import datetime
import math
import re
import time
import pandas as pd
import sqlite3 as lite
from threading import Timer
from bs4 import BeautifulSoup

import pathmagic
with pathmagic.context():
    from func.first import dbpathworkplan
    from func.pdtools import descdb
    from func.logme import log
    from func.configpr import getcfpoptionvalue, setcfpoptionvalue
    from func.mailsfunc import getmail
    from func.wrapfuncs import timethis
    from func.profilerlm import lpt_wrapper
    from func.evernttest import get_notestore, evernoteapijiayi
    from func.nettools import trycounttimes2
    from life.noteweather import getgaowenfromgoogledrive, getrainfromgoogledrive
    from func.gmailfetch import getworknewmail


@timethis
def fetchworkfile_from_gmail(topic):
    hostg = getcfpoptionvalue('everwork', 'gmail', 'host')
    usernameg = getcfpoptionvalue('everwork', 'gmail', 'username')
    passwordg = getcfpoptionvalue('everwork', 'gmail', 'password')
    dirwork = 'Work'
    mailitemsg = getmail(hostg, usernameg, passwordg,
                         dirtarget=dirwork, unseen=True, topic=topic)
    # mailitemsg = getmail(hostg, usernameg, passwordg, dirtarget='Work', topic=topic)
    if mailitemsg is False:
        log.info('Gmail信箱目录《%s》中暂无新邮件。' % dirwork)
        return

    itemslst = list()
    for headerg, bodyg in mailitemsg:
        itemslst.append(headerg[1])
    print(itemslst)
    topicstring = '“%s”相关的' % topic if len(topic) > 0 else ''
    log.info('从Gmail邮箱目录《%s》中获取%d封%s新邮件。' %
             (dirwork, len(itemslst), topicstring))


@timethis
# @lpm_wrapper()
def chuliholidayleave_note(zhuti: list):
    # global note_store
    note_store = get_notestore()
    # print(zhuti)
    guid = getcfpoptionvalue('everworkplan', '行政管理', f'{zhuti[0]}guid')

    @trycounttimes2('evernote服务器')
    def getnote(guidin):
        notein = note_store.getNote(guidin, True, True, False, False)
        evernoteapijiayi()
        return notein

    note = getnote(guid)
    # print(timestamp2str(int(note.updated/1000)))
    # print(note.updateSequenceNum)
    if not (updatenumold := getcfpoptionvalue('everworkplan', '行政管理', f'{zhuti[0]}updatenum')):
        updatenumold = 0
    if note.updateSequenceNum <= updatenumold:
        log.info(f'{zhuti[0]}笔记内容无更新。')
        # return
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

    # print(items)
    if isjiaqi:
        resultlisthd = items
        dfresult = None
        for [dtinfor, mingmu, xingzhiinfor, tian] in resultlisthd:
            numfloat = float(tian)
            numceil = math.ceil(numfloat)
            numfloor = math.floor(numfloat)
            driminfor = pd.date_range(
                dtinfor, dtinfor + datetime.timedelta(days=int(numceil) - 1), freq='D')
            if dfresult is None:
                dfresult = pd.DataFrame(index=driminfor)
                dfresult['mingmu'] = mingmu
                dfresult['xingzhi'] = xingzhiinfor
                dfresult['tianshu'] = 1
                # dfresult['tianshu'] = dfresult['tianshu'].astype(float)
                if numfloat > numfloor:
                    xtian = numfloat - numfloor
                    # print(f'{numfloat}\t{numceil}\t{numfloor}\t{mingmu}\t{xingzhi}\t{tian}\t{xtian}')
                    dfresult.iloc[-1, -1] = xtian
            else:
                dftmp = pd.DataFrame(index=driminfor)
                dftmp['mingmu'] = mingmu
                dftmp['xingzhi'] = xingzhiinfor
                dftmp['tianshu'] = 1
                # dfresult['tianshu'] = dfresult['tianshu'].astype(float)
                if numfloat > numfloor:
                    xtian = numfloat - numfloor
                    # print(f'{numfloat}\t{numceil}\t{numfloor}\t{mingmu}\t{xingzhi}\t{tian}\t{xtian}')
                    dftmp.iloc[-1, -1] = xtian
                dfresult = dfresult.append(dftmp)
        dfresult.sort_index(ascending=False, inplace=True)
        dfresult['date'] = dfresult.index
        # dfresult['idx'] = range(dfresult.shape[0])
        # holiday, ['date', 'mingmu', 'xingzhi', 'tianshu']
        dfresult = dfresult.reset_index(drop=True)
    else:
        dfresult = pd.DataFrame(items, columns=columns)
    return dfresult


@timethis
def fetch_dutyondata2lite():
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
            if zhuti[0] in ['高温', '下雨']:
                if zhuti[0] == '高温':
                    dffromgd, dfallfromgd = getgaowenfromgoogledrive()
                    dfresult = dfresult.append(dffromgd)
                    dfresult.drop_duplicates(['hottime'], inplace=True)
                else:
                    dffromgd, dfallfromgd = getrainfromgoogledrive()
                    dfresult = dfresult.append(dffromgd)
                    dfresult.drop_duplicates(['raintime'], inplace=True)
            countfromini = getcfpoptionvalue('everworkplan', '行政管理', f'{zhuti[0]}count')
            if not countfromini:
                countfromini = 0
            if countfromini == dfresult.shape[0]:
                log.info(f"本轮查询没有发现新的《{zhuti[0]}》相关数据,跳过！")
                continue
            cnxp = lite.connect(dbpathworkplan)
            # index, ['mingmu', 'xingzhi', 'tianshu', 'date']
            dfresult.to_sql(zhuti[1], cnxp, if_exists='replace', index=None)
            cnxp.close()
            log.info(f'{zhuti[0]}数据表更新了{dfresult.shape[0]}条记录。')
            setcfpoptionvalue('everworkplan', '行政管理', f'{zhuti[0]}count', f"{dfresult.shape[0]}")
    except OSError as exp:
        topic = [x for [x, *y] in zhutis]
        log.critical(f'从evernote获取{topic}笔记信息时出现未名错误。{exp}')


if __name__ == '__main__':
    log.info(f'运行文件\t{__file__}')
    # fetchworkfile_from_gmail('')
    getworknewmail()
    fetch_dutyondata2lite()
    log.info(f'文件{__file__}运行结束！')
