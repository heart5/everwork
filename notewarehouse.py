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
from imp4nb import *


#
# 把分钟数转换成分时的显示方式，用于纵轴标签
#
def min_formatter(x, pos):
    return r"%02d:%02d" %(int(x/60), int(x%60)) #%02d，用两位数显示数字，不足位数则前导0填充


def pickstat(note_store, destguid=None):
    cnx = lite.connect('data\\quandan.db')
    # df = pd.read_sql('select * from fileread',cnx)
    # sql = "update quandan set 无货金额 = NULL where 无货金额 like '%s'" %('.') #把无货金额字段中非法字符做妥善处理
    # print(sql)
    # result = cnx.cursor().execute(sql)
    # print(result)
    # cnx.commit()
    # sql = "select * from quandan where 无货金额 like '%s'" %('.')
    # print(sql)
    try:
        df = pd.read_sql("select * from quandan", cnx)
        df = df[df.配货人 != '作废']
        df['订单日期'] = pd.to_datetime(df['订单日期'])
        df = df[df['订单日期'] >= pd.to_datetime('2016-04-01')]
        df['送达日期'] = pd.to_datetime(df['送达日期'])
        df['收款日期'] = pd.to_datetime(df['收款日期'])

    except:
        pass

    print(df.columns)
    dd = pd.DataFrame(df.groupby(['订单日期']).size(), columns=['订单数量'])
    dd['错配单数'] = df.groupby(['订单日期']).sum()['配货准确']
    dd['订单金额'] = df.groupby(['订单日期']).sum()['送货金额']
    dd['无货金额'] = df.groupby(['订单日期']).sum()['无货金额']
    dd['漏配金额'] = df.groupby(['订单日期']).sum()['少配金额']
    dd['错配金额'] = df.groupby(['订单日期']).sum()['配错未要']
    print(dd)

    df['年月'] = df['订单日期'].apply(lambda x: "%04d-%02d" % (x.year, x.month))

    ph = pd.DataFrame(df.groupby(['配货人', '年月']).size())
    ph.columns = ['配单']
    ph['配错单数'] = df.groupby(['配货人', '年月']).sum()['配货准确']
    ph['配货金额'] = df.groupby(['配货人', '年月']).sum()['送货金额']
    ph['漏配金额'] = df.groupby(['配货人', '年月']).sum()['少配金额']
    ph['错配金额'] = df.groupby(['配货人', '年月']).sum()['配错未要']

    dd.plot()
    # plt.show()
    plt.savefig("img\\pick\\pickstat.png")
    plt.close()

    print(df.groupby(['业务主管']).size())

    cnx.close()

    img_wenshifeng_path = "img\\pick\\pickstat.png"
    img_sunonoff_path = 'img\\pick\\pickstat.png'

    #
    # 要更新一个note，生成一个Note（），指定guid，更新其content
    #
    note = Types.Note()
    note.title = "订单配货统计图"
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