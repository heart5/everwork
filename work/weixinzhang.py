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
    from func.splitwebchatmsgs import fulltxt
 

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
    notecontent = "<pre>" + itemstr + "</pre>"
    finance2note4debug = getinivaluefromnote('webchat', 'finance2note4debug')
    print(f"{type(finance2note4debug)}\t{finance2note4debug}")
    if (srccount != count_zdzz) or finance2note4debug: # or True:
        imglist2note(get_notestore(), [], noteguid, title, notecontent)
        cfpcw.set('finance', mingmu4ini, f"{srccount}")
        cfpcw.write(open(cfpcwpath, 'w', encoding='utf-8'))
        log.info(f"成功更新《{title}》，记录共有{rstdf.shape[0]}条")


def showjinzhang():
    indf = fulltxt()
    # dfgpc = indf.groupby(['name']).count()
    sdzzdf = indf[indf.content.str.contains('^收到转账')].loc[:,['time', 'send', 'name',
                                                                  'content']]
    sdzzdf['namecontent'] = sdzzdf['name'] + sdzzdf['content']
    zzdf = sdzzdf.loc[:, ['time', 'send', 'namecontent']]
    zzdf.set_index('namecontent', inplace=True)
    # print(f"{zzdf}")
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
    dddf.sort_values('stime', ascending=False, inplace=True)
    dddf['name'] = dddf.namecontent.apply(lambda x : re.split('收到转账', x)[0])
    dddf['amount'] = dddf.namecontent.apply(lambda x : re.findall('([0-9\.]{2,})', x)[0])
    dddf['memo'] = dddf.namecontent.apply(lambda x : re.findall('\[(.*)\]', x)[0])
    dddf.set_index('stime', inplace=True)
    rstdf = dddf.loc[:, ['name', 'amount', 'send', 'memo', 'etime']]
    # print(f"{rstdf}")
    
    finance2note(sdzzdf.shape[0], rstdf, '收到转账全部', 'zdzz', '微信个人转账(全部)收款记录')

    secretstrfromini = getinivaluefromnote('webchat', 'secret')
    # print(f"{secretstrfromini}")
    secretlst = re.split('[,，]', secretstrfromini)
    # print(f"{secretlst}")
    rst4workdf = rstdf[~rstdf.name.isin(secretlst)]
    # print(f"{rst4workdf}")
    rstdf = rst4workdf.loc[:,:]
    # print(f"{rstdf}")
    finance2note(sdzzdf.shape[0], rstdf, '收到转账工作', 'zdzzwork', '微信个人转账收款记录')


def showshoukuan():
    indf = fulltxt()
    # dfgpc = indf.groupby(['name']).count()
    sdzzdf = indf[indf.content.str.contains('^微信支付收款')].loc[:,['time', 'send', 'name',
                                                                  'content']]
    sdzzdf['amount'] = sdzzdf['content'].apply(lambda x :
                                               re.findall('([0-9]+\.[0-9]+)', x)[0])
    sdzzdf['memo'] = sdzzdf['content'].apply(lambda x :
                                               re.findall('付款方备注(.*)',
                                                          x)[0] if
                                             re.findall('付款方备注(.*)', x) else
                                            None)
    sdzzdf['friend'] = sdzzdf['content'].apply(lambda x :
                                               '微信好友' if re.findall('朋友到店',
                                                                  x) else None)
    sdzzdf['daycount'] = sdzzdf['content'].apply(lambda x :
                                               re.findall('今日第([0-9]+)笔',
                                                         x)[0] if re.findall('今日第([0-9]+)笔',
                                                                  x) else None)
    sdzzdf['daysum'] = sdzzdf['content'].apply(lambda x :
                                               re.findall('共计￥([0-9]+\.[0-9]{2})',
                                                         x)[0] if re.findall('共计￥([0-9]+\.[0-9]{2})',
                                                                  x) else None)
    sdzzdf.set_index('time', inplace=True)
    rstdf = sdzzdf.loc[:, ['daycount', 'friend', 'amount', 'memo', 'daysum' ]]
    # print(f"{rstdf}")

    finance2note(sdzzdf.shape[0], rstdf, '微信号收款', 'wxhsk', '微信号收账记录')


def otherszhang(indf):
    lqtxdf = indf[indf.content.str.contains('^零钱提现')].loc[:,['send', 'name',
                                                                  'content']]
    # print(f"{lqtxdf}")
    wxzfpzdf = indf[indf.content.str.contains('^微信支付凭证')].loc[:,['send', 'name',
                                                                  'content']]
    wxzfskdf = indf[indf.content.str.contains('^微信支付收款')].loc[:,['send', 'name',
                                                                  'content']]
    zwdf = pd.concat([sdzzdf, lqtxdf, wxzfpzdf, wxzfskdf])
    # print(f"{zwdf.sort_index(ascending=False)}")
    pass


def showfinance():
    showjinzhang()
    showshoukuan()


if __name__ == '__main__':
    log.info(f'开始运行文件\t{__file__}')
    showfinance()
    log.info(f'{__file__}\t文件运行结束。')
