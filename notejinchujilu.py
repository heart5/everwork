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
25967ecd-4062-4eed-bfa2-ac7fbe499154 白晔峰家（鲁山）进出记录

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


def jilugoogle(filepath):
    filelist = [ff for ff in listdir(filepath) if isfile(join(filepath, ff))]
    print(filelist)
    for i in range(len(filelist)):
        df = pd.read_excel('%s\\%s' % (filepath, filelist[i]), sheetname='工作表1',
                           header=None, index_col=0, parse_dates=True)
        if df.shape[0] == 0:
            log.info('%s 无进出记录')
            continue
        # descdb(df)
        df['shuxing'] = df.iloc[:, 1].apply(lambda x: x.split(' ')[0])
        df['didian'] = df.iloc[:, 1].apply(lambda x: x.split(' ')[1])
        df['entered'] = df.iloc[:, 0].apply(lambda x: True if x == 'entered' else False)
        dff = df.iloc[:, [6, 4, 5]]
        dff.columns = ['entered', 'shuxing', 'address']
        if i == 0:
            dfout = dff
        else:
            dfout = dfout.append(dff).sort_index()

    return dfout


def jilunote(note_store, notelists):
    """
    读取ifttt自动通过gmail转发至evernote生成的地段进出记录，统计作图展示
    :rtype: Null
    """
    for num in range(len(notelists)):
        soup = BeautifulSoup(note_store.getNoteContent(notelists[num][0]), "html.parser")
        # print(soup)
        evernoteapijiayi()
        # tags = soup.find('p')
        # print(tags)

        # 生成英文的月份列表，组装正则模式，以便准确识别
        yuefenlist = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'September', 'October',
                      'December',
                      'November']
        yuefennames = str(yuefenlist[0])
        for a in range(1, len(yuefenlist)):
            yuefennames += '|' + str(yuefenlist[a])
        yuefennames = '(?:' + yuefennames + ')'  # (?:January|February|March|April|May|June|July|September|October|December|November)
        # print(yuefennames)
        # pattern = u'(\w*\s*\d+,\s*\d{4}\s*at\s*\d{2}:\d{2}[AP]M)\s：\s(e(?:xit|nter)ed)'
        # pattern = u'(%s\s*\d+,\s*\d{4}\s*at\s*\d{2}:\d{2}[AP]M)\s：\s(e(?:xit|nter)ed)' % yuefennames
        pattern = u'(%s\s*\d+,\s*\d{4}\s*at\s*\d{2}:\d{2}[AP]M)\s*：.*?\s*(e(?:xit|nter)ed)' % yuefennames
        # print(pattern)
        slicesoup = re.split(pattern, soup.get_text())
        print(slicesoup)
        # 提取时间和进出信息
        split_item = []
        for i in range(1, len(slicesoup), 3):
            zhizi = list()
            zhizi.append(slicesoup[i])
            zhizi.append(slicesoup[i + 1])
            split_item.append(zhizi)

        print(split_item)
        dfjc = pd.DataFrame(split_item, columns=['atime', 'eort'])
        dfjc = dfjc.drop_duplicates(['atime', 'eort'])  # 去重
        dfjc['atime'] = dfjc['atime'].apply(
            lambda x: pd.to_datetime(time.strftime('%Y-%m-%d %H:%M', time.strptime(x, '%B %d, %Y at %I:%M%p'))))
        dfjc.index = dfjc['atime']
        dfjc = dfjc.sort_index()  # 排序
        dfjc['entered'] = dfjc['eort'].apply(lambda x: True if x == 'entered' else False)
        dfjc['shuxing'] = notelists[num][2]
        dfjc['address'] = notelists[num][1]
        dfjc = dfjc[['entered', 'shuxing', 'address']]
        if num == 0:
            dfout = dfjc
        else:
            dfout = dfout.append(dfjc)

    return dfout


def jinchustat(token, note_store, jinchujiluall, noteoutputlists):
    """
    读取ifttt自动通过gmail转发至evernote生成的地段进出记录，统计作图展示
    :rtype: Null
    """
    noteoutputlists = pd.DataFrame(noteoutputlists)
    # print(noteoutputlists)
    adrlst = list(noteoutputlists.iloc[:, 0])
    for address in adrlst:
        destguid = noteoutputlists[noteoutputlists.iloc[:, 0] == address].iloc[:, 1].values[0]
        notetitle = noteoutputlists[noteoutputlists.iloc[:, 0] == address].iloc[:, 2].values[0]
        # print(destguid)
        # print(notetitle)
        dfjc = jinchujiluall[jinchujiluall.address == address][['entered']]
        # descdb(dfjc)
        dfjc['atime'] = dfjc.index
        dfjc['nianyue'] = dfjc['atime'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m'))
        dfjc['小时'] = dfjc['atime'].apply(lambda x: datetime.datetime.strftime(x, '%H'))
        # print(dfjc.tail(10))
        dfff = dfjc[dfjc.entered == True].groupby(['nianyue', '小时'])['entered'].count()
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
        h = dffu.to_html(justify='right')
        hout = h.replace('class="dataframe">', 'align="center">')
        hout = hout.replace('<table', '\n<h3 align="center">%s</h3>\n<table' % notetitle)
        # print(h)
        # print(hout)

        # 删掉列尾行尾的合计，并时间序列化index，为plot做准备
        del dffu['行合计']
        dffu = dffu.iloc[:-1]
        dffu['nianyue'] = dffu.index
        dffu['nianyue'] = dffu['nianyue'].apply(lambda x: pd.to_datetime("%s-%s-01" % (x[:4], x[-2:])))
        dffu.index = dffu['nianyue']
        del dffu['nianyue']

        plt.figure()
        ax1 = plt.subplot2grid((5, 2), (0, 0), colspan=2, rowspan=2)
        # print(dffu.sum())
        ax1.plot(dffu.sum())
        ax2 = plt.subplot2grid((5, 2), (3, 0), colspan=2, rowspan=2)
        # print(dffu.sum(axis=1).T)
        ax2.plot(dffu.sum(axis=1).T)

        imglist = []
        # plt.show()
        img_sunonoff_path = 'img\\jichubyfgongsi.png'
        plt.savefig(img_sunonoff_path)
        imglist.append(img_sunonoff_path)
        plt.close()

        imglist2note(note_store, imglist, destguid, notetitle, token, neirong=hout)
