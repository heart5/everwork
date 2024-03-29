# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     formats: ipynb,py:percent
#     notebook_metadata_filter: jupytext,-kernelspec,-jupytext.text_representation.jupytext_version
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
# ---

# %% [markdown]
# # 处理每日天气信息，生成图表呈现

# %%
"""
处理每日天气信息，生成图表呈现

笔记本《行政管理》：31eee750-e240-438b-a1f5-03ce34c904b4
e5d81ffa-89e7-49ff-bd4c-a5a71ae14320 武汉雨天记录
277dff5e-7042-47c0-9d7b-aae270f903b8 武汉每日天气
输出笔记：
296f57a3-c660-4dd5-885a-56492deb2cee 武汉天气图
"""

# %% [markdown]
# ## 引入库

# %%
import re
import time
import pygsheets
import datetime
import pandas as pd
import numpy as np
from threading import Timer
from bs4 import BeautifulSoup
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
from pylab import plt, FuncFormatter

# %%
import pathmagic
with pathmagic.context():
    from func.configpr import getcfpoptionvalue, setcfpoptionvalue
    from func.evernttest import get_notestore, imglist2note
    from func.first import dirmainpath, touchfilepath2depth
    from func.logme import log
    from func.mailsfunc import getmail
    from func.wrapfuncs import timethis  # , ift2phone
#     from func.profilerlm import lpt_wrapper
    from func.datatools import readfromtxt, write2txt
    from func.filedatafunc import gettopicfilefromgoogledrive
    from func.sysfunc import not_IPython


# %% [markdown]
# ## 核心功能函数集合

# %% [markdown]
# ### getweatherfromevernote()

# %%
def getweatherfromevernote():
    noteguid_weather = '277dff5e-7042-47c0-9d7b-aae270f903b8'
    note_store = get_notestore()
    soup = BeautifulSoup(note_store.getNoteContent(
        noteguid_weather), "html.parser")
    # evernoteapijiayi()
    # tags = soup.find('en-note')
    # print tags
    # print soup.get_text()

    pattern = u'(\w*\s*\d+,\s*\d{4}\s*at\s*\d{2}:\d{2}[AP]M)\s+'
    weatherslice = re.split(pattern, soup.get_text())
    # print len(slice)
    split_item = []
    for i in range(1, len(weatherslice), 2):
        split_item.append(weatherslice[i] + " " + weatherslice[i + 1])

    print(split_item)
    return split_item


# %% [markdown]
# ### getweatherfromgmail()

# %%
def getweatherfromgmail():
    host = getcfpoptionvalue('everwork', 'gmail', 'host')
    username = getcfpoptionvalue('everwork', 'gmail', 'username')
    password = getcfpoptionvalue('everwork', 'gmail', 'password')
    mailitems = getmail(host, username, password,
                        dirtarget='Ifttt/Weather', unseen=True, topic='武汉每日天气 @行政管理 +')
    if mailitems is False:
        return False
    split_items = []
    for header, body in mailitems:
        for mistext, mistextstr in body:
            split_items.append(mistextstr)
    log.info('从Gmail邮箱获取%d条天气信息记录' % len(split_items))
    # write2weathertxt("data\\ifttt\\weather.txt",split_item)

    return split_items


# %% [markdown]
# ### getweatherfromgoogledrive()

# %%
def getweatherfromgoogledrive():
    dfboottrails = gettopicfilefromgoogledrive('Today\'s weather report', 'A:H')
    dfboottrails.columns = ['date', 'gaowen', 'diwen', 'fengsu', 'fengxiang', 'sunon', 'sunoff', 'shidu']
    dfboottrails['date'] = dfboottrails['date'].apply(lambda x: pd.Timestamp(x))
    dfboottrails['date'] = dfboottrails['date'].apply(lambda x: "%04d-%02d-%02d" % (x.year, x.month, x.day))
    dfboottrails['date'] = dfboottrails['date'].apply(lambda x: pd.to_datetime(x))
    dfboottrails['sunon'] = dfboottrails['sunon'].apply(lambda x: pd.Timestamp(x))
    dfboottrails['sunon'] = dfboottrails['sunon'].apply(lambda x: x.hour*60+x.minute)
    dfboottrails['sunoff'] = dfboottrails['sunoff'].apply(lambda x: pd.Timestamp(x))
    dfboottrails['sunoff'] = dfboottrails['sunoff'].apply(lambda x: x.hour*60+x.minute)
    dfout = dfboottrails
    print(dfout.tail())
    return dfout


# %% [markdown]
# ### weatherstat(df, destguid=None)

# %%
def weatherstat(df, destguid=None):
    dfduplicates = df.groupby('date').apply(lambda d: tuple(d.index) if len(d.index) > 1 else None).dropna()
    log.info(dfduplicates)
    df.drop_duplicates(inplace=True)  # 去重，去除可能重复的天气数据记录，原因可能是邮件重复发送等
    # print(df.head(30))
    df['date'] = df['date'].apply(lambda x : pd.to_datetime(x))
    # 日期做索引，去重并重新排序
    df.index = df['date']
    df = df[~df.index.duplicated()]
    df.sort_index(inplace=True)
    # print(df)
    df.dropna(how='all', inplace=True)  # 去掉空行，索引日期，后面索引值相同的行会被置空，需要去除
    # print(len(df))
    # df['gaowen'] = df['gaowen'].apply(lambda x: np.nan if str(x).isspace() else int(x))   #处理空字符串为空值的另外一骚
    df['gaowen'] = df['gaowen'].apply(lambda x: int(
        x) if x else None)  # 数字串转换成整数，如果空字符串则为空值
    df['diwen'] = df['diwen'].apply(lambda x: int(x) if x else None)
    df['fengsu'] = df['fengsu'].apply(lambda x: int(x) if x else None)
    df['shidu'] = df['shidu'].apply(lambda x: int(x) if x else None)
    # df['gaowen'] = df['gaowen'].astype(int)
    # df['diwen'] = df['diwen'].astype(int)
    # df['fengsu'] = df['fengsu'].astype(int)
    # df['shidu'] = df['shidu'].astype(int)
    df.fillna(method='ffill', inplace=True)  # 向下填充处理可能出现的空值，bfill是向上填充
    df['wendu'] = (df['gaowen'] + df['diwen']) / 2
    df['richang'] = df['sunoff'] - df['sunon']
    df['richang'] = df['richang'].astype(int)
    df['wendu'] = df['wendu'].astype(int)

    # print(df.tail(30))

    df_recent_year = df.iloc[-365:]
    # print(df_recent_year)
    # print(df[df.gaowen == df.iloc[-364:]['gaowen'].max()])
    # df_before_year = df.iloc[:-364]

    plt.figure(figsize=(16, 20))
    ax1 = plt.subplot2grid((4, 2), (0, 0), colspan=2, rowspan=2)
    ax1.plot(df['gaowen'], lw=0.3, label=u'日高温')
    ax1.plot(df['diwen'], lw=0.3, label=u'日低温')
    ax1.plot(df['wendu'], 'g', lw=0.7, label=u'日温度（高温低温平均）')
    quyangtianshu = 10
    ax1.plot(df['wendu'].resample('%dD' % quyangtianshu).mean(),
             'b', lw=1.2, label='日温度（每%d天平均）' % quyangtianshu)
    ax1.plot(df[df.fengsu > 5]['fengsu'], '*', label='风速（大于五级）')
    plt.legend(loc=2)
    #  起始统计日
    kedu = df.iloc[0]
    ax1.plot([kedu['date'], kedu['date']], [0, kedu['wendu']], 'c--', lw=0.4)
    ax1.scatter([kedu['date'], ], [kedu['wendu']], 50, color='Wheat')
    fsize = 8
    txt = str(kedu['wendu'])
    ax1.annotate(txt, xy=(kedu['date'], kedu['wendu']), xycoords='data', xytext=(-(len(txt) * fsize), +20),
                 textcoords='offset points', fontsize=fsize,
                 arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2", color='Purple'))

    dates = "%02d-%02d" % (kedu['date'].month, kedu['date'].day)
    ax1.annotate(dates, xy=(kedu['date'], 0), xycoords='data',
                 xytext=(-10, -20), textcoords='offset points', fontsize=8,
                 arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"))
    # 去年今日，如果数据不足一年，取今日
    if len(df) >= 366:
        locqnjr = -365
    else:
        locqnjr = -1
    kedu = df.iloc[locqnjr]
    # kedu = df.iloc[-364]
    print(kedu)
    ax1.plot([kedu['date'], kedu['date']], [0, kedu['wendu']], 'c--')
    ax1.scatter([kedu['date'], ], [kedu['wendu']], 50, color='Wheat')
    ax1.annotate(str(kedu['wendu']), xy=(kedu['date'], kedu['wendu']), xycoords='data',
                 xytext=(-5, +20), textcoords='offset points',
                 arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2", color='Purple'))
    dates = "%02d-%02d" % (kedu['date'].month, kedu['date'].day)
    ax1.annotate(dates, xy=(kedu['date'], 0), xycoords='data',
                 xytext=(-10, -35), textcoords='offset points', fontsize=8,
                 arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"))
    # 今日
    kedu = df.iloc[-1]
    # print(kedu)
    ax1.plot([kedu['date'], kedu['date']], [0, kedu['wendu']], 'c--')
    ax1.scatter([kedu['date'], ], [kedu['gaowen']], 50, color='BlueViolet')
    ax1.annotate(str(kedu['gaowen']), xy=(kedu['date'], kedu['gaowen']), xycoords='data',
                 xytext=(-10, +20), textcoords='offset points',
                 arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2", color='Purple'))
    ax1.scatter([kedu['date'], ], [kedu['wendu']], 50, color='BlueViolet')
    ax1.annotate(str(kedu['wendu']), xy=(kedu['date'], kedu['wendu']), xycoords='data',
                 xytext=(10, +5), textcoords='offset points',
                 arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2", color='Purple'))
    ax1.scatter([kedu['date'], ], [kedu['diwen']], 50, color='BlueViolet')
    ax1.annotate(str(kedu['diwen']), xy=(kedu['date'], kedu['diwen']), xycoords='data',
                 xytext=(-10, -20), textcoords='offset points',
                 arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2", color='Purple'))
    dates = "%02d-%02d" % (kedu['date'].month, kedu['date'].day)
    ax1.annotate(dates, xy=(kedu['date'], 0), xycoords='data',
                 xytext=(-10, -35), textcoords='offset points', fontsize=8,
                 arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"))

    # 最近一年最高温
    kedu = df_recent_year[df_recent_year.gaowen ==
                          df_recent_year.iloc[-364:]['gaowen'].max()].iloc[0]
    # print(kedu)
    ax1.plot([kedu['date'], kedu['date']], [0, kedu['gaowen']], 'c--')
    ax1.scatter([kedu['date'], ], [kedu['gaowen']], 50, color='Wheat')
    ax1.annotate(str(kedu['gaowen']), xy=(kedu['date'], kedu['gaowen']), xycoords='data',
                 xytext=(-20, +5), textcoords='offset points',
                 arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2", color='Purple'))
    dates = "%02d-%02d" % (kedu['date'].month, kedu['date'].day)
    ax1.annotate(dates, xy=(kedu['date'], 0), xycoords='data',
                 xytext=(-10, -20), textcoords='offset points', fontsize=8,
                 arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"))
    # 最近一年最低温
    kedu = df_recent_year[df_recent_year.diwen ==
                          df_recent_year.iloc[-364:]['diwen'].min()].iloc[0]
    ax1.plot([kedu['date'], kedu['date']], [0, kedu['diwen']], 'c--')
    ax1.scatter([kedu['date'], ], [kedu['diwen']], 50, color='Wheat')
    ax1.annotate(str(kedu['diwen']), xy=(kedu['date'], kedu['diwen']), xycoords='data',
                 xytext=(-20, +5), textcoords='offset points',
                 arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2", color='Purple'))
    dates = "%02d-%02d" % (kedu['date'].month, kedu['date'].day)
    ax1.annotate(dates, xy=(kedu['date'], 0), xycoords='data',
                 xytext=(-10, -20), textcoords='offset points', fontsize=8,
                 arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"))
    # 最高温
    kedu = df[df.gaowen == df['gaowen'].max()].iloc[0]
    ax1.plot([kedu['date'], kedu['date']], [0, kedu['gaowen']], 'c--')
    ax1.scatter([kedu['date'], ], [kedu['gaowen']], 50, color='Wheat')
    ax1.annotate(str(kedu['gaowen']), xy=(kedu['date'], kedu['gaowen']), xycoords='data',
                 xytext=(-20, +5), textcoords='offset points',
                 arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2", color='Purple'))
    dates = "%02d-%02d" % (kedu['date'].month, kedu['date'].day)
    ax1.annotate(dates, xy=(kedu['date'], 0), xycoords='data',
                 xytext=(-10, -20), textcoords='offset points', fontsize=8,
                 arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"))
    # 最低温
    kedu = df[df.diwen == df['diwen'].min()].iloc[0]
    ax1.plot([kedu['date'], kedu['date']], [0, kedu['diwen']], 'c--')
    ax1.scatter([kedu['date'], ], [kedu['diwen']], 50, color='Wheat')
    ax1.annotate(str(kedu['diwen']), xy=(kedu['date'], kedu['diwen']), xycoords='data',
                 xytext=(-20, +5), textcoords='offset points',
                 arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2", color='Purple'))
    dates = "%02d-%02d" % (kedu['date'].month, kedu['date'].day)
    ax1.annotate(dates, xy=(kedu['date'], 0), xycoords='data',
                 xytext=(-10, -20), textcoords='offset points', fontsize=8,
                 arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"))
    ax1.set_ylabel(u'（摄氏度℃）')
    ax1.grid(True)
    ax1.set_title(u'最高气温、最低气温和均值温度图')

    ax3 = plt.subplot2grid((4, 2), (2, 0), colspan=2, rowspan=2)
    # print(type(ax3))
    ax3.plot(df_recent_year['shidu'], 'c.', lw=0.3, label=u'湿度')
    ax3.plot(df_recent_year['shidu'].resample('15D').mean(), 'g', lw=1.5)
    ax3.set_ylabel(u'（百分比%）')
    ax3.set_title(u'半月平均湿度图')

    img_wenshifeng_path = dirmainpath / "img" / 'weather' / 'wenshifeng.png'
    img_wenshifeng_path_str = str(img_wenshifeng_path)
    touchfilepath2depth(img_wenshifeng_path)
    plt.legend(loc='lower left')
    plt.tight_layout() # 紧缩排版，缩小默认的边距
    plt.savefig(img_wenshifeng_path_str)

    imglist = list()
    imglist.append(img_wenshifeng_path_str)
    plt.close()

    plt.figure(figsize=(16, 10))
    fig, ax1 = plt.subplots()
    plt.plot(df['date'], df['sunon'], lw=0.8, label=u'日出')
    plt.plot(df['date'], df['sunoff'], lw=0.8, label=u'日落')
    ax = plt.gca()
    # ax.yaxis.set_major_formatter(FuncFormatter(min_formatter)) # 主刻度文本用pi_formatter函数计算
    ax.yaxis.set_major_formatter(
        FuncFormatter(lambda x, pos: "%02d:%02d" % (int(x / 60), int(x % 60))))  # 主刻度文本用pi_formatter函数计算
    plt.ylim((0, 24 * 60))
    plt.yticks(np.linspace(0, 24 * 60, 25))
    plt.xlabel(u'日期')
    plt.ylabel(u'时刻')
    plt.legend(loc=6)
    plt.title(u'日出日落时刻和白天时长图')
    plt.grid(True)
    ax2 = ax1.twinx()
    print(ax2)
    plt.plot(df_recent_year['date'],
             df_recent_year['richang'], 'r', lw=1.5, label=u'日长')
    ax = plt.gca()
    # ax.yaxis.set_major_formatter(FuncFormatter(min_formatter)) # 主刻度文本用pi_formatter函数计算
    ax.yaxis.set_major_formatter(
        FuncFormatter(lambda x, pos: "%02d:%02d" % (int(x / 60), int(x % 60))))  # 主刻度文本用pi_formatter函数计算
    # ax.set_xticklabels(rotation=45, horizontalalignment='right')
    plt.ylim((3 * 60, 12 * 60))
    plt.yticks(np.linspace(3 * 60, 15 * 60, 13))
    plt.ylabel(u'时分')
    plt.legend(loc=5)
    plt.grid(True)

    # plt.show()
    img_sunonoff_path = dirmainpath / 'img' / 'weather' / 'sunonoff.png'
    img_sunonoff_path_str = str(img_sunonoff_path)
    touchfilepath2depth(img_sunonoff_path)
    plt.tight_layout() # 紧缩排版，缩小默认的边距
    plt.savefig(img_sunonoff_path_str)
    imglist.append(img_sunonoff_path_str)
    plt.close()

    imglist2note(get_notestore(), imglist, destguid, '武汉天气图')


# %% [markdown]
# ### getnewestdataday(item)

# %%
def getnewestdataday(item):
    weatherlastestday = getcfpoptionvalue('everlife', '天气', f"{item}最新日期")
    if not weatherlastestday:
        weatherlastestday = '2016-09-19'
        setcfpoptionvalue('everlife', '天气', f'{item}最新日期', '%s' % weatherlastestday)

    return weatherlastestday


# %% [markdown]
# ### fetchweatherinfo_from_gmail(weathertxtfilename)

# %%
def fetchweatherinfo_from_gmail(weathertxtfilename):
    weatherdatalastestday = getnewestdataday('存储数据')
    today = datetime.datetime.now().strftime('%F')
    hour = int(datetime.datetime.now().strftime('%H'))
    if (today > weatherdatalastestday) and (hour > 6):
        items = getweatherfromgmail()
        if items:
            log.info('通过邮件轮询，读取天气信息%d条。' % len(items))
            itemfromtxt = readfromtxt(weathertxtfilename)
            for itemg in itemfromtxt:
                items.append(str(itemg))
            write2txt(weathertxtfilename, items)
            weathertxtlastestday = time.strftime('%F', time.strptime(
                items[0].split(' ：')[0], '%B %d, %Y at %I:%M%p'))
            setcfpoptionvalue('everlife', '天气', '存储数据最新日期', '%s' % weathertxtlastestday)


# %% [markdown]
# ### isweatherupdate(weathertxtfilename)

# %%
def isweatherupdate(weathertxtfilename):
    # print(weathertoday, end='\t')
    # print(datetime.datetime.now().strftime('%F'))
    weathertoday = time.strftime('%F',
                                 time.strptime(readfromweathertxt(weathertxtfilename)[0].split(' ：')[0],
                                               '%B %d, %Y at %I:%M%p'))
    if datetime.datetime.now().strftime('%F') == weathertoday:
        log.info('今天的天气信息已取回，跳过邮件轮询。')
    else:
        items = getweatherfromgmail()
        if items:
            log.info('通过邮件轮询，读取天气信息%d条。' % len(items))
            itemfromtxt = readfromtxt(weathertxtfilename)
            for itemg in itemfromtxt:
                items.append(str(itemg))
            write2txt(weathertxtfilename, items)

    items = readfromtxt(weathertxtfilename)
    print(len(items))
    if not (dycountini := getcfpoptionvalue('everlife', '天气', '统计天数')):
        dycountini = 0

    if len(items) > dycountini:
        return items
    else:
        return False


# %% [markdown]
# ### items2df(items)

# %%
def items2df(items):
    split_item = items
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
        stritem = list()
        for jj in re.findall(itempattern, ii):
            stritem = [pd.Timestamp(jj[0]),
                       jj[1], jj[2], jj[3], jj[4],
                       # pd.Timestamp(jj[5]).strftime("%I%M"),
                       int(pd.Timestamp(jj[5]).strftime("%H")) * \
                       60 + int(pd.Timestamp(jj[5]).strftime("%M")),
                       # pd.Timestamp(jj[6]),
                       int(pd.Timestamp(jj[6]).strftime("%H")) * \
                       60 + int(pd.Timestamp(jj[6]).strftime("%M")),
                       jj[7]]
            datei = stritem[0]
            dates = "%04d-%02d-%02d" % (datei.year, datei.month, datei.day)
            # print(str(datei)+'\t'+dates)
            stritem[0] = pd.to_datetime(dates)
            # stritem[0] = dates
        # print stritem
        data_list.append(stritem)

    print(f'{len(data_list)}\t{data_list[0]}\t{data_list[-1]}')

    df = pd.DataFrame(data_list,
                      columns=['date', 'gaowen', 'diwen', 'fengsu', 'fengxiang', 'sunon', 'sunoff', 'shidu'])
    # print(df)
    # print(len(df))

    return df


# %% [markdown]
# ### fetchweatherinfo_from_googledrive()

# %%
def fetchweatherinfo_from_googledrive():
    weatherdatalastestday = getnewestdataday('存储数据')
    today = datetime.datetime.now().strftime('%F')
    hour = int(datetime.datetime.now().strftime('%H'))
    if (today > weatherdatalastestday):  # or True:
        df = getweatherfromgoogledrive()
        if df is not None:
            log.info('通过读Google drive表格，获取天气信息%d条。' % df.shape[0])
            print(df['date'].max())
            weathertxtlastestday = df['date'].max().strftime('%F')
            setcfpoptionvalue('everlife', '天气', '存储数据最新日期', '%s' % weathertxtlastestday)

            return df


# %% [markdown]
# ### getrainfromgoogledrive()

# %%
@timethis
# @lpt_wrapper()
def getrainfromgoogledrive():
    dfrainraw = gettopicfilefromgoogledrive('Rain in Wuhan', 'A:E')
    dfrainraw.columns = ['raintime', 'tianxiang', 'huashi', 'sheshi', 'links']
    dfrainraw['raintime'] = dfrainraw['raintime'].apply(lambda x:pd.to_datetime(x))
    dfrainraw['date'] = dfrainraw['raintime'].apply(lambda x: pd.to_datetime(f"{x.year}-{x.month}-{x.day}"))
    dfrainraw['mingmu'] = '下雨'

    # 处理数据错行
    dfrainokay = dfrainraw[~dfrainraw.tianxiang.str.isnumeric()]
    dfrainchuli = dfrainraw[dfrainraw.tianxiang.str.isnumeric()]
    dfrainchuli.columns = ['raintime', 'huashi', 'sheshi', 'tianxiang', 'links', 'date', 'mingmu']
    dfrainraw = dfrainokay.append(dfrainchuli).sort_index()

    # 温度数值化
    dfrainraw['huashi'] = dfrainraw['huashi'].apply(lambda x: re.findall(r'\d+', x)[0])
    dfrainraw['sheshi'] = dfrainraw['sheshi'].apply(lambda x: re.findall(r'\d+', x)[0])

    dfrain = dfrainraw.drop_duplicates(['raintime'])
    dfrainduplicates = dfrain.groupby('date').apply(lambda d: tuple(d.raintime) if len(d.index) > 1 else None).dropna()
    print(dfrainduplicates)
    # dfout = dfgaowen.drop_duplicates(['date'], keep='first')
    dfout = dfrain.loc[:, ['date', 'raintime', 'mingmu']]

    return dfout, dfrain


# %% [markdown]
# ### getgaowenfromgoogledrive()

# %%
@timethis
def getgaowenfromgoogledrive():
    dfgaowenraw = gettopicfilefromgoogledrive('武汉高温纪录', 'A:D')
    dfgaowenraw.columns = ['hottime', 'huashi', 'sheshi', 'tianxiang']
    dfgaowenraw['hottime'] = dfgaowenraw['hottime'].apply(lambda x:pd.to_datetime(x))
    dfgaowenraw['date'] = dfgaowenraw['hottime'].apply(lambda x: pd.to_datetime(f"{x.year}-{x.month}-{x.day}"))
    dfgaowenraw['mingmu'] = '高温'
    dfgaowen = dfgaowenraw.drop_duplicates(['hottime'])
    dfgaowenduplicates = dfgaowen.groupby('date').apply(lambda d: tuple(d.hottime) if len(d.index) > 1 else None).dropna()
    print(dfgaowenduplicates)
    # dfout = dfgaowen.drop_duplicates(['date'], keep='first')
    dfout = dfgaowen.loc[:, ['date', 'hottime', 'mingmu']]

    return dfout, dfgaowen


# %% [markdown]
# ### weatherstatdo()

# %%
@timethis
# @ift2phone()
def weatherstatdo():
    weathertxtfilename = str(dirmainpath / 'data' / 'ifttt' / 'weather.txt')
    print(weathertxtfilename)
    dfgoogledrive = None
    try:
        # fetchweatherinfo_from_gmail(weathertxtfilename)
        dfgoogledrive = fetchweatherinfo_from_googledrive()
    except Exception as weathererror:
        log.critical(f'从邮箱或谷歌硬盘获取天气信息时出现错误。{weathererror}')
        raise

    weathernotelastestday = getnewestdataday('笔记')
    today = datetime.datetime.now().strftime('%F')
    weathertxtlastestday = getnewestdataday('存储数据')
    if today == weathernotelastestday:  # and False:
        print('今天的天气信息统计笔记已刷新，本次轮询跳过')
    elif today == weathertxtlastestday:  # or True:
        try:
            items = readfromtxt(weathertxtfilename)
            dftxt = items2df(items)
            # print(dftxt.dtypes)
            dfall = dftxt.append(dfgoogledrive, True)
            # print(dfall)
            # print(dfgoogledrive.dtypes)
            datenew = dfall['date'].max()
            weatherstat(dfall, '296f57a3-c660-4dd5-885a-56492deb2cee')
            log.info(f'天气信息({datenew})成功更新入天气信息统计笔记')
            setcfpoptionvalue('everlife', '天气', '统计天数', f"{len(items)}")
            setcfpoptionvalue('everlife', '天气', '笔记最新日期', today)
        except IndexError as ixe:
            log.critical('读取天气信息并更新天气统计信息笔记时出现索引错误。%s' % (str(ixe)))
        except TypeError as te:
            log.critical('读取天气信息并更新天气统计信息笔记时出现类型错误。%s' % (str(te)))
            raise
        except Exception as eeee:
            log.critical('读取天气信息笔记并更新天气统计信息笔记时出现未名错误。%s' % (str(eeee)))
    else:
        log.info('时间的花儿静悄悄！')


# %% [markdown]
# ## 主函数main()

# %%
if __name__ == '__main__':
    if not_IPython():
        log.info(f'运行文件\t{__file__}……')
    weatherstatdo()
    # df, dfall = getrainfromgoogledrive()
    # print(df)
    # print(dfall)
    # df = getgaowenfromgoogledrive()
    # print(df)
    # getweatherfromgoogledrive()
    # weathertxtfilename = "data\\ifttt\\weather.txt"
    # usn = isweatherupdate(weathertxtfilename)
    # # print(getweatherfromgmail())
    if not_IPython():
        log.info(f'文件\t{__file__}执行结束。Done！')
