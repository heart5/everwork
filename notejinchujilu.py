#
# encoding:utf-8
#
"""
处理进出记录笔记，生成图表呈现

笔记本《行政管理》guid：31eee750-e240-438b-a1f5-03ce34c904b4
源信息笔记guid和标题如下：
f119e38e-3876-4937-80f1-e6a6b2e5d3d0 白晔峰公司文昌路进出记录
24aad619-2356-499e-9fa7-f685af3a81b1 白晔峰公司花木市场进出记录
84e9ee0b-30c3-4404-84e2-7b4614980b4b 汉阳办进出记录
6fb1e016-01ab-439d-929e-994dc980ddbe 汉口办进出记录
38f4b1a9-7d6e-4091-928e-c82d7d3717c5 创食人公司进出记录

"""

from imp4nb import *
from bs4 import BeautifulSoup

from matplotlib.ticker import MultipleLocator, FuncFormatter


def jilustat(token, note_store, sourceguid, destguid=None):
    """

    :rtype: Null
    """
    soup = BeautifulSoup(note_store.getNoteContent(sourceguid), "html.parser")
    evernoteapijiayi()
    tags = soup.find('p')
    # print(tags)
    # print(soup.get_text())

    yuefenlist = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'September', 'October', 'December',
                  'November']
    yuefennames = str(yuefenlist[0])
    for a in range(1, len(yuefenlist)):
        yuefennames += '|' + str(yuefenlist[a])
    yuefennames = '(?:' + yuefennames + ')'  # (?:January|February|March|April|May|June|July|September|October|December|November)
    print(yuefennames)
    pattern = u'(\w*\s*\d+,\s*\d{4}\s*at\s*\d{2}:\d{2}[AP]M)\s：\s(e(?:xit|nter)ed)'
    pattern = u'(%s\s*\d+,\s*\d{4}\s*at\s*\d{2}:\d{2}[AP]M)\s：\s(e(?:xit|nter)ed)' % yuefennames
    slice = re.split(pattern, soup.get_text())
    print(slice)
    split_item = []
    for i in range(1, len(slice), 3):
        zhizi = []
        zhizi.append(slice[i])
        zhizi.append(slice[i + 1])
        split_item.append(zhizi)

    print(split_item)
    dfjc = pd.DataFrame(split_item, columns=['atime', 'eort'])
    dfjc['atime'] = dfjc['atime'].apply(
        lambda x: pd.to_datetime(time.strftime('%Y-%m-%d', time.strptime(x, '%B %d, %Y at %I:%M%p'))))
    print(dfjc.shape[0])
    dfjc = dfjc.drop_duplicates(['atime', 'eort'])
    dfjc.index = dfjc['atime']
    del dfjc['atime']
    print(dfjc.shape[0])
    dfjc = dfjc.sort_index()
    dfjc['exit'] = dfjc['eort'].apply(lambda x: True if x == 'exited' else False)
    dfjc['enter'] = dfjc['eort'].apply(lambda x: True if x == 'entered' else False)
    del dfjc['eort']
    # dfjc.groupby(dfjc.index)
    print(dfjc[dfjc.enter == True].tail())

    # dfre = dfjc.reindex(pd.date_range(dfjc.index.min(),periods=(dfjc.index.max() -dfjc.index.min()).days +1))
    # print(dfre)
    dfff = dfjc.resample('D')['enter'].count()
    print(dfff)
    dffff = dfff.resample('M').count()
    print(dffff)
    # plt.plot(dfff)

    imglist = []
    plt.show()
    # img_sunonoff_path = 'img\\weather\\sunonoff.png'
    # plt.savefig(img_sunonoff_path)
    # imglist.append(img_sunonoff_path)
    plt.close()

    # imglist2note(note_store, imglist, destguid, '武汉天气图', token)
