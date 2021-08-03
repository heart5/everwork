# encoding:utf-8
# %% [markdown]
# # 数据集动态存储至evernote（不同主机针对同一类笔记）

# %%
"""
date time function related
getstartdate
gethumantimedelay
"""

# %% [markdown]
# # 引入库

# %%
import os
import re
import pandas as pd

import pathmagic
with pathmagic.context():
    from func.first import getdirmain, touchfilepath2depth
    from func.logme import log
    from etc.getid import getdeviceid
    from func.sysfunc import not_IPython
    from func.evernttest import getinivaluefromnote, getnoteresource, gettoken, get_notestore, getnotecontent, updatereslst2note
# print(f"{__file__} is loading now...")

# %% [markdown]
# # 功能函数集

# %%
def huojieds2note():
    huojieguid = getinivaluefromnote('game', 'guid')
    notecontent = getnotecontent(huojieguid)

    jushufromnote = int([x.split('：')[1] for x in notecontent.find('pre').text.split()][0])
    musedatapath = getdirmain() / 'data' / 'muse'
    tlst = [musedatapath / pt for pt in os.listdir(musedatapath) if pt.endswith('xlsx') or pt.endswith('xls')]
    df = pd.DataFrame()
    for datafile in tlst:
        df = df.append(pd.read_excel(datafile))

    df = df.drop_duplicates().sort_values('time', ascending=False)
    jushufromhost = df.shape[0] // 4

    if jushufromnote != jushufromhost:
        datamainpath = getdirmain() / 'data' / 'tmp' / 'huojiemain.xlsx'
        touchfilepath2depth(datamainpath)
        
        reslst = getnoteresource(huojieguid)
        targetbinlst = [x[1] for x in reslst if x[0] == os.path.basename(datamainpath)]
        if len(targetbinlst) != 0:            
            huojiefromnotepath = dirmainpath / 'data' / 'tmp' / 'huojiemainfromnote.xlsx'
            f = open(huojiefromnotepath, 'wb')
            f.write(targetbinlst[0])
            f.close()
            log.info(f"本地数据局数为：{jushufromhost}")
            df = df.append(pd.read_excel(huojiefromnotepath))
            df = df.drop_duplicates().sort_values('time', ascending=False)
            jushufromhost = df.shape[0] // 4
            log.info(f"添加网络数据后的总局数为：{jushufromhost}")
        df.to_excel(datamainpath, index=False)

        timemin = df['time'].min()
        timemax = df['time'].max()
        deviceid = getdeviceid()
        if (device_name := getinivaluefromnote('device', deviceid)) is None:
            device_name = deviceid
        updatereslst2note([datamainpath], huojieguid, neirong=f'局数：{jushufromhost}\n时间跨度：{timemin}至{timemax}\n{device_name}', filenameonly=True)
    
    return jushufromnote, jusdhufromhost


# %% [markdown]
# # 运行主函数main

# %%
if __name__ == '__main__':
    if not_IPython():
        log.info(f'运行文件\t{__file__}')

    huojieds2note()

    if not_IPython():
        log.info(f"文件\t{__file__}\t运行结束。")

# %%
