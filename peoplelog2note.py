#
# encoding:utf-8
#
"""
处理进出记录笔记，生成图表呈现
"""

from imp4nb import *
from bs4 import BeautifulSoup


def notification2df(items):
    split_items = list()
    for itemstr in items:
        split_items.append(itemstr.strip().split('||| '))

    dfnoti = pd.DataFrame(split_items, columns=('atime', 'shuxing', 'topic', 'content'))
    dfnoti['received'] = True
    log.info('系统提醒记录有%d条。' % dfnoti.shape[0])
    # descdb(dfnoti)
    dfnoti.drop_duplicates(inplace=True)
    log.info('系统提醒记录去重后有%d条。' % dfnoti.shape[0])
    dfnoti.index = dfnoti['atime'].apply(
        lambda x: pd.to_datetime(datetime.datetime.strptime(x.strip(), '%B %d, %Y at %I:%M%p'))
        if len(x.split('at')) > 1 else pd.to_datetime(datetime.datetime.strptime(x.strip(), '%B %d, %Y')))
    # dfnoti.index = dfnoti['atime']
    del dfnoti['atime']
    dfnoti.sort_index(ascending=False, inplace=True)
    # descdb(dfnoti)
    dfout = dfnoti
    # b3a3e458-f05b-424d-8ec1-604a3e916724

    try:
        token = cfp.get('evernote', 'token')
        notestore = get_notestore()
        xiangmu = ['微信', '支付宝', 'QQ', '日历']
        for xm in xiangmu:
            biaoti = '系统提醒（%s）记录' % xm
            dfxm = dfnoti[dfnoti.shuxing == xm]
            if cfplife.has_option('lifenotecount', xm):
                ready2update = dfxm.shape[0] > cfplife.getint('lifenotecount', xm)
            else:
                ready2update = True
            print('%d\t%s\t%s' % (dfxm.shape[0], ready2update, biaoti))
            if ready2update:
                imglist2note(notestore, [], cfplife.get('notesguid', xm), biaoti,
                             tablehtml2evernote(dfxm, biaoti))
                cfplife.set('lifenotecount', xm, '%d' % dfxm.shape[0])
                cfplife.write(open(inilifepath, 'w', encoding='utf-8'))

    except Exception as ee:
        log.critical('更新系统提醒笔记时出现错误。%s' % str(ee))
    return dfout


def callsms2df(itemstr):
    # 读取老记录
    with open('data\\ifttt\\smslog_gmail_all.txt', 'r', encoding='utf-8') as fsms:
        items = [line.strip() for line in fsms if len(line.strip()) > 0]
    itemstr = itemstr + items
    log.info('电话短信记录有%d条。' % len(itemstr))
    itemstrjoin = '\n'.join(itemstr)
    pattern = re.compile(
        r'^(.*?)(?:(\w+ \d+, \d{4} at \d{2}:\d{2}[A|P]M)|(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\+08:00))(.*?)$',
        re.U | re.M)
    slices = re.split(pattern, itemstrjoin)
    slices = slices[1:]
    # print(len(slices))
    # for i in range(15):
    #     print("%d\t%s" %(i,slices[i]))

    # pattern = re.compile(r'^(?:\w*?)(?:\s*?)@SMS \+(?:\s+)(\w+ \d+, \d{4} at \d{2}:\d{2}[A|P]M)(?:\s*?)，'
    #                      r'(.*?)(?:\s+)(.*?)(?:\s+)([\d|-]+)(?:.*?)(?:\s+)(\d+)(?:\s+)(?:.*?)$', re.U|re.M)
    # slices = re.split(pattern, itemstr)
    # print(len(slices))
    # for i in range(30):
    #     print(slices[i].strip())
    #
    split_items = list()
    for i in range(int(len(slices) / 5)):
        item = list()
        # print(slices[i*5:i*5+5])
        itemtimestr = slices[i * 5 + 1]
        if itemtimestr is None:
            itemtimestr = slices[i * 5 + 2].strip()
            itemtime = datetime.datetime.strptime(itemtimestr, '%Y-%m-%d %H:%M:%S+08:00')
            # itemtime = pd.to_datetime(itemtimestr)
        else:
            itemtime = datetime.datetime.strptime(slices[i * 5 + 1].strip(), '%B %d, %Y at %I:%M%p')

        itemname = ''
        itemnumber = ''
        itemshuxing = '电话'
        itemreceived = True
        itemcontentstr = slices[i * 5 + 3].strip()
        itemcontent = itemcontentstr

        patternsms = re.compile(r'：(.*)，(\w*)\|\|\| (\d+)', re.U)
        splititem = re.split(patternsms, itemcontentstr)
        if len(splititem) == 5:
            # ：抱歉 明天见，||| 13554015554
            # ['', '抱歉 明天见', '', '13554015554', '']
            itemcontent = splititem[1]
            itemname = splititem[2]
            itemnumber = splititem[3]
            itemshuxing = '短信'

        if len(itemname) == 0:
            itemnamestr = slices[i * 5 + 0].strip()
            if itemnamestr.endswith('@SMS +'):
                [itemname, *__] = itemnamestr.split('@SMS +')
                patterncall7 = re.compile('^，?(?:(电话打给)|(电话来自))\s+(?:(.+?)\s+)?(\d+)，时长\s+(\d+)\s+秒$', re.U)
                splititem = re.split(patterncall7, itemcontentstr)
                # print(len(splititem))
                # splititem = itemcontentstr.split()
                if len(splititem) == 7:
                    # ，电话打给 陈益 15623759390，时长 42 秒
                    # ['', '电话打给', None, '陈益', '15623759390', '42', '']
                    # ，电话来自 18671454792，时长 29 秒
                    # ['', None, '电话来自', None, '18671454792', '29', '']
                    # ，电话打给 黄兆钢 15337282888，时长 42 秒
                    # ['', '电话打给', None, '黄兆钢', '15337282888', '42', '']
                    # ，电话来自 白天军 13949452849，时长 35 秒
                    # ['', None, '电话来自', '白天军', '13949452849', '35', '']

                    itemshuxing = '电话'
                    itemname = splititem[3]
                    itemnumber = splititem[4]
                    itemcontent = splititem[5]
                    if splititem[1]:
                        itemreceived = False
                # else:

                patterncall5 = re.compile('(错过来电)\s+(?:(.+?)\s+)?(\d+)', re.U)
                splititem = re.split(patterncall5, itemcontentstr)
                if len(splititem) == 5:
                    # 错过来电 曹树强 13971167977
                    # ['', '错过来电', '曹树强', '13971167977', '']
                    # 错过来电 18903752832
                    # ['', '错过来电', None, '18903752832', '']
                    itemshuxing = '电话'
                    itemname = splititem[2]
                    itemnumber = splititem[3]
                    itemreceived = True
                    itemcontent = None

            elif itemnamestr.endswith('的通话记录'):
                [_, itemname, *__] = itemnamestr.split()
                patterncall6 = re.compile(
                    r'，(?:(\+?\d+)s\s\(\d{2}:\d{2}:\d{2}\))?(\+?\d+)\s\((?:(已接来电)|(已拨电话)|(未接来电))\)')
                splititem = re.split(patterncall6, itemcontent)
                if len(splititem) == 7:
                    itemshuxing = '电话'
                    itemnumber = splititem[2]
                    itemcontent = splititem[1]
                    if splititem[4] is not None:
                        itemreceived = False
                else:
                    pass
            elif itemnamestr.startswith('SMS with'):
                itemshuxing = '短信'
                [*__, itemname] = itemnamestr.split()
                if itemcontent.startswith('收到'):
                    itemreceived = True
                    weiyi = 4
                elif itemcontent.startswith('发出'):
                    itemreceived = False
                    weiyi = 4
                else:
                    weiyi = 1
                itemcontent = itemcontentstr[weiyi:]
                # print(itemname + '\t' + str(itemtime) + '\t' + itemcontent)
                # print(splititem)

        item.append(itemtime)
        if itemname is None:
            itemname = itemnumber
        item.append(itemname)
        item.append(itemnumber)
        item.append(itemshuxing)
        item.append(itemreceived)
        item.append(itemcontent)
        # print(slices[i*5].strip()+'\t'+slices[i*5+1].strip()+'\t'+slices[i*5+2].strip()+'\t'+slices[i*5+4].strip())
        split_items.append(item)

    dfnoti = pd.DataFrame(split_items, columns=('atime', 'name', 'number', 'shuxing', 'received', 'content'))
    log.info('电话短信记录整理后有%d条。' % dfnoti.shape[0])
    dfnoti.drop_duplicates(inplace=True)
    log.info('电话短信记录去重后有%d条。' % dfnoti.shape[0])
    dfnoti.sort_values(['atime'], ascending=False, inplace=True)
    # dfnoti.index = dfnoti['time']
    # del dfnoti['time']
    dfout = dfnoti
    # b3a3e458-f05b-424d-8ec1-604a3e916724

    try:
        token = cfp.get('evernote', 'token')
        notestore = get_notestore()
        if cfplife.has_option('allsets', 'callsms'):
            ready2update = dfout.shape[0] > cfplife.getint('allsets', 'callsms')
        else:
            ready2update = True
        if ready2update:
            xiangmu = '电话短信'
            imglist2note(notestore, [], cfplife.get('notesguid', xiangmu), xiangmu,
                         tablehtml2evernote(dfout[:1000], xiangmu))
            cfplife.set('allsets', 'callsms', '%d' % dfout.shape[0])
            cfplife.write(open(inilifepath, 'w', encoding='utf-8'))
    except Exception as eee:
        log.critical('更新人脉记录笔记时出现错误。%s' % str(eee))
    return dfout


def peoplestattimer(jiangemiao):
    dfpeople = pd.DataFrame()

    strjilunotifi = jilugmail('Ifttt/Notification', 'notification', 'all')
    if strjilunotifi:
        dfnoti = notification2df(strjilunotifi)
    # print(dfnoti.head(5))
    strjilucallsms = jilugmail('Ifttt/CallSmsLog', 'callsmslog', 'all', bodyonly=False)
    if strjilucallsms:
        # callsmsold('data\\ifttt\\smslog_gmail_all.txt')
        dfcs = callsms2df(strjilucallsms)

    global timer_jinchu
    timer_jinchu = Timer(jiangemiao, peoplestattimer, [jiangemiao])
    timer_jinchu.start()


if __name__ == '__main__':
    peoplestattimer(60 * 25)

    # rn = '\r\n'
    # print(len(rn))
    # print(len(rn.strip()))
    # print(len(rn.strip().replace('\r', '').replace('\n', '')))

    # strjilucallsms = jilugmail('Ifttt/CallSmsLog', 'callsmslog', 'all', bodyonly=False)
    # print(strjilucallsms[:300])
    #
    # dfcs = callsms2df(strjilucallsms)
    # print(dfcs)
