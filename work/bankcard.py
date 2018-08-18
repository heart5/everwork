# encoding:utf-8
"""
根据银行卡的流水记录，自动提取更新公司相关记录到共享笔记本中相应笔记中
笔记本：银行卡，guid：34b5423f-296f-4a87-b8c0-2ca0a6113053
笔记本：财务管理，guid：bec668cd-bc55-4496-83e3-660044042399

全纪录 to 公司相关流水
招行（9929）：0248c009-f709-40b2-9cf1-f28ed6b3a44e
农商行（6047：82e5d858-5fc5-4816-8cc0-f83eb261b4f2
工行（7520）：1fa53462-ba4b-42b3-87b1-d03f0dd7f432
农商行（2073）朱平：81a9c899-c960-4a64-ba02-0de9792df4a0
农行（8574）：f05636eb-12a7-4198-a652-b39e7f34d327
邮储（4824）：2e2cde17-447b-4d9b-833e-c5fb40230328
工行（8527）罗运辉：d86c3a51-e68d-4866-8b74-7cbd1d55ddfb
招行（6028）：12eedce8-ab24-495a-b987-dc4923627563
交行（5631）：054b9077-a866-4c1c-a7c7-943064dd75b4
中信（3391）：aa5acf2c-1395-43c6-a46a-82dda20a1ba9
招行（1568）朱平：328eda47-f199-4469-bdba-8b4df2426fbe
招行（4367）范小华：c38262ff-920a-4b60-b7ff-1918b6175ac2

"""
import re

from bs4 import BeautifulSoup

from func.logme import log
from func.evernt import findnotefromnotebook, token, get_notestore, evernoteapijiayi


def fetchfinacefromliushui():
    note_store = get_notestore()
    nbguid = '34b5423f-296f-4a87-b8c0-2ca0a6113053'
    finacenotefind = findnotefromnotebook(token, nbguid, '储蓄卡')

    ptn = re.compile(u'\s*(\d{4}年\d{1,2}月\d{1,2}日)\s+([出入])\s+([\d.]+元)\s+(.+)')
    resultlist = list()
    for item in finacenotefind:
        note = note_store.getNote(item[0], True, True, False, False)
        evernoteapijiayi()
        print(f'{item[0]}\t{item[1]}')
        souporigin = BeautifulSoup(note.content, "html.parser")
        # print(souporigin)
        # for im in souporigin.find_all(re.compile("^div$")):
        itemlist = list()
        for im in souporigin.find_all(re.compile("^div$")):
            imtxt = im.get_text()
            if im.has_attr('style'):
                print(f'{len(im.attrs)}\t{im.attrs}')
                continue
            if len(imtxt) == 0:
                continue
            if len(re.split(ptn, imtxt)) != 6:
                print(imtxt)
                continue
            itemlist.append(re.split(ptn, imtxt))
        resultlist.append(itemlist)

    return resultlist


if __name__ == '__main__':
    log.info(f'运行文件\t{__file__}')
    resultlist = fetchfinacefromliushui()
    print(resultlist)
    print('Done.完毕。')
