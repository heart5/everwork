#! python3
# encoding:utf-8
# 学习excel表格的操作
# 0大数据分析（真元）.xlsx
import openpyxl, pandas as pd

print(u'打开excel表格中……')
wb = openpyxl.load_workbook(u'2017年全单统计管理.xlsm', read_only=True )
# wb = openpyxl.load_workbook(u'2017年全单统计管理.xlsm')
# wb = openpyxl.load_workbook(u'0大数据分析（真元）.xlsx')
sheetlist = wb.get_sheet_names()
print(sheetlist)
sheet = wb.get_active_sheet()
print(sheet)
sheet = wb.get_sheet_by_name('全单统计管理 (bak)')
# print("总行数：", len(sheet.rows))

def toint(input):
    if input == None:
        return 0
    else:
        return int(input)

def tofloat(input):
    if input == None:
        return 0.0
    else:
        return float(input)

colnames = []
count = 0
bigdata = []
for row in sheet.rows:
    # print("行宽：", len(row))
    if count == 0:
        for cell in row:
            colnames.append(cell.value)
        count += 1
        continue
    itemrow = []
    for cell in row:
        if cell.value is None:
            itemrow.append(0)
        else:
            itemrow.append(cell.value)
    bigdata.append(itemrow)
    count += 1

print(colnames)
print(sheet.title)
print(sheet['A2'])
print(sheet['A3'].value)
print(bigdata[:20])
df = pd.DataFrame(bigdata)
df.fillna(value=0)
print(df[0:15])
print(df.columns)
df.columns=colnames
df['配货准确'] = df['配货准确'].astype(int)
df['积欠'] = df['积欠'].astype(float)
df['送货金额'] = df['送货金额'].astype(float)
df['实收金额'] = df['实收金额'].astype(float)
df['退货金额'] = df['退货金额'].astype(float)
df['客户拒收'] = df['客户拒收'].astype(float)
df['无货金额'] = df['无货金额'].astype(float)
df['少配金额'] = df['少配金额欠'].astype(float)
df['配错未要'] = df['配错未要'].astype(float)
print(df[0:15])
print(df.columns)
print(df[0:15])

print(df.tail())
print(df.describe())