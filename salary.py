# encoding:utf-8
"""
核算工资
"""
from imp4nb import *

cnx = lite.connect('data\\quandan.db')

# desclitedb(cnx)
# dataokay(cnx)

zhongduanstr = '  and (leixing.类型 =\'终端客户\')'
# zhongduanstr = ''
qrystr = "select strftime('%Y%m',日期) as 年月, 职员名称 as 业务主管, substr(customer.往来单位编号,1,2) as 区域, " \
         "xiaoshoumingxi.商品全名 as 产品, product.推广等级 as 等级, 单位全名 as 客户名称, 单据编号, " \
         '金额 as 销售金额, substr(customer.往来单位编号,12,1) as 类型编码 from xiaoshoumingxi, customer, product, leixing ' \
         'where (customer.往来单位 = xiaoshoumingxi.单位全名) and (product.商品全名 = xiaoshoumingxi.商品全名) and ' \
         ' (leixing.编码 = 类型编码) and (金额 >=0)'
qrystr += zhongduanstr
print(qrystr)
dfz = pd.read_sql_query(qrystr, cnx)
# descdb(dfz)

qrystr = "select strftime('%Y%m',日期) as 年月, 职员名称 as 业务主管, substr(customer.往来单位编号,1,2) as 区域, " \
         "xiaoshoumingxi.商品全名 as 产品, product.推广等级 as 等级, 单位全名 as 客户名称, 单据编号, " \
         '金额 as 销售金额, substr(customer.往来单位编号,12,1) as 类型编码 from xiaoshoumingxi, customer, product, leixing ' \
         'where (customer.往来单位 = xiaoshoumingxi.单位全名) and (product.商品全名 = xiaoshoumingxi.商品全名) and ' \
         ' (leixing.编码 = 类型编码) and (金额 <0)  and (leixing.类型 =\'终端客户\')'
qrystr += zhongduanstr
print(qrystr)
dff = pd.read_sql_query(qrystr, cnx)
# descdb(dff)

df = dfz.append(dff).sort_values(['年月', '业务主管'])

df['销售金额净'] = df['销售金额'].apply(lambda x: x * 5 if x < 0 else x)
ticheng = [0, 0.005, 0.01, 0.02, 0.03]
df['提成比例'] = df['等级'].apply(lambda x: ticheng[x - 1])
df['业绩奖金'] = df['销售金额净'] * df['提成比例']

print(df[df.业务主管 == '耿华忠'].groupby(['年月', '业务主管', '客户名称', '单据编号'])['销售金额净'].sum())

dftarget = df[df.年月 >= '201706'].groupby(['年月', '业务主管', '等级', '产品'], as_index=False)['销售金额净', '业绩奖金'].sum()
# print(df.tail(50))

dfyd = dftarget.groupby(['年月', '业务主管', '等级'], as_index=False)['销售金额净', '业绩奖金'].sum()
# print(dfyd.tail(50))

dfyt = dfyd.groupby(['年月', '业务主管', '等级'])['销售金额净', '业绩奖金'].sum().unstack().fillna(value=0)
# print(dfyt)
dfyt.reset_index(inplace=True)
descdb(dfyt)

# xlswriter = pd.ExcelWriter('data\\业绩奖金.xlsx')
# dfyt.to_excel(xlswriter, '业绩奖金', freeze_panes=[1, 2])
# xlswriter.close()

dfy = dftarget.groupby(['年月', '业务主管'], as_index=False)['销售金额净', '业绩奖金'].sum()
print(dfy.tail(60))


def shuoming(df2):
    return str(df2.ix[0, 0]) + str(df2[0, 1])


dfys = dfy
# dfys['UIi'] = dfys['年月', '业务主管'].apply(lambda x: shuoming(x))
# print(dfys)
# cnx.close()
