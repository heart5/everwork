# encoding:utf-8
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
#
# 处理每日天气信息，生成图表呈现
#
# 源信息笔记标题：武汉每日天气，笔记guid：277dff5e-7042-47c0-9d7b-aae270f903b8；所在笔记本《行政管理》，
# 该笔记本guid：31eee750-e240-438b-a1f5-03ce34c904b4
# 输出信息笔记标题：武汉天气图，笔记guid：296f57a3-c660-4dd5-885a-56492deb2cee；所在笔记本《行政管理》，
# 该笔记本guid：31eee750-e240-438b-a1f5-03ce34c904b4

# %%
import pandas as pd
from matplotlib.pyplot import subplot2grid, figure, bar, gca, plot, legend, savefig, title, close
from matplotlib.ticker import FuncFormatter

# %%
import pathmagic

# %%
with pathmagic.context():
    from func.first import dirmainpath
    from func.pdtools import chuturizhexian
    from func.evernt import imglist2note


# %%
def pickstat(note_store, cnx, destguid=None, notetitle='', cum=False):
    # cnx = lite.connect('data\\quandan.db')
    # df = pd.read_sql('select * from fileread',cnx)
    # sql = "update quandan set 无货金额 = NULL where 无货金额 like '%s'" %('.') #把无货金额字段中非法字符做妥善处理
    # print(sql)
    # result = cnx.cursor().execute(sql)
    # print(result)
    # cnx.commit()
    # sql = "select * from quandan where 无货金额 like '%s'" %('.')
    # print(sql)
    df = pd.DataFrame()
    try:
        df = pd.read_sql("select * from quandan", cnx)
        df = df[df.配货人 != '作废']
        df['订单日期'] = pd.to_datetime(df['订单日期'])
        df = df[df['订单日期'] >= pd.to_datetime('2016-04-01')]
        df['送达日期'] = pd.to_datetime(df['送达日期'])
        df['收款日期'] = pd.to_datetime(df['收款日期'])

    except Exception as eee:
        print(f'{eee}')
    xlswriter = pd.ExcelWriter(str(dirmainpath / 'data' / 'ttt.xlsx'))

    print(df.columns)
    dd = pd.DataFrame(df.groupby(['订单日期']).size(), columns=['配单数量'])
    dd['错配单数'] = df.groupby(['订单日期']).sum()['配货准确']
    dd['配单金额'] = df.groupby(['订单日期']).sum()['送货金额']
    dd['无货金额'] = df.groupby(['订单日期']).sum()['无货金额']
    dd['漏配金额'] = df.groupby(['订单日期']).sum()['少配金额']
    dd['错配金额'] = df.groupby(['订单日期']).sum()['配错未要']
    # dd.insert(0,'日期',dd.index)
    # dd.insert(0,'年月',dd['日期'].apply(lambda x: "%04d%02d" % (x.year, x.month)))
    dd = dd.fillna(value=0)

    # ddfirstdate = dd.index.min()
    ddlastdate = dd.index.max()

    # old_width = pd.get_option('display.max_colwidth')
    # pd.set_option('display.max_colwidth', -1)
    # dd.to_html('data\\tmp\\files.html', classes=None, escape=False, index=None, sparsify=True,
    # border=0, index_names=None, justify='right', header=True)
    # pd.set_option('display.max_colwidth', old_width)

    # print(dd)
    dd.to_excel(xlswriter, '配货日汇总', freeze_panes=[1, 1])

    figure()
    ax1 = subplot2grid((5, 2), (0, 0), colspan=2, rowspan=2)
    ddm = dd.iloc[-400:, :].resample('M').sum()
    l1 = ax1.plot(ddm['配单数量'], lw=0.5, label='配单数量')
    legend()
    l2 = ax1.plot(ddm['错配单数'], lw=0.5, label='错配单数')
    legend()
    ax2 = ax1.twinx()
    plot(ddm['错配单数'] / ddm['配单数量'], 'r-', label='错单比例')
    legend()
    gca().yaxis.set_major_formatter(
        FuncFormatter(lambda x, pos: "%.1f%%" % (x*100)))  # 纵轴主刻度显示小数为百分数
    title('错配单数（月度）统计图')
    ax3 = subplot2grid((5, 2), (3, 0), colspan=2, rowspan=2)
    bar(ddm.index, ddm['漏配金额'], width=5, label='漏配金额')
    legend()
    bar(ddm.index, ddm['错配金额'], width=5, bottom=ddm['漏配金额'], label='错配金额')
    legend()
    title('错配金额（月度）统计图')
    savefig(str(dirmainpath / 'img' / 'pick' / 'pickstat.png'))
    close()

    imgpathlist = []
    pathimgpick = dirmainpath / 'img' / 'pick'
    imgpathlist += chuturizhexian(dd['配单数量'], ddlastdate, '配单数量', cum=cum, imgpath=pathimgpick)
    imgpathlist += chuturizhexian(dd['配单金额'], ddlastdate, '配单金额', cum=cum, imgpath=pathimgpick)
    imgpathlist.append(str(pathimgpick / "pickstat.png"))

    df['年月'] = df['订单日期'].apply(lambda x: "%04d-%02d" % (x.year, x.month))

    ph = pd.DataFrame(df.groupby(['配货人', '年月']).size())
    ph.columns = ['配单']
    ph['配错单数'] = df.groupby(['配货人', '年月']).sum()['配货准确']
    ph['配货金额'] = df.groupby(['配货人', '年月']).sum()['送货金额']
    ph['漏配金额'] = df.groupby(['配货人', '年月']).sum()['少配金额']
    ph['错配金额'] = df.groupby(['配货人', '年月']).sum()['配错未要']
    ph = ph.fillna(value=0)

    print(ph.index[[0]])

    # descdb(ph)
    # phh = ph[ph.index[[0]].isin(['黄传芝','黄国伟','姜明君']).values==True]
    phh = ph.unstack().T
    phh.to_excel(xlswriter, '配货人年月汇总', freeze_panes=[1, 2])
    # print(phh)

    xlswriter.save()

    imglist2note(note_store, imgpathlist, destguid, notetitle)
