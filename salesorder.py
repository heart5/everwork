#
# encoding:utf-8
#
"""
处理订单数据，进行各种统计，用于每日订单核对等工作
['c1b8297a-2c3a-4afc-9faf-e36484495529', '武汉真元放假调休记录'],
['040509c2-a8bf-4af9-9296-3d41321889d9', '武汉真元员工请假记录']
"""

from imp4nb import *
from bs4 import BeautifulSoup
from matplotlib.ticker import MultipleLocator, FuncFormatter
import pygsheets


def chuliholidayleave_note(zhuti):
    note_store = get_notestore()
    guid = cfpzysm.get('行政管理', f'{zhuti[0]}guid')
    note = note_store.getNote(guid, True, True, False, False)
    evernoteapijiayi()
    # print(timestamp2str(int(note.updated/1000)))
    # print(note.updateSequenceNum)
    if cfpzysm.has_option('行政管理', f'{zhuti[0]}updatenum'):
        updatenumold = cfpzysm.getint('行政管理', f'{zhuti[0]}updatenum')
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
    resultlist = list()
    for i in range(int(len(splititems) / 2)):
        item = list()
        item.append(pd.to_datetime(splititems[i * 2]))
        *names, daynum = re.split('[,，]', splititems[i * 2 + 1])
        # print(sitems)
        if len(names) == 2:
            names.append('放假')
        # item.append(names[1:])
        item.append(names[1])
        item.append(names[2])
        item.append(daynum)
        resultlist.append(item)

    print(resultlist)

    dfresult = None
    for im in resultlist:
        num = math.ceil(float(im[3]))
        drim = pd.date_range(im[0], im[0] + datetime.timedelta(days=int(num) - 1), freq='D')
        if dfresult is None:
            dfresult = pd.DataFrame(index=drim)
            dfresult['mingmu'] = im[1]
            dfresult['xingzhi'] = im[2]
        else:
            dftmp = pd.DataFrame(index=drim)
            dftmp['mingmu'] = im[1]
            dftmp['xingzhi'] = im[2]
            dfresult = dfresult.append(dftmp)
        pass
    dfresult.sort_index(ascending=False, inplace=True)
    cnxp = lite.connect('data\\workplan.db')
    dfresult.to_sql(zhuti[1], cnxp, if_exists='replace')
    cnxp.close()
    log.info(f'{zhuti[0]}数据表更新了{dfresult.shape[0]}条记录。')
    cfpzysm.set('行政管理', f'{zhuti[0]}updatenum', '%d' % note.updateSequenceNum)
    cfpzysm.write(open(inizysmpath, 'w', encoding='utf-8'))

    return dfresult


def fetchworkfile_from_gmail(topic):
    hostg = cfp.get('gmail', 'host')
    usernameg = cfp.get('gmail', 'username')
    passwordg = cfp.get('gmail', 'password')
    dirwork = 'Work'
    mailitemsg = getmail(hostg, usernameg, passwordg, dirtarget=dirwork, unseen=True, topic=topic)
    # mailitemsg = getmail(hostg, usernameg, passwordg, dirtarget='Work', topic=topic)
    if mailitemsg is False:
        log.info('Gmail信箱目录《%s》中暂无新邮件。' % dirwork)
        return

    itemslst = list()
    for headerg, bodyg in mailitemsg:
        itemslst.append(headerg[1])
    print(itemslst)
    topicstring = '“%s”相关的' % topic if len(topic) > 0 else ''
    log.info('从Gmail邮箱目录《%s》中获取%d封%s新邮件。' % (dirwork, len(itemslst), topicstring))


def workfilefromgmail2datacenter(jiangemiao):

    try:
        fetchworkfile_from_gmail('')
    except Exception as eeee:
        log.critical('从gmail信箱获取工作文件时出现未名错误。%s' % (str(eeee)))

    global timer_filegmail2datacenter
    timer_filegmail2datacenter = Timer(jiangemiao, workfilefromgmail2datacenter, [jiangemiao])
    timer_filegmail2datacenter.start()


def fetchattendance_from_evernote(jiangemiao):
    try:
        zhutis = [['放假', 'holiday'], ['请假', 'leave']]
        for zhuti in zhutis:
            dfresult = chuliholidayleave_note(zhuti)
            if dfresult is not False:
                descdb(dfresult)
    except Exception as eee:
        log.critical(f'从evernote获取放假笔记信息时出现未名错误。{eee}')

    global timer_holiday2datacenter
    timer_holiday2datacenter = Timer(jiangemiao, fetchattendance_from_evernote, [jiangemiao])
    timer_holiday2datacenter.start()


if __name__ == '__main__':
    # fetchworkfile_from_gmail('销售订单')
    # workfilefromgmail2datacenter(60*60*2)
    # fetchattendance_from_evernote(60*30)
    dtlist = ['2018-6-14', '2018-6-10', '2018-5-1', '2018-3-4']
    reslist = isworkday(dtlist)
    print(dtlist)
    print(reslist)
