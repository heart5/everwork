#
# encoding:utf-8
#
# 处理每日天气信息，生成图表呈现
#
# 源信息笔记标题：武汉每日天气，笔记guid：277dff5e-7042-47c0-9d7b-aae270f903b8；所在笔记本《行政管理》，
# 该笔记本guid：31eee750-e240-438b-a1f5-03ce34c904b4
# 输出信息笔记标题：武汉天气图，笔记guid：296f57a3-c660-4dd5-885a-56492deb2cee；所在笔记本《行政管理》，
# 该笔记本guid：31eee750-e240-438b-a1f5-03ce34c904b4

import re, pandas as pd, numpy as np, matplotlib.pyplot as plt, evernote.edam.type.ttypes as Types, time, hashlib, binascii
from bs4 import BeautifulSoup

from matplotlib.ticker import MultipleLocator, FuncFormatter


#
# 把分钟数转换成分时的显示方式，用于纵轴标签
#
def min_formatter(x, pos):
    return r"%02d:%02d" %(int(x/60), int(x%60)) #%02d，用两位数显示数字，不足位数则前导0填充


def weatherstat(note_store, sourceguid, destguid=None):
    soup = BeautifulSoup(note_store.getNoteContent(sourceguid), "html.parser")
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
        # print stritem
        data_list.append(stritem)

    print (len(data_list))
    print (data_list[-1])


    df = pd.DataFrame(data_list,
                      columns=['date', 'gaowen', 'diwen', 'fengsu', 'fengxiang', 'sunon', 'sunoff', 'shidu'])
    df['richang'] = df['sunoff'] - df['sunon']
    df['richang'] = df['richang'].astype(int)
    df['wendu'] = (df['gaowen'] + df['diwen'])/2
    df['wendu'] = df['wendu'].astype(int)
    df['fengsu'] = df['fengsu'].astype(int)

    # print(df.head())

    # x = list(df['date'])
    # y = list(df['gaowen'])
    # plt.plot(x,y)
    # plt.show()

    # tss = pd.Series(list(df['gaowen']),index=pd.date_range('9/19/2016', periods=354))
    # tss = pd.Series(list(df[0:100]['gaowen']),index=df[0:100]['date'])
    # tss.cumsum()
    # tss.plot()

    # tss = pd.Series(list(df['gaowen']), index=df['date'])
    # tss.cumsum()
    # tss.plot()

    df1 = df.iloc[-365:]
    plt.figure(figsize=(10, 16))
    ax1 = plt.subplot2grid((7,2),(0,0),colspan=2,rowspan = 3)
    ax1.plot(df['date'], df['gaowen'], lw=0.3, label=u'日高温')
    ax1.plot(df['date'], df['diwen'], lw=0.3, label=u'日低温')
    ax1.plot(df1['date'], df1['wendu'], 'g', lw=1.5, label=u'温度')
    ax1.set_ylabel(u'（摄氏度℃）')
    ax1.grid(True)
    ax1.set_title(u'最高气温、最低气温和均值温度图')


    ax2 = plt.subplot2grid((7, 2), (4, 1), colspan=1, rowspan=3)
    ax2.plot(df1['date'], df1['fengsu'], 'c*', lw=1.5, label=u'风速')
    ax2.set_title(u'风速图')

    ax3 = plt.subplot2grid((7, 2), (4, 0), colspan=1, rowspan=3)
    ax3.plot(df1['date'], df1['shidu'], 'g*', lw=1.5, label=u'湿度')
    ax3.set_ylabel(u'（百分比%）')
    ax3.set_title(u'湿度图')

    # tssr = tss.resample('M').max()
    # tssr = tss.asfreq('10D', method='pad')
    # tssr.cumsum()
    # tssr.plot()
    # plt.show()

    img_wenshifeng_path = "img\\weather\\wenshifeng.png"
    plt.savefig(img_wenshifeng_path)
    plt.close()


    plt.figure(figsize=(10,10))
    fig,ax1 = plt.subplots()
    plt.plot(df['date'], df['sunon'], lw=0.8, label=u'日出')
    plt.plot(df['date'], df['sunoff'], lw=0.8, label=u'日落')
    ax = plt.gca()
    ax.yaxis.set_major_formatter(FuncFormatter(min_formatter)) # 主刻度文本用pi_formatter函数计算
    plt.ylim((0,24*60))
    plt.yticks(np.linspace(0,24*60,25))
    plt.xlabel(u'日期')
    plt.ylabel(u'时刻')
    plt.legend(loc=6)
    plt.title(u'日出日落时刻和白天时长图')
    plt.grid(True)
    ax2 = ax1.twinx()
    plt.plot(df1['date'], df1['richang'], 'r', lw=1.5, label=u'日长')
    ax = plt.gca()
    ax.yaxis.set_major_formatter(FuncFormatter(min_formatter)) # 主刻度文本用pi_formatter函数计算
    # ax.set_xticklabels(rotation=45, horizontalalignment='right')
    # plt.ylim((0, 15 * 60))
    # plt.yticks(np.linspace(0, 15 * 60, 16))
    plt.ylabel(u'时分')
    plt.legend(loc=5)
    plt.grid(True)

    # plt.show()
    img_sunonoff_path = 'img\\weather\\sunonoff.png'
    plt.savefig(img_sunonoff_path)
    plt.close()


    #
    # 要更新一个note，生成一个Note（），指定guid，更新其content
    #
    note = Types.Note()
    note.title = "武汉天气图"
    note.guid = destguid
    # note.notebookGuid = '31eee750-e240-438b-a1f5-03ce34c904b4'

    # To include an attachment such as an image in a note, first create a Resource
    # for the attachment. At a minimum, the Resource contains the binary attachment
    # data, an MD5 hash of the binary data, and the attachment MIME type.
    # It can also include attributes such as filename and location.
    image = open(img_wenshifeng_path, 'rb').read()
    md5 = hashlib.md5()
    md5.update(image)
    hash = md5.digest()
    data = Types.Data()
    data.size = len(image)
    data.bodyHash = hash
    data.body = image
    resource_wenshifeng = Types.Resource()
    resource_wenshifeng.mime = 'image/png'
    resource_wenshifeng.data = data
    # print resource_wenshifeng

    image = open(img_sunonoff_path, 'rb').read()
    md5 = hashlib.md5()
    md5.update(image)
    hash = md5.digest()
    data = Types.Data() #必须要重新构建一个Data（），否则内容不会变化
    data.size = len(image)
    data.bodyHash = hash
    data.body = image
    resource_sunonoff = Types.Resource()
    resource_sunonoff.mime = 'image/png'
    resource_sunonoff.data = data

    # print resource_sunonoff
    # Now, add the new Resource to the note's list of resources
    note.resources = []
    note.resources.append(resource_wenshifeng)
    note.resources.append(resource_sunonoff)

    # print len(note.resources)
    # # print note.resources
    # print note.resources[0]
    # print note.resources[1]


    # The content of an Evernote note is represented using Evernote Markup Language
    # (ENML). The full ENML specification can be found in the Evernote API Overview
    # at http://dev.evernote.com/documentation/cloud/chapters/ENML.php
    nBody = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
    nBody += "<!DOCTYPE en-note SYSTEM \"http://xml.evernote.com/pub/enml2.dtd\">"
    nBody += "<en-note>"
    if note.resources:
        # To display the Resource as part of the note's content, include an <en-media>
        # tag in the note's ENML content. The en-media tag identifies the corresponding
        # Resource using the MD5 hash.
        # nBody += "<br />" * 2
        for resource in note.resources:
            hexhash = binascii.hexlify(resource.data.bodyHash)
            str1 = "%s" %hexhash #b'cd34b4b6c8d9279217b03c396ca913df'
            # print (str1)
            str1 = str1[2:-1] #cd34b4b6c8d9279217b03c396ca913df
            # print (str1)
            nBody += "<en-media type=\"%s\" hash=\"%s\" /><br />"  %(resource.mime, str1)
    nBody += "</en-note>"

    note.content = nBody
    # print (note.content)

    # Finally, send the new note to Evernote using the updateNote method
    # The new Note object that is returned will contain server-generated
    # attributes such as the new note's unique GUID.
    updated_note = note_store.updateNote(note)
    # print(updated_note)
    print ("Successfully updated a note with GUID: ", updated_note.guid, updated_note.title)