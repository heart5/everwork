#
# encoding:utf-8
#
"""
处理每日天气信息，生成图表呈现

笔记本《行政管理》：31eee750-e240-438b-a1f5-03ce34c904b4
e5d81ffa-89e7-49ff-bd4c-a5a71ae14320 武汉雨天记录
277dff5e-7042-47c0-9d7b-aae270f903b8 武汉每日天气
输出笔记：
296f57a3-c660-4dd5-885a-56492deb2cee 武汉天气图
"""


from imp4nb import *
from bs4 import BeautifulSoup

from matplotlib.ticker import MultipleLocator, FuncFormatter


def weatherstat(token, note_store, sourceguid, destguid=None):
    """

    :rtype: Null
    """
    soup = BeautifulSoup(note_store.getNoteContent(sourceguid), "html.parser")
    evernoteapijiayi()
    # tags = soup.find('en-note')
    # print tags
    # print soup.get_text()

    pattern = u'(\w*\s*\d+,\s*\d{4}\s*at\s*\d{2}:\d{2}[AP]M)\s+'
    slice = re.split(pattern, soup.get_text())
    # print len(slice)
    split_item = []
    for i in range(1, len(slice), 2):
        split_item.append(slice[i] + " " + slice[i + 1])

    # print len(split_item)
    # print split_item[-1]
    # print split_item
    # for t in split_item:
    #     print t

    itempattern = re.compile(
        u'(?P<date>\w*\s*\d+,\s*\d{4}\s*at\s*\d{2}:\d{2}[AP]M)\s+：最高温度\s*(?P<gaowen>-?\d*)\s*℃，'
        u'最低温度(?P<diwen>-?\d*)\s*℃；风速：\s*(?P<fengsu>\d*) \s*，风向：(?P<fengxiang>\w*)；'
        u'(?:污染：*\s*Not Available；)*日出：\s*(?P<sunon>\w*\s*\d+,\s*\d{4}\s*at\s*\d{2}:\d{2}[AP]M)，'
        u'日落：(?:Sunset:)*\s*(?P<sunoff>\w*\s*\d+,\s*\d{4}\s*at\s*\d{2}:\d{2}[AP]M)；湿度：(?P<shidu>\w*)%')
    # print re.findall(itempattern, itemtext)
    # timestr = 'August 12, 2017 at 06:00AM'
    # itemtime = time.strptime(timestr, '%B %d, %Y at %I:%M%p')
    # print itemtime

    data_list = []
    for ii in split_item:
        for jj in re.findall(itempattern, ii):
            stritem = [pd.Timestamp(jj[0]),
                       int(jj[1]), int(jj[2]), int(jj[3]), jj[4],
                       # pd.Timestamp(jj[5]).strftime("%I%M"),
                       int(pd.Timestamp(jj[5]).strftime("%H")) * 60 + int(pd.Timestamp(jj[5]).strftime("%M")),
                       # pd.Timestamp(jj[6]),
                       int(pd.Timestamp(jj[6]).strftime("%H")) * 60 + int(pd.Timestamp(jj[6]).strftime("%M")),
                       int(jj[7])]
            datei = stritem[0]
            dates = "%04d-%02d-%02d" %(datei.year, datei.month, datei.day)
            # print(str(datei)+'\t'+dates)
            stritem[0] = pd.to_datetime(dates)
        # print stritem
        data_list.append(stritem)

    print (len(data_list))
    print (data_list[-1])


    df = pd.DataFrame(data_list,
                      columns=['date', 'gaowen', 'diwen', 'fengsu', 'fengxiang', 'sunon', 'sunoff', 'shidu'])
    df.index = df['date']
    df['richang'] = df['sunoff'] - df['sunon']
    df['richang'] = df['richang'].astype(int)
    df['wendu'] = (df['gaowen'] + df['diwen'])/2
    df['wendu'] = df['wendu'].astype(int)
    df['fengsu'] = df['fengsu'].astype(int)

    # print(df.head())

    df_recent_year = df.iloc[-364:]
    # print(df[df.gaowen == df.iloc[-364:]['gaowen'].max()])
    df_before_year = df.iloc[:-364]

    plt.figure(figsize=(16, 20))
    ax1 = plt.subplot2grid((4,2),(0,0),colspan=2,rowspan = 2)
    ax1.plot(df['gaowen'], lw=0.3, label=u'日高温')
    ax1.plot(df['diwen'], lw=0.3, label=u'日低温')
    ax1.plot(df['wendu'], 'g', lw=0.7, label=u'日温度（高温低温平均）')
    quyangtianshu = 10
    ax1.plot(df['wendu'].resample('%dD' %quyangtianshu).mean(),'b', lw=1.2,label='日温度（每%d天平均）' %quyangtianshu)
    ax1.plot(df[df.fengsu > 5]['fengsu'],'*',label='风速（大于五级）')
    plt.legend()
    #起始统计日
    kedu = df.iloc[0]
    ax1.plot([kedu['date'],kedu['date']],[0,kedu['wendu']],'c--',lw=0.4)
    ax1.scatter([kedu['date'],],[kedu['wendu']],50,color='Wheat')
    fsize = 8
    txt = str(kedu['wendu'])
    ax1.annotate(txt,xy=(kedu['date'],kedu['wendu']),xycoords='data',
            xytext=(-(len(txt)*fsize), +20), textcoords='offset points',fontsize=fsize,
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2",color='Purple'))

    dates = "%02d-%02d" % (kedu['date'].month, kedu['date'].day)
    ax1.annotate(dates,xy=(kedu['date'],0),xycoords='data',
            xytext=(-10, -20), textcoords='offset points',fontsize=8,
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"))
    #去年今日
    kedu = df.iloc[-364]
    # print(kedu)
    ax1.plot([kedu['date'],kedu['date']],[0,kedu['wendu']],'c--')
    ax1.scatter([kedu['date'],],[kedu['wendu']],50,color='Wheat')
    ax1.annotate(str(kedu['wendu']),xy=(kedu['date'],kedu['wendu']),xycoords='data',
            xytext=(-5, +20), textcoords='offset points',
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2",color='Purple'))
    dates = "%02d-%02d" % (kedu['date'].month, kedu['date'].day)
    ax1.annotate(dates,xy=(kedu['date'],0),xycoords='data',
            xytext=(-10, -20), textcoords='offset points',fontsize=8,
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"))
    #今日
    kedu = df.iloc[-1]
    # print(kedu)
    ax1.plot([kedu['date'],kedu['date']],[0,kedu['wendu']],'c--')
    ax1.scatter([kedu['date'],],[kedu['wendu']],50,color='BlueViolet')
    dates = "%02d-%02d" % (kedu['date'].month, kedu['date'].day)
    ax1.annotate(dates,xy=(kedu['date'],0),xycoords='data',
            xytext=(-10, -20), textcoords='offset points',fontsize=8,
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"))

    #最近一年最高温
    kedu = df_recent_year[df_recent_year.gaowen == df_recent_year.iloc[-364:]['gaowen'].max()].iloc[0]
    # print(kedu)
    ax1.plot([kedu['date'],kedu['date']],[0,kedu['gaowen']],'c--')
    ax1.scatter([kedu['date'],],[kedu['gaowen']],50,color='Wheat')
    ax1.annotate(str(kedu['gaowen']),xy=(kedu['date'],kedu['gaowen']),xycoords='data',
            xytext=(-20, +5), textcoords='offset points',
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2",color='Purple'))
    dates = "%02d-%02d" % (kedu['date'].month, kedu['date'].day)
    ax1.annotate(dates,xy=(kedu['date'],0),xycoords='data',
            xytext=(-10, -20), textcoords='offset points',fontsize=8,
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"))
    #最近一年最低温
    kedu = df_recent_year[df_recent_year.diwen == df_recent_year.iloc[-364:]['diwen'].min()].iloc[0]
    ax1.plot([kedu['date'],kedu['date']],[0,kedu['diwen']],'c--')
    ax1.scatter([kedu['date'],],[kedu['diwen']],50,color='Wheat')
    ax1.annotate(str(kedu['diwen']),xy=(kedu['date'],kedu['diwen']),xycoords='data',
            xytext=(-20, +5), textcoords='offset points',
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2",color='Purple'))
    dates = "%02d-%02d" % (kedu['date'].month, kedu['date'].day)
    ax1.annotate(dates,xy=(kedu['date'],0),xycoords='data',
            xytext=(-10, -20), textcoords='offset points',fontsize=8,
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"))
    #最高温
    kedu = df[df.gaowen == df['gaowen'].max()].iloc[0]
    ax1.plot([kedu['date'],kedu['date']],[0,kedu['gaowen']],'c--')
    ax1.scatter([kedu['date'],],[kedu['gaowen']],50,color='Wheat')
    ax1.annotate(str(kedu['gaowen']),xy=(kedu['date'],kedu['gaowen']),xycoords='data',
            xytext=(-20, +5), textcoords='offset points',
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2",color='Purple'))
    dates = "%02d-%02d" % (kedu['date'].month, kedu['date'].day)
    ax1.annotate(dates,xy=(kedu['date'],0),xycoords='data',
            xytext=(-10, -20), textcoords='offset points',fontsize=8,
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"))
    #最低温
    kedu = df[df.diwen == df['diwen'].min()].iloc[0]
    ax1.plot([kedu['date'],kedu['date']],[0,kedu['diwen']],'c--')
    ax1.scatter([kedu['date'],],[kedu['diwen']],50,color='Wheat')
    ax1.annotate(str(kedu['diwen']),xy=(kedu['date'],kedu['diwen']),xycoords='data',
            xytext=(-20, +5), textcoords='offset points',
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2",color='Purple'))
    dates = "%02d-%02d" % (kedu['date'].month, kedu['date'].day)
    ax1.annotate(dates,xy=(kedu['date'],0),xycoords='data',
            xytext=(-10, -20), textcoords='offset points',fontsize=8,
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"))
    ax1.set_ylabel(u'（摄氏度℃）')
    ax1.grid(True)
    ax1.set_title(u'最高气温、最低气温和均值温度图')


    ax3 = plt.subplot2grid((4, 2), (2, 0), colspan=2, rowspan=2)
    # print(type(ax3))
    ax3.plot(df_recent_year['shidu'], 'c.', lw=0.3, label=u'湿度')
    ax3.plot(df_recent_year['shidu'].resample('15D').mean(),'g', lw=1.5)
    ax3.set_ylabel(u'（百分比%）')
    ax3.set_title(u'半月平均湿度图')

    img_wenshifeng_path = "img\\weather\\wenshifeng.png"
    plt.savefig(img_wenshifeng_path)

    imglist = []
    imglist.append(img_wenshifeng_path)
    plt.close()


    plt.figure(figsize=(16,10))
    fig,ax1 = plt.subplots()
    plt.plot(df['date'], df['sunon'], lw=0.8, label=u'日出')
    plt.plot(df['date'], df['sunoff'], lw=0.8, label=u'日落')
    ax = plt.gca()
    # ax.yaxis.set_major_formatter(FuncFormatter(min_formatter)) # 主刻度文本用pi_formatter函数计算
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x,pos: "%02d:%02d" %(int(x/60), int(x%60))))  # 主刻度文本用pi_formatter函数计算
    plt.ylim((0,24*60))
    plt.yticks(np.linspace(0,24*60,25))
    plt.xlabel(u'日期')
    plt.ylabel(u'时刻')
    plt.legend(loc=6)
    plt.title(u'日出日落时刻和白天时长图')
    plt.grid(True)
    ax2 = ax1.twinx()
    plt.plot(df_recent_year['date'], df_recent_year['richang'], 'r', lw=1.5, label=u'日长')
    ax = plt.gca()
    # ax.yaxis.set_major_formatter(FuncFormatter(min_formatter)) # 主刻度文本用pi_formatter函数计算
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x,pos: "%02d:%02d" %(int(x/60), int(x%60))))  # 主刻度文本用pi_formatter函数计算
    # ax.set_xticklabels(rotation=45, horizontalalignment='right')
    plt.ylim((3*60, 12 * 60))
    plt.yticks(np.linspace(3*60, 15 * 60, 13))
    plt.ylabel(u'时分')
    plt.legend(loc=5)
    plt.grid(True)

    # plt.show()
    img_sunonoff_path = 'img\\weather\\sunonoff.png'
    plt.savefig(img_sunonoff_path)
    imglist.append(img_sunonoff_path)
    plt.close()

    imglist2note(note_store, imglist, destguid, '武汉天气图', token)

