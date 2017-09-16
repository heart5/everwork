#! python3
# encoding:utf-8
# 学习excel表格的操作
# 0大数据分析（真元）.xlsx
import openpyxl,pprint

print(u'打开excel表格中……')
wb = openpyxl.load_workbook(u'0大数据分析（真元）.xlsx')
sheetlist = wb.get_sheet_names()
print(sheetlist)
sheet = wb.get_active_sheet()
print(sheet)