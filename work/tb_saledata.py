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
# # 处理清洗销售数据 

# %% [markdown]
# ## 导入库 

# %%
import os
import pandas as pd
# from pathlib import Path
import xlsxwriter
import datetime
from pandas.tseries.offsets import MonthEnd

import pathmagic
with pathmagic.context():
    from func.first import getdirmain
    from func.sysfunc import not_IPython


# %% [markdown]
# ## 功能函数

# %% [markdown]
# ### def isclsatdf(cls, dfcls)

# %%
def isclsatdf(cls, dfcls):
    """
    查询cls中的元素是否全部被包含在dfcls中
    """
    isnotat = [cl for cl in cls if cl not in dfcls]
    if len(isnotat) > 0:
        # print(f"必须的列{isnotat}在该DataFrame中不存在，数据不符合规范")
        pass

    return len(isnotat) == 0


# %% [markdown]
# ### def managesourcesxlsx2cleandf(datapath)

# %%
def managesourcesxlsx2cleandf(datapath):
    """
    从数据目录读取xlsx文件，获取文件中的所有sheet，并判断列名是否符合规范
    然后按照原始销售数据重新处理生成标准、奖金等数据
    最后输出分组合计的标准df
    """
    fllst = [fl for fl in os.listdir(datapath) if fl.endswith("xlsx")]
    df = pd.DataFrame()
    clnmsneeded = ['开票日期', '客户简称', '业务员', '存货名称', '规格型号', '件数', '数量', '含税单价', '提货金额']
    for fl in fllst:
        datadict = pd.read_excel(datapath / fl, sheet_name=None)
        for k in datadict.keys():
            dftmp = datadict[k]
            dftmp.rename(columns={'业 务 员': '业务员', '价税合计': '提货金额'}, inplace=True)
            if not isclsatdf(clnmsneeded, dftmp.columns):
                # print(fl, dftmp.shape[0], k, "不合格的sheet", sep="\t")
                continue
            else:
                print(fl, dftmp.shape[0], k, "合格的sheet", sep="\t")
            df = df.append(dftmp, ignore_index=False)
#     print(df.shape[0])
#     print(df.dtypes)
    if (not isclsatdf(clnmsneeded, df.columns)) or (df.shape[0] == 0):
        return

    # 拷贝一份数据进行操作，避免链式赋值错误警告
    dftmp = df[clnmsneeded].copy()
    dftmp['计提标准'] = dftmp['含税单价'].apply(lambda x: 0.024 if x < 20 else 0.03)
    dftmp['业务奖金标准'] = dftmp['计提标准'] / 2
    dftmp['奖金金额'] = dftmp['计提标准'] * dftmp['提货金额']
    dftmp['业务应分配金额'] = dftmp['业务奖金标准'] * dftmp['提货金额']
    dftmp['奖金金额'] = dftmp['奖金金额'].map(lambda x: round(x, 2))
    dftmp['业务应分配金额'] = dftmp['业务应分配金额'].map(lambda x: round(x, 2))
    dftmpgr = dftmp.groupby(['开票日期', '客户简称', '业务员', '计提标准', '业务奖金标准']).sum()[['提货金额', '奖金金额', '业务应分配金额']]
    dfdone = dftmpgr.reset_index(['开票日期', '客户简称', '计提标准', '业务奖金标准', '业务员'])
    dfout = dfdone[['开票日期', '客户简称', '提货金额', '计提标准', '奖金金额', '业务奖金标准', '业务应分配金额', '业务员']]

    return dfout


# %%
def managesourcesxlsx2cleandf(datapath):
    """
    从数据目录读取xlsx文件，获取文件中的所有sheet，并判断列名是否符合规范
    然后按照原始销售数据重新处理生成标准、奖金等数据
    最后输出分组合计的标准df
    """
    fllst = [fl for fl in os.listdir(datapath) if fl.endswith("xlsx")]
    df = pd.DataFrame()
    clnmsneeded = ['开票日期', '客户简称', '业务员', '存货名称', '规格型号', '件数', '数量', '含税单价', '提货金额']
    for fl in fllst:
        datadict = pd.read_excel(datapath / fl, sheet_name=None)
        for k in datadict.keys():
            dftmp = datadict[k]
            dftmp.rename(columns={'业 务 员': '业务员', '价税合计': '提货金额'}, inplace=True)
            if not isclsatdf(clnmsneeded, dftmp.columns):
                # print(fl, dftmp.shape[0], k, "不合格的sheet", sep="\t")
                continue
            else:
                print(fl, dftmp.shape[0], k, "合格的sheet", sep="\t")
            df = df.append(dftmp, ignore_index=False)
#     print(df.shape[0])
#     print(df.dtypes)
    if (not isclsatdf(clnmsneeded, df.columns)) or (df.shape[0] == 0):
        return

    # 拷贝一份数据进行操作，避免链式赋值错误警告
    dftmp = df[clnmsneeded].copy()
    dftmp['计提标准'] = dftmp['含税单价'].apply(lambda x: 0.024 if x < 20 else 0.03)
    dftmp['业务奖金标准'] = dftmp['计提标准'] / 2
    dftmp['奖金金额'] = dftmp['计提标准'] * dftmp['提货金额']
    dftmp['业务应分配金额'] = dftmp['业务奖金标准'] * dftmp['提货金额']
    dftmp['奖金金额'] = dftmp['奖金金额'].map(lambda x: round(x, 2))
    dftmp['业务应分配金额'] = dftmp['业务应分配金额'].map(lambda x: round(x, 2))
    dftmpgr = dftmp.groupby(['开票日期', '客户简称', '业务员', '计提标准', '业务奖金标准']).sum()[['提货金额', '奖金金额', '业务应分配金额']]
    dfdone = dftmpgr.reset_index(['开票日期', '客户简称', '计提标准', '业务奖金标准', '业务员'])
    dfout = dfdone[['开票日期', '客户简称', '提货金额', '计提标准', '奖金金额', '业务奖金标准', '业务应分配金额', '业务员']]

    return dfout


# %% [markdown]
# ### getmonthtotal(df, month)

# %%
def getmonthdf(df, month):
    month_start = pd.to_datetime(f"{month[:4]}-{month[-2:]}-01")
    month_end = pd.to_datetime(f"{month[:4]}-{month[-2:]}-01 23:59:59") + MonthEnd()
    dftmp = df[df['开票日期'] >= month_start]
    dftmp = dftmp[dftmp['开票日期'] <= month_end]
    print(month_start, dftmp['开票日期'].min(),month_end, dftmp['开票日期'].max())
    
    return dftmp


# %% [markdown]
# ### def getdftotal(df, month)

# %%
def getdftotal(df, month):
    dftmp = getmonthdf(df, month)
    dftmpgr = dftmp.groupby(['客户简称', '业务员', '计提标准', '业务奖金标准']).sum()[['提货金额', '奖金金额', '业务应分配金额']]
    dfdone = dftmpgr.reset_index(['客户简称', '计提标准', '业务奖金标准', '业务员'])
    dfout = dfdone[['客户简称', '提货金额', '计提标准', '奖金金额', '业务奖金标准', '业务应分配金额', '业务员']]
    
    return dfout


# %% [markdown]
# ### def getserver(sale)

# %%
def getwaiter(sale, waiterdict):
    """
    通过服务管辖字典查找并返回对应业务负责人
    """
#     waiterdict = {"刘仓奇": ["孙斌", "杨志文"], "茹金建": ["白德鹏"]}
    for k, v in waiterdict.items():
        if sale in waiterdict[k]:
            return k


# %% [markdown]
# ### def expandsale(df)

# %%
def expandsale(df):
    """
    纵向扩展记录。奖金超过500元，增加“外部分配”；如果有驻地业务，则追加定制服务人员。
    """
    dftmp = df.copy(deep=True)
    waiterdict = {"刘仓奇": ["孙斌", "杨志文", "马芹利"], "茹金建": ["白德鹏"]}
    for ix in dftmp.index:
        dsorigin = dftmp.loc[ix]
        if dsorigin['业务应分配金额'] > 500:
            ds = dsorigin.copy()
            sale = ds['业务员']
            if sale not in waiterdict.keys():
                dsother = ds.copy()
                dsother['业务员'] = getwaiter(sale, waiterdict)
                dftmp = dftmp.append(dsother, ignore_index=True)
            ds['业务员'] = "外部分配"
            dftmp = dftmp.append(ds, ignore_index=True)
    # 按客户、索引排序确保“业务员”列的正常排序，然后在输出时重置索引，避免杂乱
    dfout = dftmp.reset_index().sort_values(['客户简称', "index"])

    return dfout[[cl for cl in dfout.columns if cl != 'index']].reset_index(drop=True)


# %% [markdown]
# ### def clsplit(tglst)

# %%
def clsplit(tglst):
    """
    遍历输入列表，纵向查找不同内容的分割点，
    返回内容数量超过两个的键值字典：键值为分割起点，值为相同内容的计数
    """
    lst = list()
    i = 0
    # 从头遍历查询分割点
    while i < len(tglst):
        # 对尾部做特殊处理
        if (i + 1) == len(tglst):
            lst.append(i + 1)
            break
        if tglst[i] != tglst[i + 1]:
            lst.append(i + 1)
        i += 1
    # 前插0，补上第一个分割点
    lst.insert(0, 0)
    # print(lst)

    outdict = dict()
    for i in range(len(lst) - 1):
        overone = lst[i + 1] - lst[i]
        # if overone == 1:
        #     continue
        outdict[lst[i]] = overone

    return outdict


# %% [markdown]
# ### fenpei2excel(dfdone, month)

# %%
def fenpei2excel(dfin, month):
    dfdone = expandsale(dfin)
    datapath = getdirmain() / 'data' / 'taibai'
    path2 = datapath / f"{month[2:4]}年{month[-2:]}月定制奖金分配.xlsx"
    with pd.ExcelWriter(path2) as writer:
        workbook = writer.book
        header = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True,})
        bold_first_cl = workbook.add_format({'bold': True, 'align': 'left', 'valign': 'vcenter', 'text_wrap': False,})
        bold_only = workbook.add_format({'bold': True,})
        bold_int = workbook.add_format({'bold': True, 'num_format': '0',})
        vcenter_content = workbook.add_format({'valign': 'vcenter', 'text_wrap': False,})
        vcenter_content_percent = workbook.add_format({'valign': 'vcenter', 'text_wrap': False, 'num_format': '0.0%',})
        vcenter_content_percent0 = workbook.add_format({'valign': 'vcenter', 'text_wrap': False, 'num_format': '0.0%',})
        vcenter_content_int = workbook.add_format({'valign': 'vcenter', 'text_wrap': False, 'num_format': '0',})

        first_row = list(dfdone.columns)
        first_row.extend(['奖金', '占比', '核对'])
        ws = workbook.add_worksheet(f'{month}定制奖金分配')
        ws.write_row(0, 0, first_row, cell_format=header)
        for i in range(dfdone.shape[0]):
            ws.write_row(1 + i, 0, dfdone.iloc[i])
        ws.set_column("A:A", 15, cell_format=bold_first_cl)
        ws.set_column("B:B",cell_format=vcenter_content_int)
        ws.set_column("C:C",cell_format=vcenter_content_percent)
        ws.set_column("D:D",cell_format=vcenter_content_int)
        ws.set_column("E:E",cell_format=vcenter_content_percent)
        ws.set_column("F:F",cell_format=vcenter_content_int)

        # 处理首列（客户名称），然后在此范围内处理后续其他列的数据
        ftglst = list(dfdone.iloc[:,0])
        fspdict = clsplit(ftglst)
        print(fspdict)
        for k, v in fspdict.items():
            print(k, v, ftglst[k])
            ws.merge_range(1 + k, 0, 1 + k + v - 1, 0, ftglst[k], bold_first_cl)
            for cl in range(1, len(dfdone.columns) - 1):
                innerlst = list(dfdone.iloc[k:k+v, cl])
                innerspdict = clsplit(innerlst)
                print("\t", cl, dfdone.columns[cl], innerspdict, innerlst, end="\t")
                for innerk, innerv in innerspdict.items():
                    target = innerlst[innerk]
                    # ws.merge_range(1 + k + innerk, cl, 1 + k + innerv - 1, cl, target, vcenter_content)
                    if (type(target) == float):
                        if target < 1.0:
                            ws.merge_range(1 + k + innerk, cl, 1 + k + innerv - 1, cl, target, vcenter_content_percent)
                        else:
                            ws.merge_range(1 + k + innerk, cl, 1 + k + innerv - 1, cl, target, vcenter_content_int)
                    else:
                        ws.merge_range(1 + k + innerk, cl, 1 + k + innerv - 1, cl, target, vcenter_content)
                    print(type(target), target, end="\t")
                    for i in range(innerv):
                        cell_per_pos = f"I{2 + k + innerk + i}"
                        cell_divided = f"F{2 + k + innerk}"
                        cell_val = f"H{2 + k + innerk + i}"
                        cell_formula = f"={cell_val}/{cell_divided}"
                        ws.write_formula(cell_per_pos, cell_formula, vcenter_content_percent0)
                        print(cell_per_pos, cell_formula, end="\t")
                    cell_minus_pos = f"J{2 + k + innerk}"
                    cell_minus_tobesub = f"F{2 + k + innerk}"
                    cell_minus_sum_start = f"H{2 + k + innerk}"
                    cell_minus_sum_end = f"H{2 + k + innerk + innerv - 1}"
                    cell_minus_formula = f"={cell_minus_tobesub} - sum({cell_minus_sum_start}:{cell_minus_sum_end})"
                    ws.write_formula(cell_minus_pos, cell_minus_formula, vcenter_content_int)
                    print(cell_minus_pos, cell_minus_formula)
        rowtotal = dfdone.shape[0]
        ws.write_string(f"A{rowtotal + 2}", "合计", bold_only)
        for cn in ['B', 'D', 'F', 'J']:
            ws.write_formula(f"{cn}{rowtotal + 2}", f"=sum({cn}2:{cn}{rowtotal + 1})", bold_int)
        # ws.write_formula("O1", "=UNIQUE(G:G)")
        ws.write_string("O1", "人员")
        teamnamelst = list(dfdone.groupby(['业务员']).sum().index)
        for i in range(len(teamnamelst)):
            ws.write_string(f"O{i + 2}", teamnamelst[i])
            ws.write_formula(f"P{i + 2}", f"=SUMIF(G:H,O{i + 2},H:H)")

        start_yewu = 2
        ws.write_string(f"L{start_yewu - 1}", "业务员分配汇总", bold_int)
        teamnamelst_sales = [x for x in list(dfdone.groupby(['业务员']).sum().index) if x != "外部分配"]
        end_row = start_yewu + len(teamnamelst) - 1
        for i in range(len(teamnamelst_sales)):
            ws.write_string(f"L{i + start_yewu}", teamnamelst_sales[i])
            ws.write_formula(f"M{i + start_yewu}", f"=SUMIF(O2:P{end_row},L{i + 2},P2:P{end_row})")
        ws.write_string(f"L{len(teamnamelst_sales) + start_yewu}", "合计", bold_only)
        ws.write_formula(f"M{len(teamnamelst_sales) + start_yewu}", 
                         f"=SUM(M{start_yewu}:M{len(teamnamelst_sales) + 1})",bold_int)

        start_xg = start_yewu + len(teamnamelst_sales) + 3
        ws.write_string(f"L{start_xg - 1}", "销管分配", bold_only)
        teamnamelst_xg = ["耿华忠", "曹鑫"]
        for i in range(len(teamnamelst_xg)):
            ws.write_string(f"L{i + start_xg}", teamnamelst_xg[i])
        ws.write_string(f"L{len(teamnamelst_xg) + start_xg}", "合计", bold_only)
        ws.write_formula(f"M{len(teamnamelst_xg) + start_xg}", 
                         f"=SUM(M{start_xg}:M{start_xg + len(teamnamelst_xg) - 1})",bold_int)
        ws.write_formula(f"N{start_xg - 1}", 
                         f"=int(F{rowtotal + 2}/15*2) - M{len(teamnamelst_xg) + start_xg}", bold_int)

        start_wb = start_xg + 2 + 3
        ws.write_string(f"L{start_wb - 1}", "定制外部分配", bold_only)
        ws.write_formula(f"N{start_wb - 1}", 
                         f"=index(P2:P{len(teamnamelst) + 1},match(\"外部分配\",O2:O{len(teamnamelst) + 1},0)) - sum(M{start_wb}:M{start_wb + 10})", bold_int)

        ws.merge_range(f"O{start_xg - 1}:P{start_xg - 1}",f"O{start_xg - 1}")
        ws.merge_range(f"O{start_xg}:P{start_xg}",f"O{start_xg}")
        ws.write_string(f"O{start_xg - 1}", "月度结余", header)
        ws.write_formula(f"O{start_xg}", f"=sum(N:N)", vcenter_content_int)

        # 写入客户销售汇总数据表，备份核对用
        ws_details = workbook.add_worksheet(f'{month}客户销售汇总')
        ws_details.write_row(0, 0, list(dfin.columns), cell_format=header)
        for i in range(dfin.shape[0]):
            ws_details.write_row(1 + i, 0, dfin.iloc[i])


# %% [markdown]
# ## 主运行函数

# %%
if __name__ == '__main__':
    if not_IPython():
        log.info(f'运行文件\t{__file__}')

    datapath = getdirmain() / 'data' / 'taibai'
    dfout = managesourcesxlsx2cleandf(datapath)
    yuefen = "202203"
    dfdone = getdftotal(dfout, yuefen)
    fenpei2excel(dfdone, yuefen)

    if not_IPython():
        log.info(f"文件\t{__file__}\t运行结束。")
