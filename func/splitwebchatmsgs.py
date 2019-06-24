"""
拆分微信聊天记录并分类处理
"""

import re
import os
import pandas as pd

import pathmagic

with pathmagic.context():
    from func.configpr import cfp, inifilepath, getcfp
    from func.first import dirlog, dirmainpath
    from func.logme import log
    from func.evernttest import get_notestore, imglist2note, tablehtml2evernote, getinivaluefromnote
 

def finance2note(srccount, rstdf, mingmu, mingmu4ini, title):
    noteguid = getinivaluefromnote('webchat', mingmu)
    cfpcw, cfpcwpath = getcfp('everwebchat')
    if not cfpcw.has_section('finance'):
        cfpcw.add_section('finance')
        cfpcw.write(open(cfpcwpath, 'w', encoding='utf-8'))
    if cfpcw.has_option('finance', mingmu4ini):
        count_zdzz = cfpcw.getint('finance', mingmu4ini)
    else:
        count_zdzz = 0
    # print(f"{count_zdzz}")

    rstdf.fillna('None', inplace=True)
    colstr = 'index\t' + '\t'.join(list(rstdf.columns)) + '\n'
    itemstr = colstr
    for idx in rstdf.index:
        itemstr += str(idx)+ '\t' + '\t'.join(rstdf.loc[idx]) + '\n'
    # print(f"{itemstr}")
    notecontent = itemstr
    finance2note4debug = getinivaluefromnote('webchat', 'finance2note4debug')
    print(f"{type(finance2note4debug)}\t{finance2note4debug}")
    if (srccount != count_zdzz) or finance2note4debug:
        imglist2note(get_notestore(), [], noteguid, title, notecontent)
        cfpcw.set('finance', mingmu4ini, f"{srccount}")
        cfpcw.write(open(cfpcwpath, 'w', encoding='utf-8'))
        log.info(f"成功更新《{title}》，记录共有{rstdf.shape[0]}条")


def fulltxt():
    dmpath = dirmainpath / "data" / "webchat"
    # print(f"{dmpath}")

    # 找到最新的聊天记录文件
    file_list = os.listdir(dmpath)
    fnlst = [ x for x in file_list if x.startswith('chatitems') ]
    fnlst.sort(key=lambda fn: os.path.getmtime(dmpath / fn))
    tfn = dmpath / fnlst[-1]
    # print(tfn)

    f = open(tfn, 'r')
    ffulltxt = f.read()
    f.close()
    # print(ffulltxt[:400])
    ptn = re.compile("((20[0-9]{2}-)?[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2})\t((True)|(False))")
    rstlst = re.split(ptn, ffulltxt)[1:]
    # print(f"{rstlst[:20]}")
    rlstlen = len(rstlst)
    rlstcount = int(rlstlen / 6)
    log.info(f"聊天记录共有\t{rlstcount}\t条")
    testcount = rlstcount

    # 调试开关，控制输出的条目数
    # testcount = 20
    rstitems = []
    for i in range(testcount):
        item = []
        # print(f"{rstlst[i*6]}\t{rstlst[i*6 + 2]}\t{rstlst[i*6 + 5]}")
        item.append(rstlst[i*6])
        item.append(rstlst[i*6 + 2])
        # item.append(rstlst[i*6 + 5])
        ttxt = rstlst[i*6 + 5].strip()
        # ttxt = rstlst[i*6 + 5]
        # print(f"{ttxt}")
        # ttxtlst = ttxt.split('\t', 2)

        # 应对类型后直接换行的情况
        ttxtlst = re.split('[\t\n]', ttxt, 2)
        # 设立群字段，独立用户则该字段置空
        sender = re.split('\(群\)', ttxtlst[0])
        # print(f"{sender}")
        if len(sender) == 1:
            item.append(None)
            item.append(sender[0])
        else:
            item.append(sender[0])
            item.append(sender[1])
        # item.append(ttxtlst[0])
        item.append(ttxtlst[1])

        # 小函数，输出某行记录（原始状态的）
        def piminlst(inlst, start):
            print()
            for n in range(6):
                print(inlst[start + n], end='\t')
            print()

        # 处理content为空的情况
        if len(ttxtlst) == 3:
            item.append(ttxtlst[2])
        else:
            # piminlst(rstlst, i*6)
            item.append(None)
        rstitems.append(item)

    # print(rstitems[:20])
    df = pd.DataFrame(rstitems, columns=['time', 'send', 'qun', 'name',
                                            'type', 'content'])
    # 去空去重
    print(df.shape[0])
    ndf = df[df.content.isnull().values == True]
    # print(f"{ndf}")
    tdf = df[df.content.isnull().values != True]
    cdf = tdf.drop_duplicates(subset=['time', 'name', 'type', 'content'])
    print(cdf.shape[0])
    # rstdf = cdf.set_index('time')
    rstdf = cdf

    return rstdf


if __name__ == '__main__':
    log.info(f'开始测试文件\t{__file__}')
    # nost = get_notestore()
    # print(nost)
    allitems = fulltxt()
    print(allitems[:10])
    # print(f"{allitems[:30]}")
    # writeini()
    # findnotebookfromevernote()
    # notefind = findnotefromnotebook(
    # token, '4524187f-c131-4d7d-b6cc-a1af20474a7f', '日志')
    # print(notefind)
    log.info(f'对\t{__file__}\t的测试结束。')
