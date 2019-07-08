"""
处理微信相关账务事宜
"""

import re
import os
import pandas as pd

import pathmagic

with pathmagic.context():
    from func.configpr import getcfpoptionvalue, setcfpoptionvalue
    from func.first import dirlog, dirmainpath
    from func.logme import log
    from func.evernttest import get_notestore, imglist2note, tablehtml2evernote, getinivaluefromnote, getnotecontent
    from func.splitwebchatmsgs import fulltxt
 

def finance2note(srccount, rstdf, mingmu, mingmu4ini, title):
    print(f"df索引名称为：{rstdf.index.name}")
    noteguid = getinivaluefromnote('webchat', mingmu)
    count_zdzz = getcfpoptionvalue('everwebchat', 'finance', mingmu4ini)
    if not count_zdzz:
        count_zdzz = 0
    # print(f"{count_zdzz}")

    rstdf.fillna('None', inplace=True)
    colstr = f'{rstdf.index.name}\t' + '\t'.join(list(rstdf.columns)) + '\n'
    itemstr = colstr
    for idx in rstdf.index:
        itemstr += str(idx)+ '\t' + '\t'.join(rstdf.loc[idx]) + '\n'
    # print(f"{itemstr}")
    notecontent = "<pre>" + itemstr + "</pre>"
    finance2note4debug = getinivaluefromnote('webchat', 'finance2note4debug')
    # print(f"{type(finance2note4debug)}\t{finance2note4debug}")
    if (srccount != count_zdzz) or finance2note4debug: # or True:
        imglist2note(get_notestore(), [], noteguid, title, notecontent)
        setcfpoptionvalue('everwebchat', 'finance', mingmu4ini, f"{srccount}")
        log.info(f"成功更新《{title}》，记录共有{rstdf.shape[0]}条")


def getfix4finance(guid, clnames):
    notecontent = getnotecontent(guid)
    ndiv = notecontent.find_all('div')
    # print(ndiv)
    # ndivlst = [x.string for x in ndiv if x.string]
    ndivlst = [x.text for x in ndiv if x.text][1:]
    # print(ndivlst)
    rstlst = []
    ptn = re.compile('[\xa0,， ]+')
    for im in ndivlst:
        # print(im.split('\xa0'*4))
        tsplit = re.split(ptn, im)
        # print(tsplit)
        ttt = [x.strip() for x in tsplit if len(x.strip()) > 0]
        # print(ttt)
        for i in range(len(ttt)):
            # print(ttt[i])
            if re.match('\d{4}-\d{2}-\d{2}', ttt[i]) and re.match('\d{2}:\d{2}:\d{2}', ttt[i+1]):
                ttt[i] = ' '.join(ttt[i:i+2])
                # ttt = ttt[:i+1] + ttt[i+2:]
        ttt = [x for x in ttt if not re.match('\d{2}:\d{2}:\d{2}', x)]
        # print(ttt)

        if len(ttt) != len(clnames):
            log.critical(f"账务数据格式不符合标准。{clnames}\t{ttt}")
            continue
        # print(ttt)
        rstlst.append(ttt)

    # print(rstlst)
    rstdf = pd.DataFrame(rstlst, columns=clnames)
    rstdf.set_index(clnames[0], inplace=True)
    # print(rstdf)
    
    return rstdf


def pickupzhuanzhanghuizongfromdf():
    indf = fulltxt()
    # indf = indf[indf.name == '微信支付']
    sdzzdf = indf[indf.content.str.contains('^转账收款汇总通知')].loc[:,['time', 'send', 'name', 'content']]
    # print(f"{sdzzdf['content']}")
    sdzzdf['amount'] = sdzzdf['content'].apply(lambda x : re.findall('向你转账([0-9]+\.[0-9]{2})元', x)[0])
    # print(f"{sdzzdf['amount']}")
    sdzzdf['memo'] = None
    # sdzzdf['memo'] = sdzzdf['content'].apply(lambda x : re.findall('[付收]款方备注(.*)', x)[0] if re.findall('[付收]款方备注(.*)', x) else None)
    sdzzdf['friend'] = sdzzdf['content'].apply(lambda x : re.findall('由(.*)向你', x)[0])
    sdzzdf['daycount'] = sdzzdf['content'].apply(lambda x : re.findall('今日收款([0-9]+)笔', x)[0])
    sdzzdf['daysum'] = sdzzdf['content'].apply(lambda x : re.findall('今日收款总额￥([0-9]+\.[0-9]{2})', x)[0])
    sdzzdf.set_index('time', inplace=True)
    clnameswithindex = ['time', 'daycount', 'friend', 'amount', 'daysum']
    rstdf = sdzzdf.loc[:, clnameswithindex[1:]]

    return rstdf, clnameswithindex


def caiwu2note(itemname, itemnameini, rstdf, clnameswithindex):
    print(f"<{itemname}>数据文本有效条目数：{rstdf.shape[0]}")
    shoukuanfixguid = getinivaluefromnote('webchat', f'{itemname}补')
    fixdf = getfix4finance(shoukuanfixguid, clnameswithindex)
    print(f"<{itemname}>修正笔记有效条目数：{fixdf.shape[0]}")
    alldf = rstdf.append(fixdf)
    bcount = alldf.shape[0]
    # 索引去重
    alldf = alldf[~alldf.index.duplicated()]
    acount = alldf.shape[0]
    print(f"{bcount}\t{acount}")
    alldf.sort_index(ascending=False, inplace=True)
    # print(alldf)
    print(f"<{itemname}>综合有效条目数：{alldf.shape[0]}")

    finance2note(alldf.shape[0], alldf, f'{itemname}', f"{itemnameini}", f'{itemname}记录')


    alldf['time'] = alldf.index
    alldf['date'] = alldf['time'].apply(lambda x : pd.to_datetime(x).strftime('%F'))
    alldf['amount'] = alldf['amount'].astype(float)
    agg_map = {'daycount':'count', 'amount':'sum'}
    alldfgrpagg = alldf.groupby('date', as_index=False).agg(agg_map)
    alldfgrpagg.columns = ['date', 'lcount', 'lsum']
    alldf.drop_duplicates(['date'], keep='first', inplace=True)
    finaldf = pd.merge(alldf, alldfgrpagg, how='outer', on=['date'])
    alldf = finaldf.loc[:,['date', 'lcount', 'daycount', 'daysum', 'lsum']]
    # 日期，记录项目计数，记录项目最高值，记录项目累计值，记录项目求和
    alldf.columns = ['date', 'lc', 'lh', 'lacc', 'lsum']
    shoukuanrihuizongguid = getinivaluefromnote('webchat', f'{itemname}总手动')
    rhzdengjidf = getfix4finance(shoukuanrihuizongguid, ['date', 'count', 'sum'])
    duibidf = pd.merge(alldf, rhzdengjidf, how='outer', on=['date'])

    # 判断覆盖天数是否需要更新
    itemslcsum = duibidf['lc'].sum()
    print(f"<{itemname}>记录条目数量:{itemslcsum}")
    itemslcsumini = getcfpoptionvalue('everwebchat', 'finance', f'{itemname}lcsum')
    print(f"<{itemname}>记录数量（ini）\t{itemslcsumini}")
    if not itemslcsumini:
        itemslcsumini = 0
    if itemslcsumini == itemslcsum: # and False:
        print(f"<{itemname}>收款记录数量无变化")
        return
    
    duibidf.set_index('date', inplace=True)
    duibidf.sort_index(ascending=False, inplace=True)
    col_names = list(duibidf.columns)
    col_names.append('check')
    duibidf = duibidf.reindex(columns=col_names)
    # 通过0的填充保证各列数据可以运算
    duibidf.fillna(0, inplace=True)
    duibidf['lacc'] = duibidf['lacc'].astype(float)
    duibidf['sum'] = duibidf['sum'].astype(float)
    duibidf['count'] = duibidf['count'].astype(int, errors='ignore')
    # print(duibidf.dtypes)
    duibidf['check'] = duibidf['lc'] - duibidf['count']
    duibidf['check'] = duibidf['check'].apply(lambda x : '待核正' if (x!=0) else '')
    duibiguid = getinivaluefromnote('webchat', f'{itemname}核对')
    title = f'{itemname}核对'
    notecontent = tablehtml2evernote(duibidf, title)
    imglist2note(get_notestore(), [], duibiguid, title, notecontent)
    setcfpoptionvalue('everwebchat', 'finance', f'{itemname}lcsum', f"{itemslcsum}")


def showjinzhang():
    indf = fulltxt()
    # dfgpc = indf.groupby(['name']).count()
    sdzzdf = indf[indf.content.str.contains('^收到转账')].loc[:,['time', 'send', 'name', 'content']]
    sdzzdfclnames = list(sdzzdf.columns)
    sdzzdfclnames.append('namecontent')
    sdzzdf = sdzzdf.reindex(columns=sdzzdfclnames)
    sdzzdf['namecontent'] = sdzzdf[['name', 'content']].apply(lambda x: x['name'] + x['content'], axis=1)
    zzdf = sdzzdf.loc[:, ['time', 'send', 'namecontent']]
    zzdf.set_index('namecontent', inplace=True)
    # print(sdzzdf)
    print(f"{zzdf.dtypes}")
    ixlst = list(set(zzdf.index))
    # print(f"{ixlst}")
    rstlst = []
    for ix in ixlst:
        item = []
        if type(zzdf.loc[ix]) == pd.core.series.Series:
            item.append(ix)
            item.append(zzdf.loc[ix]['time'])
            item.append(zzdf.loc[ix]['send'])
            rstlst.append(item)
            # print(f"{item}")
            continue
        if type(zzdf.loc[ix]) == pd.core.frame.DataFrame:
            mf = zzdf.loc[ix].sort_values(['time']).reset_index(drop=True)
            # print(f"{ix}\t{mf.shape[0]}\t{mf}")
            # 指针滚动，处理项目相同的各条记录
            ii = 0
            while ii < mf.shape[0]:
                item = []
                item.append(ix)
                item.append(mf.loc[ii]['time'])
                item.append(mf.loc[ii]['send'])
                if ii+1 == mf.shape[0]:
                    rstlst.append(item)
                    # print(f"{item}")
                    # print(f"循环到头了，添加走人")
                    break
                if mf.loc[ii,'send'] == mf.loc[ii+1,'send']:
                    rstlst.append(item)
                    # print(f"{item}")
                    # print(f"没有配对的，添加继续循环")
                    ii += 1
                    break
                else:
                    item.append(mf.loc[ii+1]['time'])
                    rstlst.append(item)
                    # print(f"{item}")
                    ii += 2

    # print(f"{rstlst}")
    dddf = pd.DataFrame(rstlst, columns=['namecontent', 'stime', 'send', 'etime'])
    dddf['stime'] = pd.to_datetime(dddf['stime'])
    # dddf['etime'] = pd.to_datetime(dddf['etime'])
    dddf.sort_values('stime', ascending=False, inplace=True)
    dddfclnames = list(dddf.columns)
    dddfclnames.append('name')
    dddfclnames.append('amount')
    dddfclnames.append('memo')
    dddf = dddf.reindex(columns=dddfclnames)
    dddf['name'] = dddf.namecontent.apply(lambda x : re.split('收到转账', x)[0])
    dddf['amount'] = dddf.namecontent.apply(lambda x : re.findall('([0-9\.]{2,})', x)[0])
    dddf['memo'] = dddf.namecontent.apply(lambda x : re.findall('\[(.*)\]', x)[0])
    dddf.set_index('stime', inplace=True)
    clnameswithindex = ['stime','name', 'amount', 'send', 'memo', 'etime' ]
    rstdf = dddf.loc[:, clnameswithindex[1:]]
    # print(rstdf.dtypes)
    print(f"数据文本有效条目数：{rstdf.shape[0]}")
    jinzhangfixguid = getinivaluefromnote('webchat', '收到转账补')
    fixdf = getfix4finance(jinzhangfixguid, clnameswithindex)
    fixdf['stime'] = pd.to_datetime(fixdf.index)
    fixdf.set_index('stime', inplace=True)
    # fixdf['etime'] = pd.to_datetime(fixdf['etime'])
    # print(fixdf.dtypes)
    print(f"修正笔记有效条目数：{fixdf.shape[0]}")
    alldf = rstdf.append(fixdf)
    # alldf['etime'] = alldf['etime'].apply(lambda x: x.strftime('%F %T') if x!=pd.NaT else x)
    alldf.sort_index(ascending=False, inplace=True)
    # print(alldf)
    print(f"综合有效条目数：{alldf.shape[0]}")
    
    finance2note(alldf.shape[0], alldf, '收到转账全部', 'zdzz', '微信个人转账(全部)收款记录')

    secretstrfromini = getinivaluefromnote('webchat', 'secret')
    # print(f"{secretstrfromini}")
    secretlst = re.split('[,，]', secretstrfromini)
    # print(f"{secretlst}")
    rst4workdf = alldf[~alldf.name.isin(secretlst)]
    # print(f"{rst4workdf}")
    rstdf = rst4workdf.loc[:,:]
    # print(f"{rstdf}")
    finance2note(rstdf.shape[0], rstdf, '收到转账工作', 'zdzzwork', '微信个人转账收款记录')

    alldf['amount'] = alldf['amount'].astype(float)
    jzdf = alldf[alldf.send.isin(['False'])]
    jzdf = jzdf[jzdf.etime != None]
    print(jzdf.dtypes)
    agg_map = {'name':'count', 'amount':'sum'}
    rsdf = jzdf.resample('D').agg(agg_map).sort_index(ascending=False)
    rsdf.columns = ['count', 'sum']
    # print(rsdf)


def pickupshoukuanfromdf():
    indf = fulltxt()
    sdzzdf = indf[indf.content.str.contains('^微信支付收款')].loc[:,['time', 'send', 'name', 'content']]
    sdzzdf['amount'] = sdzzdf['content'].apply(lambda x : re.findall('([0-9]+\.[0-9]+)', x)[0])
    sdzzdf['memo'] = sdzzdf['content'].apply(lambda x : re.findall('[付收]款方备注(.*)', x)[0] if re.findall('[付收]款方备注(.*)', x) else None)
    sdzzdf['friend'] = sdzzdf['content'].apply(lambda x : '微信好友' if re.findall('朋友到店', x) else None)
    sdzzdf['daycount'] = sdzzdf['content'].apply(lambda x : re.findall('今日第([0-9]+)笔', x)[0] if re.findall('今日第([0-9]+)笔', x) else None)
    sdzzdf['daysum'] = sdzzdf['content'].apply(lambda x : re.findall('共计￥([0-9]+\.[0-9]{2})', x)[0] if re.findall('共计￥([0-9]+\.[0-9]{2})', x) else None)
    sdzzdf.set_index('time', inplace=True)
    clnameswithindex = ['time', 'daycount', 'friend', 'amount', 'memo', 'daysum']
    rstdf = sdzzdf.loc[:, clnameswithindex[1:]]

    return rstdf, clnameswithindex


def showzhuanzhanghuizong():
    itemname = '微信转账日汇'
    itemnameini = 'wxzzrh'
    rstdf, clnameswithindex = pickupzhuanzhanghuizongfromdf()
    caiwu2note(itemname, itemnameini, rstdf, clnameswithindex)    


def showshoukuan():
    itemname = '微信号收款'
    itemnameini = 'wxhsk'
    rstdf, clnameswithindex = pickupshoukuanfromdf()
    caiwu2note(itemname, itemnameini, rstdf, clnameswithindex)    


def otherszhang(indf):
    lqtxdf = indf[indf.content.str.contains('^零钱提现')].loc[:,['send', 'name',
                                                                  'content']]
    # print(f"{lqtxdf}")
    wxzfpzdf = indf[indf.content.str.contains('^微信支付凭证')].loc[:,['send', 'name',
                                                                  'content']]
    zwdf = pd.concat([sdzzdf, lqtxdf, wxzfpzdf, wxzfskdf])
    # print(f"{zwdf.sort_index(ascending=False)}")


def showfinance():
    showjinzhang()
    showzhuanzhanghuizong()
    showshoukuan()


if __name__ == '__main__':
    log.info(f'开始运行文件\t{__file__}')
    # jinzhangfixguid = '39c0d815-df23-4fcc-928d-d9193d5fff93' 
    # shoukuanrihuizongguid = '25b6e71d-5f43-4147-b45c-8147b35c8f00'
    # skrhzdf = getfix4finance(shoukuanrihuizongguid, ['date', 'count', 'sum'])
    # print(skrhzdf)
    # showjinzhang()
    # showshoukuan()
    # showzhuanzhanghuizong()
    showfinance()
    log.info(f'{__file__}\t文件运行结束。')
