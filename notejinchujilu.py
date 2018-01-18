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
2d908c33-d0a2-4d42-8d4d-5a0bc9d2ff7e 公司进出记录统计图表

08a01c35-d16d-4b22-b7f7-61e3993fd2cb 家附近出入统计

"""

from imp4nb import *
from bs4 import BeautifulSoup

from matplotlib.ticker import MultipleLocator, FuncFormatter


def jilustat(token, note_store, sourceguid, destguid=None, title=''):
    """
    读取ifttt自动通过gmail转发至evernote生成的地段进出记录，统计作图展示
    :rtype: Null
    """
    soup = BeautifulSoup(note_store.getNoteContent(sourceguid), "html.parser")
    evernoteapijiayi()
    tags = soup.find('p')

    # 生成英文的月份列表，组装正则模式，以便准确识别
    yuefenlist = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'September', 'October', 'December',
                  'November']
    yuefennames = str(yuefenlist[0])
    for a in range(1, len(yuefenlist)):
        yuefennames += '|' + str(yuefenlist[a])
    yuefennames = '(?:' + yuefennames + ')'  # (?:January|February|March|April|May|June|July|September|October|December|November)
    # print(yuefennames)
    # pattern = u'(\w*\s*\d+,\s*\d{4}\s*at\s*\d{2}:\d{2}[AP]M)\s：\s(e(?:xit|nter)ed)'
    pattern = u'(%s\s*\d+,\s*\d{4}\s*at\s*\d{2}:\d{2}[AP]M)\s：\s(e(?:xit|nter)ed)' % yuefennames
    pattern = u'(%s\s*\d+,\s*\d{4}\s*at\s*\d{2}:\d{2}[AP]M)\s*：\s*(e(?:xit|nter)ed)' % yuefennames
    slice = re.split(pattern, soup.get_text())
    print(slice)
    # 提取时间和进出信息
    split_item = []
    for i in range(1, len(slice), 3):
        zhizi = []
        zhizi.append(slice[i])
        zhizi.append(slice[i + 1])
        split_item.append(zhizi)

    print(split_item)
    dfjc = pd.DataFrame(split_item, columns=['atime', 'eort'])
    dfjc = dfjc.drop_duplicates(['atime', 'eort'])  # 去重
    dfjc['atime'] = dfjc['atime'].apply(
        lambda x: pd.to_datetime(time.strftime('%Y-%m-%d %H:%M', time.strptime(x, '%B %d, %Y at %I:%M%p'))))
    dfjc.index = dfjc['atime']
    dfjc = dfjc.sort_index()  # 排序
    dfjc['enter'] = dfjc['eort'].apply(lambda x: True if x == 'entered' else False)
    dfjc['nianyue'] = dfjc['atime'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m'))
    dfjc['小时'] = dfjc['atime'].apply(lambda x: datetime.datetime.strftime(x, '%H'))
    del dfjc['eort']
    print(dfjc.tail())
    dfff = dfjc[dfjc.enter == True].groupby(['nianyue', '小时'])['enter'].count()
    dffu = dfff.unstack(fill_value=0)
    print(dffu)

    # 补满小时数和年月份
    for i in range(24):
        colname = '%02d' % i
        if colname not in list(dffu.columns):
            dffu[colname] = 0
    lst = sort(list(dffu.columns))
    dffu = dffu[lst]
    drange = pd.date_range(dfjc.index.min(), dfjc.index.max() + MonthBegin(), freq='M')
    ddrange = pd.Series(drange).apply(lambda x: datetime.datetime.strftime(x, "%Y%m"))
    dffu = dffu.reindex(ddrange, fill_value=0)
    # 列尾行尾增加汇总
    dffu['行合计'] = dffu.apply(lambda x: x.sum(), axis=1)
    dffu.loc['列合计'] = dffu.apply(lambda x: x.sum())
    print(dffu)
    h = dffu.to_html()
    h = h.replace('class="dataframe"', '')
    # print(h)

    # 删掉列尾行尾的合计，并时间序列化index，为plot做准备
    del dffu['行合计']
    dffu = dffu.iloc[:-1]
    dffu['nianyue'] = dffu.index
    dffu['nianyue'] = dffu['nianyue'].apply(lambda x: pd.to_datetime("%s-%s-01" % (x[:4], x[-2:])))
    dffu.index = dffu['nianyue']
    del dffu['nianyue']

    plt.figure()
    ax1 = plt.subplot2grid((5, 2), (0, 0), colspan=2, rowspan=2)
    print(dffu.sum())
    ax1.plot(dffu.sum())
    ax2 = plt.subplot2grid((5, 2), (3, 0), colspan=2, rowspan=2)
    print(dffu.sum(axis=1).T)
    ax2.plot(dffu.sum(axis=1).T)

    imglist = []
    # plt.show()
    img_sunonoff_path = 'img\\jichubyfgongsi.png'
    plt.savefig(img_sunonoff_path)
    imglist.append(img_sunonoff_path)
    plt.close()

    imglist2note(note_store, imglist, destguid, title, token, neirong=h)
