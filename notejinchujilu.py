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

from imp4nb import *
from bs4 import BeautifulSoup
from matplotlib.ticker import MultipleLocator, FuncFormatter
import pygsheets


def readfromtxt(fn):
    if not os.path.exists(fn):
        newfile = open(fn, 'w', encoding='utf-8')
        newfile.close()
    with open(fn, 'r', encoding='utf-8') as f:
        items = [line.strip().replace('\r', '').replace('\n', '') for line in f]
    # print(items)
    f.close()

    return items


def jilugooglefile(filepath):
    filelist = [ff for ff in listdir(filepath) if isfile(join(filepath, ff))]
    print(filelist)
    dfout = None
    for i in range(len(filelist)):
        df = pd.read_excel('%s\\%s' % (filepath, filelist[i]), sheetname='工作表1',
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
    gc = pygsheets.authorize(service_file='ewjinchu.json')
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


def jilugmail(dir, mingmu, fenleistr='', topic='', bodyonly=True):
    host = cfp.get('gmail', 'host')
    username = cfp.get('gmail', 'username')
    password = cfp.get('gmail', 'password')
    mailitems = []
    try:
        # mailitems = getMail(host, username, password, dirtarget='Ifttt/Location', unseen=False, topic=noteinfos[5])
        mailitems = getMail(host, username, password, debug=False, dirtarget=dir, unseen=True, topic=topic)
    except socket.error as se:
        log.critical("构建socket连接时出错。%s" % str(se))
    except Exception as e:
        log.critical('处理邮件时出现严重错误。%s' % str(e))

    itemslst = []
    for header, body in mailitems:
        for text, textstr in body:
            if text.startswith('text'):  # 只取用纯文本部分
                if bodyonly:  # 只要邮件body文本，否则增加邮件标题部分内容
                    itemslst.append(textstr)
                elif header[1].startswith('SMS with') or header[1].endswith('的短信记录') or header[1].endswith(
                        '的通话记录'):  # 对特别记录增补时间戳
                    itemslst.append(header[1] + '\t' + str(header[0]) + '，' + textstr)
                else:
                    itemslst.append(header[1] + '\t' + textstr)  #
    # print('从Gmail邮箱获取%d条进出记录信息记录' %len(itemslst))
    # print(itemslst)

    # txtfilename = 'data\\ifttt\\'+'%s_gmail_'+noteinfos[2]+'_'+noteinfos[1]+'.txt' %mingmu
    txtfilename = 'data\\ifttt\\' + '%s_gmail_%s.txt' % (mingmu, fenleistr)
    if len(itemslst) > 0:
        items = itemslst + readfromtxt(txtfilename)
        # items = itemslst
        fb = open(txtfilename, 'w', encoding='utf-8')
        for item in items:
            fb.write(str(item) + '\n')
        fb.close()

    items = readfromtxt(txtfilename)

    resultstr = ''.join(items)
    # print(resultstr)

    return resultstr


def jilunote(token, noteinfos):
    """
    读取ifttt自动通过gmail转发至evernote生成的地段进出记录，统计作图展示
    :rtype: Null
    """
    itemstr = BeautifulSoup(get_notestore(token).getNoteContent(noteinfos[0]), "html.parser"). \
        get_text().replace('\r', '').replace('\n', '')  # 文本化后去掉回车、换行符等
    # print('笔记："%s" 中提取内容' %noteinfos[5])
    # print(itemstr)
    evernoteapijiayi()
    # tags = soup.find('p')
    # print(tags)

    return itemstr


def itemstodf(itemstr, noteinfos):

    # 生成英文的月份列表，组装正则模式，以便准确识别
    yuefenlist = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'September', 'October',
                  'December', 'November']
    yuefennames = str(yuefenlist[0])
    for a in range(1, len(yuefenlist)):
        yuefennames += '|' + str(yuefenlist[a])
    yuefennames = '(?:' + yuefennames + ')'  # (?:January|February|March|April|May|June|July|September|October|December|November)
    # print(yuefennames)
    # pattern = u'(\w*\s*\d+,\s*\d{4}\s*at\s*\d{2}:\d{2}[AP]M)\s：\s(e(?:xit|nter)ed)'
    # pattern = u'(%s\s*\d+,\s*\d{4}\s*at\s*\d{2}:\d{2}[AP]M)\s：\s(e(?:xit|nter)ed)' % yuefennames
    pattern = u'(%s\s*\d+,\s*\d{4}\s*at\s*\d{2}:\d{2}[AP]M)\s*：.*?\s*(e(?:xit|nter)ed)' % yuefennames
    # print(pattern)
    slicesoup = re.split(pattern, itemstr)
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


def jinchustat(token, jinchujiluall, noteinfos):
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
    dfff = dfjc[dfjc.entered == False].groupby(['nianyue', '小时'])['entered'].count()  #以离开为进出标准
    dffu = dfff.unstack(fill_value=0)
    # print(dffu)

    # 补满小时数和年月份
    for i in range(24):
        colname = '%02d' % i
        if colname not in list(dffu.columns):
            dffu[colname] = 0
    lst = sort(list(dffu.columns))
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
    img_jinchu_path = 'img\\jichubyfgongsi.png'
    plt.savefig(img_jinchu_path)
    imglist.append(img_jinchu_path)
    # print(imglist)
    plt.close()

    imglist2note(get_notestore(token), imglist, destguid, notetitle, hout)


def jinchustattimer(token, jiangemiao):
    dfjilu = jilugmail('Ifttt/Wifi', 'wifi', 'all')
    print(dfjilu[:200])
    dfjilu = jilugmail('Ifttt/Notification', 'notification', 'all')
    print(dfjilu[:200])
    dfjilu = jilugmail('Ifttt/CallSmsLog', 'callsmslog', 'all', bodyonly=False)
    print(dfjilu[:200])

    noteinfolist = [
        ['', 'yangfu\'restraunaut', 'life', '06bb4996-d0d8-4266-87d5-f3283d71f58e', '进出统计图表（东西湖）', '东西湖进出记录'],
        ['', 'fanyuan', 'life', 'db59af11-fb1c-4864-a7da-0989452e170f', '进出统计图表（范渊）', '范渊进出记录'],
        ['', 'liyang', 'life', '76a9d82c-5a22-4cb6-9acf-13426a2be3b7', '进出统计图表（立阳）', '立阳进出记录'],
        ['f119e38e-3876-4937-80f1-e6a6b2e5d3d0', 'wenchanglu', 'work', '7f4bec82-626b-4022-b3c2-0d9b3d71198d',
         '进出统计图表（文昌路金地格林）', '文昌路'],
        ['d8fa0226-88ac-4b6c-b8fd-63a9038a6abf', 'huadianxiaolu', 'home', '08a01c35-d16d-4b22-b7f7-61e3993fd2cb',
         '家进出统计图表（岳家嘴）', '白晔峰家附近区域进出记录'],
        ['1ea50564-dee7-4e82-87b5-39703671e623', 'dingziqiao', 'life', '6eef085c-0e84-4753-bf3e-b45473a12274',
         '进出统计图表（丁字桥）', '丁字桥'],
        ['', 'daye', 'home', 'ba1d98ff-be3b-400a-bb59-ce78efca45fc', '家进出统计图表（大冶）', '白晔峰家大冶进出记录'],
        ['9ac941cc-c04b-4d4b-879f-2bfb044382d4', 'lushan', 'home', '987c1d5e-d8ad-41aa-9269-d2b840616410',
         '家进出统计图表（鲁山）', '鲁山'],
        ['84e9ee0b-30c3-4404-84e2-7b4614980b4b', 'hanyangban', 'work', 'a7e84055-f075-44ab-8205-5a42f3f05284',
         '进出记录统计图表（汉阳办）', '汉阳办'],
        ['6fb1e016-01ab-439d-929e-994dc980ddbe', 'hankouban', 'work', '2c5e3728-be69-4e52-a8ff-07860e8593b7',
         '进出记录统计图表（汉口办）', '汉口办'],
        ['24aad619-2356-499e-9fa7-f685af3a81b1', 'maotanhuamushichang', 'work', '2d908c33-d0a2-4d42-8d4d-5a0bc9d2ff7e',
         '公司进出记录统计图表', '花木市场'],
        ['38f4b1a9-7d6e-4091-928e-c82d7d3717c5', 'qiwei', 'work', '294b584f-f34a-49f0-b4d3-08085a37bfd5',
         '进出统计图表（创食人）', '创食人']
    ]
    dfjinchugooglefile = jilugooglefile('data\\google')
    dfjinchugoogle = pd.DataFrame()
    try:
        dfjinchugoogle = dfjinchugooglefile.append(jilugoogledrive())
    except Exception as e:
        log.critical('读取Goolge Drive中表格中数据记录时出现未名错误。%s' % (str(e)))

    try:
        for noteinfo in noteinfolist:
            if len(noteinfo[0]) > 0:  # 有数据源笔记的guid就处理该笔记
                dfjinchunote = itemstodf(jilunote(token, noteinfo), noteinfo)  # 从evernote相应笔记中获取记录
                # print(dfjinchunote.shape[0])
            else:
                dfjinchunote = pd.DataFrame()

            dfjinchugmail = itemstodf(
                jilugmail('Ifttt/Location', 'jinchu', noteinfo[2] + '_' + noteinfo[1], noteinfo[5]), noteinfo)
            # print(dfjinchugmail.shape[0])
            dfjinchu = dfjinchugoogle.append(dfjinchunote).append(dfjinchugmail)
            # print(dfjinchu.groupby(['address']).count())
            dfjinchu = dfjinchu[dfjinchu.address == noteinfo[1]]  # 缩减记录集合，只处理当前循环项目相关记录
            if dfjinchu.shape[0] == 0:
                continue
            dfjinchu['time'] = dfjinchu.index
            dfjinchu.drop_duplicates(inplace=True)  # 默认根据全部列值进行判断，duplicated方法亦然，所以强增time列配合
            del dfjinchu['time']
            dfjinchu.sort_index(ascending=False, inplace=True)
            dfjinchucount = dfjinchu.shape[0]  # shape[0]获得行数，shape[1]则是列数
            print(dfjinchucount, end='\t')
            if cfp.has_option('jinchu', noteinfo[1]):
                ntupdatenum = dfjinchucount > cfp.getint('jinchu', noteinfo[1])  # 新数据集记录数和存档比较
            else:
                ntupdatenum = True
            print(ntupdatenum, end='\t')
            print(noteinfo[4], end='\t')
            print(dfjinchu.index[0])
            if ntupdatenum:  # or True:
                # print(dfjinchu.head(5))
                jinchustat(token, dfjinchu, noteinfo[1:])
                cfp.set('jinchu', noteinfo[1], '%d' % dfjinchucount)
                cfp.write(open(inifilepath, 'w', encoding='utf-8'))
                log.info('%s成功更新入图表统计笔记，将于%d秒后再次自动检查并更新' % (str(noteinfo), jiangemiao))
    except Exception as e:
        log.critical('读取系列进出笔记并更新统计信息时出现未名错误。%s' % (str(e)))

    global timer_jinchu
    timer_jinchu = Timer(jiangemiao, jinchustattimer, (token, jiangemiao))
    # print(timer_jinchu)
    timer_jinchu.start()


if __name__ == '__main__':
    token = cfp.get('evernote', 'token')
    # findnotefromnotebook(token, 'c068e01f-1a7a-4e65-b8e4-ed93eed6bd0b', '统计')
    # jinchustattimer(token, 60*32)
    dfjilu = jilugmail('Ifttt/SmsLog', 'smslog', 'all', bodyonly=False)
    print(dfjilu[:200])
