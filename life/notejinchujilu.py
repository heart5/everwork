#
# encoding:utf-8
#
"""
处理进出记录笔记，生成图表呈现

名称：行政管理 guid：31eee750-e240-438b-a1f5-03ce34c904b4
名称：love    guid：c068e01f-1a7a-4e65-b8e4-ed93eed6bd0b
源信息笔记guid和标题如下：
f119e38e-3876-4937-80f1-e6a6b2e5d3d0 白晔峰公司文昌路进出记录
24aad619-2356-499e-9fa7-f685af3a81b1 白晔峰公司花木市场进出记录
84e9ee0b-30c3-4404-84e2-7b4614980b4b 汉阳办进出记录
6fb1e016-01ab-439d-929e-994dc980ddbe 汉口办进出记录
38f4b1a9-7d6e-4091-928e-c82d7d3717c5 创食人公司进出记录

d8fa0226-88ac-4b6c-b8fd-63a9038a6abf 白晔峰家附近区域进出记录
1ea50564-dee7-4e82-87b5-39703671e623 丁字桥进出记录
9ac941cc-c04b-4d4b-879f-2bfb044382d4 白晔峰家鲁山进出记录

输出结果笔记：
7f4bec82-626b-4022-b3c2-0d9b3d71198d 公司（文昌路）进出记录统计图表    wenchanglu
a7e84055-f075-44ab-8205-5a42f3f05284 汉阳办进出记录统计图表    hanyangban
2c5e3728-be69-4e52-a8ff-07860e8593b7 汉口办进出记录统计图表    hankouban
2d908c33-d0a2-4d42-8d4d-5a0bc9d2ff7e 公司进出记录统计图表 maotanhuamushichang
06bb4996-d0d8-4266-87d5-f3283d71f58e 东西湖三秀路进出记录统计图表 yangfu'restraunaut
0fa3222e-1029-4417-a7a2-8ec64f9c9a12 家（大冶）进出记录统计图表  daye
294b584f-f34a-49f0-b4d3-08085a37bfd5 创食人公司进出记录统计图表  qiwei
08a01c35-d16d-4b22-b7f7-61e3993fd2cb 家附近出入统计    huadianxiaolu
987c1d5e-d8ad-41aa-9269-d2b840616410 老家（鲁山）进出统计图表   lushan
6eef085c-0e84-4753-bf3e-b45473a12274 丁字桥进出统计图表  dingziqiao


"""

# from imp4nb import *
import os, re, time, datetime, pandas as pd, matplotlib.pyplot as plt
from os import listdir
from os.path import isfile, join
from bs4 import BeautifulSoup
from threading import Timer
from matplotlib.ticker import MultipleLocator, FuncFormatter
from pandas.tseries.offsets import *
import pygsheets
from func.logme import log
from func.first import dirmainpath
from func.evernt import get_notestore, evernoteapijiayi, tablehtml2evernote, imglist2note
from func.configpr import cfp, inifilepath, cfplife, inilifepath
from func.mailsfunc import jilugmail


def jilugooglefile(filepath):
    filelist = [ff for ff in listdir(str(filepath)) if isfile(str(filepath / ff))]
    print(filelist)
    dfout = None
    global log
    for i in range(len(filelist)):
        df = pd.read_excel(str(filepath / filelist[i]), sheetname='工作表1',
                           header=None, index_col=0, parse_dates=True)
        if df.shape[0] == 0:
            log.info('%s 无进出记录' % filelist[i])
            continue
        # descdb(df)
        df['shuxing'] = df.iloc[:, 1].apply(lambda x: x.split(' ')[0])
        df['didian'] = df.iloc[:, 1].apply(lambda x: x.split(' ')[1])
        df['entered'] = df.iloc[:, 0].apply(lambda x: True if x == 'entered' else False)
        dff = df.iloc[:, [6, 4, 5]]
        dff.columns = ['entered', 'shuxing', 'address']
        # descdb(dff)
        if i == 0:
            dfout = dff
        else:
            dfout = dfout.append(dff).sort_index()

    return dfout


def jilugoogledrive():
    # 验证登录
    global dirmainpath
    gc = pygsheets.authorize(service_file=str(dirmainpath / 'data' / 'imp' / 'ewjinchu.json'))
    files = gc.list_ssheets()
    dffiles = pd.DataFrame(files)
    # print(dffiles.head())

    dfboot = dffiles[dffiles.name.str.contains('boots trail').values == True]
    print(list(dfboot['name']))

    dfboottrails = pd.DataFrame()
    for ix in dfboot.index:
        dts = gc.get_range(dfboot.loc[ix][0], 'A:E')
        df = pd.DataFrame(dts)
        dfboottrails = dfboottrails.append(df, True)
        # print(df.head())
    dfboottrails.columns = ['atime', 'entered', 'xingzhi', 'tu', 'tulian']
    dfboottrails = pd.concat([dfboottrails, dfboottrails['xingzhi'].str.split(r' ', expand=True)], axis=1)
    dfboottrails = pd.DataFrame(dfboottrails)
    dfboottrails.rename(columns={0: 'shuxing', 1: 'address'}, inplace=True)
    dfboottrails.drop_duplicates(inplace=True)
    dfbout = dfboottrails.loc[:, ['atime', 'entered', 'shuxing', 'address']]
    dfbout['atime'] = dfbout['atime'].apply(
        lambda x: pd.to_datetime(time.strftime('%Y-%m-%d %H:%M', time.strptime(x, '%B %d, %Y at %I:%M%p'))))
    dfbout['entered'] = dfbout['entered'].apply(lambda x: True if x == 'entered' else False)
    dfbout['atime'] = dfbout['atime'].astype(pd.datetime)
    dfbout.index = dfbout['atime']
    dfbout = dfbout.sort_index()
    dfout = dfbout[['entered', 'shuxing', 'address']]
    # print(dfout.tail())
    return dfout


def jilunote(noteinfos):
    """
    读取ifttt自动通过gmail转发至evernote生成的地段进出记录，统计作图展示
    :rtype: Null
    """
    # itemstr = BeautifulSoup(get_notestore().getNoteContent(noteinfos[0]), "html.parser"). \
    #     get_text().replace('\r', '').replace('\n', '')  # 文本化后去掉回车、换行符等
    itemstr = BeautifulSoup(get_notestore().getNoteContent(noteinfos[0]), "html.parser"). \
        get_text().split('\r\n')  # 文本化后去掉回车、换行符等，通过split转换为list
    # print('笔记："%s" 中提取内容' %noteinfos[5])
    # print(itemstr)
    evernoteapijiayi()

    return itemstr


def wifitodf(itemstr, noteinfolistw):
    itemstrjoin = '\n'.join(itemstr)
    pattern = re.compile(
        '(?:Device )((?:dis)?connected) (?:to|from) ([\w|-]+)， (\w+ \d+, \d{4} at \d{2}:\d{2}[A|P]M)')
    slices = re.split(pattern, itemstrjoin)
    items_split = []
    for i in range(int(len(slices) / 4)):
        zhizi = list()
        zhizi.append(datetime.datetime.strptime(slices[i * 4 + 3], '%B %d, %Y at %I:%M%p'))
        if slices[i * 4 + 1].startswith('dis'):
            zhizi.append(False)
        else:
            zhizi.append(True)
        zhizi.append(slices[i * 4 + 2].lower())
        items_split.append(zhizi)
    dfwifiall = pd.DataFrame(items_split, columns=('atime', 'entered', 'name'))
    dfwifiall.drop_duplicates(inplace=True)
    dfwifiall.sort_values(['atime'], ascending=False, inplace=True)
    dfwifiall.index = dfwifiall['atime']

    dfwifilist = list()
    for item in items_split:
        for [_, address, shuxing, *arg, wifilist] in noteinfolistw:
            if item[2] in wifilist:
                item.append(shuxing)
                address1 = address
                if item[0] > pd.to_datetime('2017-01-09'):
                    if address.startswith('wenchanglu'):
                        address1 = 'maotanhuamushichang'
                else:
                    if address.startswith('maotanhuamushichang'):
                        address1 = 'wenchanglu'
                item.append(address1)
                dfwifilist.append(item)
                break

    dfwifi = pd.DataFrame(dfwifilist, columns=('atime', 'entered', 'name', 'shuxing', 'address'))
    dfwifi.drop_duplicates(inplace=True)
    # descdb(dfwifi)
    dfwifi.sort_values(['atime'], ascending=False, inplace=True)
    dfwifi.index = dfwifi['atime']
    del dfwifiall['atime']

    dfout = dfwifi[['entered', 'shuxing', 'address']]
    # descdb(dfout)

    try:
        notestore = get_notestore()
        dfnotename = dfwifi[['entered', 'shuxing', 'address']]
        dfwificount = dfwifi.shape[0]  # shape[0]获得行数，shape[1]则是列数
        print(dfwificount, end='\t')
        global cfp, inifilepath
        if cfp.has_option('wifi', 'itemnumber'):
            ntupdatenum = dfwificount > cfp.getint('wifi', 'itemnumber')  # 新数据集记录数和存档比较
        else:
            ntupdatenum = True
        print(ntupdatenum, end='\t')
        print('WIFI连接记录', end='\t')
        print(dfwifi.index[0])
        if ntupdatenum:  # or True:
            dfnotename.reset_index(inplace=True)
            dfnotenameg = pd.DataFrame(dfnotename.groupby(['address']).max()['atime'])
            dfnotenameg['count'] = dfnotename.groupby(['address']).count()['atime']
            dfnotenameg.sort_values(['atime'], ascending=False, inplace=True)
            wifitongjinametablestr = tablehtml2evernote(dfnotenameg, 'WIFI（特定）统计')
            wifijilutablestr = tablehtml2evernote(dfnotename.head(50), 'WIFI（特定）连接记录')
            dfwifiall.reset_index(inplace=True)
            dfnoteallg = pd.DataFrame(dfwifiall.groupby(['name']).max()['atime'])
            dfnoteallg['count'] = dfwifiall.groupby(['name']).count()['atime']
            dfnoteallg.sort_values(['atime'], ascending=False, inplace=True)
            wifitongjialltablestr = tablehtml2evernote(dfnoteallg, 'WIFI（全部）统计')
            imglist2note(notestore, [], '971f14c0-dea9-4f13-9a16-ee6e236e25be', 'WIFI连接统计表',
                         wifitongjinametablestr + wifijilutablestr + wifitongjialltablestr)

            cfp.set('wifi', 'itemnumber', '%d' % dfwificount)
            cfp.write(open(inifilepath, 'w', encoding='utf-8'))
    except Exception as eee:
        log.critical('更新WIFI连接统计笔记时出现错误。%s' % str(eee))

    return dfout


def itemstodf(itemstr, noteinfos):
    itemstrjoin = '\n'.join(itemstr)
    # 生成英文的月份列表，组装正则模式，以便准确识别
    yuefenlist = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'September', 'October',
                  'December', 'November']
    yuefennames = str(yuefenlist[0])
    for a in range(1, len(yuefenlist)):
        yuefennames += '|' + str(yuefenlist[a])
    yuefennames = '(?:' + yuefennames + ')'
    # (?:January|February|March|April|May|June|July|September|October|December|November)
    # print(yuefennames)
    # pattern = u'(\w*\s*\d+,\s*\d{4}\s*at\s*\d{2}:\d{2}[AP]M)\s：\s(e(?:xit|nter)ed)'
    # pattern = u'(%s\s*\d+,\s*\d{4}\s*at\s*\d{2}:\d{2}[AP]M)\s：\s(e(?:xit|nter)ed)' % yuefennames
    pattern = u'(%s\s*\d+,\s*\d{4}\s*at\s*\d{2}:\d{2}[AP]M)\s*：.*?\s*(e(?:xit|nter)ed)' % yuefennames
    # print(pattern)
    slicesoup = re.split(pattern, itemstrjoin)
    # print('印象笔记或Gmail邮件中提取“%s”内容后取模' %noteinfos[5])
    # print(slicesoup)
    # 提取时间和进出信息
    split_items = []
    for i in range(1, len(slicesoup), 3):
        zhizi = list()
        zhizi.append(slicesoup[i])
        zhizi.append(slicesoup[i + 1])
        split_items.append(zhizi)
    # print('生成目标列表')
    # print(split_items)

    dfjc = pd.DataFrame(split_items, columns=['atime', 'eort'])
    dfjc = dfjc.drop_duplicates(['atime', 'eort'])  # 去重
    dfjc['atime'] = dfjc['atime'].apply(
        lambda x: pd.to_datetime(time.strftime('%Y-%m-%d %H:%M', time.strptime(x, '%B %d, %Y at %I:%M%p'))))
    dfjc.index = dfjc['atime']
    dfjc = dfjc.sort_index()  # 排序
    dfjc['entered'] = dfjc['eort'].apply(lambda x: True if x == 'entered' else False)
    dfjc['shuxing'] = noteinfos[2]
    dfjc['address'] = noteinfos[1]
    dfout = dfjc[['entered', 'shuxing', 'address']]

    return dfout


def jinchustat(jinchujiluall, noteinfos):
    """
    读取ifttt自动通过gmail转发至evernote生成的地段进出记录，统计作图展示
    :rtype: Null
    """
    address = noteinfos[0]
    destguid = noteinfos[2]
    notetitle = noteinfos[3]
    # print(destguid, end='\t')
    # print(notetitle)
    dfjc = jinchujiluall[jinchujiluall.address == address][['entered']]
    # descdb(dfjc)
    dfjc['atime'] = dfjc.index
    dfjc['nianyue'] = dfjc['atime'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m'))
    dfjc['小时'] = dfjc['atime'].apply(lambda x: datetime.datetime.strftime(x, '%H'))
    # print(dfjc.tail(10))
    dfff = dfjc[dfjc.entered == False].groupby(['nianyue', '小时'])['entered'].count()  # 以离开为进出标准
    dffu = dfff.unstack(fill_value=0)
    # print(dffu)

    # 补满小时数和年月份
    for i in range(24):
        colname = '%02d' % i
        if colname not in list(dffu.columns):
            dffu[colname] = 0
    lst = sorted(list(dffu.columns))
    dffu = dffu[lst]
    dfrange = pd.date_range(dfjc.index.min(), dfjc.index.max() + MonthBegin(), freq='M')
    ddrange = pd.Series(dfrange).apply(lambda x: datetime.datetime.strftime(x, "%Y%m"))
    dffu = dffu.reindex(ddrange, fill_value=0)
    # 列尾行尾增加汇总
    dffu['行合计'] = dffu.apply(lambda x: x.sum(), axis=1)
    dffu.loc['列合计'] = dffu.apply(lambda x: x.sum())
    # print(dffu)

    lastestitems = tablehtml2evernote(dfjc[['entered']].head(5), notetitle.replace('统计图表', '记录'))
    stattable = tablehtml2evernote(dffu.sort_index(ascending=False), notetitle)
    hout = lastestitems + stattable
    # print(h)
    # print(hout)

    # 删掉列尾行尾的合计，并时间序列化index，为plot做准备
    del dffu['行合计']
    dffu = dffu.iloc[:-1]
    dffu['nianyue'] = dffu.index
    dffu['nianyue'] = dffu['nianyue'].apply(lambda x: pd.to_datetime("%s-%s-01" % (x[:4], x[-2:])))
    dffu.index = dffu['nianyue']
    del dffu['nianyue']
    # descdb(dffu)

    plt.figure()
    ax1 = plt.subplot2grid((5, 2), (0, 0), colspan=2, rowspan=2)
    # print(dffu.sum())
    ax1.plot(dffu.sum(axis=1).T)
    ax2 = plt.subplot2grid((5, 2), (3, 0), colspan=2, rowspan=2)
    # print(dffu.sum(axis=1).T)
    ax2.plot(dffu.sum())

    imglist = []
    # plt.show()
    global dirmainpath
    img_jinchu_path = str(dirmainpath / 'img' / 'jichubyfgongsi.png')
    plt.savefig(img_jinchu_path)
    imglist.append(img_jinchu_path)
    # print(imglist)
    plt.close()

    imglist2note(get_notestore(), imglist, destguid, notetitle, hout)


def jinchustattimer(jiangemiao):
    global cfplife
    items = cfplife.items('impinfolist')
    noteinfolistinside = []
    for address, infoslicelist in items:
        infoslist = [*args, wifilist] = infoslicelist.split('\n')
        infoslist.insert(1, address)
        infoslist.insert(-1, infoslist[-1].split(','))
        noteinfolistinside.append(infoslist[:-1])
    # print(noteinfolist)

    global dirmainpath
    dfjinchu = pd.DataFrame(jilugooglefile(dirmainpath / 'data' / 'google'))
    itemswifi = jilugmail('Ifttt/Wifi', 'wifi', 'all')
    if itemswifi:
        dfjinchuwifi = wifitodf(itemswifi, noteinfolistinside)
        dfjinchu = dfjinchu.append(dfjinchuwifi)

    try:
        dfjinchu = dfjinchu.append(jilugoogledrive())
    except Exception as eeee:
        log.critical('读取Goolge Drive中表格中数据记录时出现未名错误。%s' % (str(eeee)))

    # print(dfjinchu.shape[0])
    try:
        for noteinfo in noteinfolistinside:
            if len(noteinfo[0]) > 0:  # 有数据源笔记的guid就处理该笔记
                dfjinchunote = itemstodf(jilunote(noteinfo), noteinfo)  # 从evernote相应笔记中获取记录
            else:
                dfjinchunote = pd.DataFrame()
            # print(dfjinchunote)
            dfjinchuloop = dfjinchu.append(dfjinchunote)

            itemsgmail = jilugmail('Ifttt/Location', 'jinchu', noteinfo[2] + '_' + noteinfo[1], noteinfo[5])
            dfjinchugmail = itemstodf(itemsgmail, noteinfo)
            dfjinchuloop = dfjinchuloop.append(dfjinchugmail)
            # descdb(dfjinchuloop)
            dfjinchuloop = dfjinchuloop[dfjinchuloop.address == noteinfo[1]]  # 缩减记录集合，只处理当前循环项目相关记录
            if dfjinchuloop.shape[0] == 0:
                continue
            # descdb(dfjinchuloop)
            dfjinchuitem = dfjinchuloop[['entered', 'shuxing', 'address']]
            dfjinchuitem['time'] = dfjinchuitem.index
            dfjinchuitem.drop_duplicates(inplace=True)  # 默认根据全部列值进行判断，duplicated方法亦然，所以强增time列配合
            del dfjinchuitem['time']
            dfjinchuitem.sort_index(ascending=False, inplace=True)
            dfjinchucount = dfjinchuitem.shape[0]  # shape[0]获得行数，shape[1]则是列数
            print(dfjinchucount, end='\t')
            if cfp.has_option('jinchu', noteinfo[1]):
                ntupdatenum = dfjinchucount > cfp.getint('jinchu', noteinfo[1])  # 新数据集记录数和存档比较
            else:
                ntupdatenum = True
            print(ntupdatenum, end='\t')
            print(noteinfo[4], end='\t')
            print(dfjinchuitem.index[0])
            # descdb(dfjinchuitem)
            if ntupdatenum:  # or True:
                # print(dfjinchu.head(5))
                jinchustat(dfjinchuitem, noteinfo[1:])
                cfp.set('jinchu', noteinfo[1], '%d' % dfjinchucount)
                cfp.write(open(inifilepath, 'w', encoding='utf-8'))
                log.info('%s成功更新入图表统计笔记，将于%d秒后再次自动检查并更新' % (str(noteinfo), jiangemiao))
    except Exception as eee:
        log.critical('读取系列进出笔记并更新统计信息时出现未名错误。%s' % str(eee))
        # raise eee

    global timer_jinchu
    timer_jinchu = Timer(jiangemiao, jinchustattimer, [jiangemiao])
    # print(timer_jinchu)
    timer_jinchu.start()


if __name__ == '__main__':
    token = cfp.get('evernote', 'token')
    # findnotefromnotebook(token, 'c068e01f-1a7a-4e65-b8e4-ed93eed6bd0b', '统计')

    noteinfolist = [
        ['d8fa0226-88ac-4b6c-b8fd-63a9038a6abf', 'huadianxiaolu', 'home', '08a01c35-d16d-4b22-b7f7-61e3993fd2cb',
         '家进出统计图表（岳家嘴）', '白晔峰家附近区域进出记录', ['60bf0', '60bf0_5g', '60bf0_plus']],
        ['1ea50564-dee7-4e82-87b5-39703671e623', 'dingziqiao', 'life', '6eef085c-0e84-4753-bf3e-b45473a12274',
         '进出统计图表（丁字桥）', '丁字桥', ['wx-sgkf', '大浪淘沙']],
        ['24aad619-2356-499e-9fa7-f685af3a81b1', 'maotanhuamushichang', 'work', '2d908c33-d0a2-4d42-8d4d-5a0bc9d2ff7e',
         '公司进出记录统计图表', '花木市场', ['zysm3100', 'zysm2100', 'zysm4100', 'zysm5100', 'zysm_friends', 'zyck']],
        ['38f4b1a9-7d6e-4091-928e-c82d7d3717c5', 'qiwei', 'work', '294b584f-f34a-49f0-b4d3-08085a37bfd5',
         '进出统计图表（创食人）', '创食人', ['qw2', 'zcb']]
    ]

    jinchustattimer(60 * 32)

    # dfjilu = jilugmail('Ifttt/SmsLog', 'smslog', 'all', bodyonly=False)
    # print(dfjilu[:200])

    # itemswifi = jilugmail('Ifttt/Wifi', 'wifi', 'all')
    # dfout = wifitodf(itemswifi, noteinfolist)
    # descdb(dfout)

    # dfjilunotifi = jilugmail('Ifttt/Notification', 'notification', 'all')
    # print(dfjilunotifi[:200])
    # dfnoti = notification2df(dfjilunotifi)
    # descdb(dfnoti)

    # jinchustattimer(token,60*8)
