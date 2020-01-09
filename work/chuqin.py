# encoding:utf-8
"""
月度出勤统计
"""
import os
import re
import math
import pandas as pd

import pathmagic

with pathmagic.context():
    from func.logme import log
    from func.first import dirmainpath
    from func.configpr import getcfpoptionvalue
    from func.evernttest import getinivaluefromnote


def chuqinjiluzhengli():
    """
    整理原始出勤记录，输出有用信息
    :return: 有用信息列表
    """
    print(dirmainpath)
    qdpath = dirmainpath / 'data' / 'work' / '考勤记录'
    print(qdpath)
    ptn = re.compile('^员工出勤记录(20\\d{4}).*\\.xls$')
    stopcount = 0
    fls = os.listdir(qdpath)
    print(len(fls))
    targetlst = []
    for fl in fls:
        timestamp = re.findall(ptn, fl)
        if timestamp:
            cld = []
            qddf = pd.read_excel(qdpath / fl, sheet_name='考勤记录')
            shiduan = qddf.iloc[1, 2]  # 时间段
            """
            出勤统计时间段
            """
            zhibiao = qddf.iloc[1, 11]  # 制表时间
            jiludf = qddf.iloc[3:]
            cld.append(shiduan)
            cld.append(zhibiao)
            renshu = int(jiludf.shape[0] / 2)
            cld.append(f"{renshu}")
            clcount = len(jiludf.columns)
            jiludf.columns = range(1, clcount + 1)
            cllst = []
            jilulst = []
            danganlst = []
            for i in range(renshu):
                dangan = [jiludf.iloc[i * 2, 2], jiludf.iloc[i * 2, 10], jiludf.iloc[i * 2, 20]]
                danganlst.append(dangan)
                cllst.append(i + 1)
                jilulst.append(jiludf.iloc[i * 2 + 1])

            dangandf = pd.DataFrame(danganlst, columns=['number', 'name', 'bumen'])
            cld.append(dangandf)
            jiluoutdf = pd.DataFrame(jilulst)
            jiluoutdf = jiluoutdf.T
            # jiluoutdf.columns = cllst
            jiluoutdf.columns = list(dangandf['name'].values)
            cld.append(jiluoutdf)
            # cld.append(jilulst)
            targetlst.append(cld)
            # print(f"{fl}\t{timestamp[0]}\t{qddf.shape[0]}")
            # print(targetlst)
            stopcount += 1
        if stopcount >= 5:
            break

    return targetlst


def tongjichuqin():
    print('56')
    pass


def splitjs(jsstr: str):
    """
    处理《计时工》原始打卡记录，规范成合规的时间间隔
    :param jsstr: str
    :return: str
    """
    zhongwuxiaban = getcfpoptionvalue('everinifromnote', 'xingzheng', 'zhongwuxiaban')
    xiawushangban = getcfpoptionvalue('everinifromnote', 'xingzheng', 'xiawushangban')
    xiawuxiaban = getcfpoptionvalue('everinifromnote', 'xingzheng', 'xiawuxiaban')
    ptn = re.compile('\\d{2}:\\d{2}')
    findlst = re.findall(ptn, jsstr)
    if len(findlst) == 2:
        if (findlst[0] <= zhongwuxiaban) & (findlst[1] >= xiawushangban):
            findlst.insert(1, xiawushangban)
            findlst.insert(1, zhongwuxiaban)
            log.info(f"计时工打卡记录条目({len(findlst)})增补中午休息间隔\t{findlst}")
        elif (findlst[0] >= zhongwuxiaban) & (findlst[1] >= xiawushangban):
            log.info(f"计时工打卡记录条目({len(findlst)})属于正常下午班")
        elif (findlst[0] <= zhongwuxiaban) & (findlst[1] <= xiawushangban):
            log.info(f"计时工打卡记录条目({len(findlst)})属于正常上午班")
        else:
            log.critical(f"出现不合规范的计时工打卡记录({len(findlst)})\t{findlst}")
            findlst = None
    elif len(findlst) == 3:
        if findlst[0] <= zhongwuxiaban:
            findlst.insert(1, zhongwuxiaban)
            log.info(f"计时工打卡记录条目({len(findlst)})增补中午休息间隔\t{findlst}")
        else:
            log.critical(f"出现不合规范的计时工打卡记录({len(findlst)})\t{findlst}")
            findlst = None
    elif len(findlst) == 1:
        if findlst[0] <= zhongwuxiaban:
            findlst.append(zhongwuxiaban)
            log.info(f"计时工打卡记录条目({len(findlst)})增补中午休止\t{findlst}")
        elif findlst[0] >= zhongwuxiaban:
            findlst.append(xiawuxiaban)
            log.info(f"计时工打卡记录条目({len(findlst)})增补下午休止\t{findlst}")
        else:
            log.critical(f"出现不合规范的计时工打卡记录({len(findlst)})\t{findlst}")
            findlst = None
    elif len(findlst) == 4:
        pass
    elif len(findlst) != 0:
        log.critical(f"出现不合规范的计时工打卡记录({len(findlst)})\t{findlst}")
        findlst = None
    resultlst = findlst

    return resultlst


def computejishi(inputlst: list):
    """
    计算工时
    :param inputlst:
    :return:
    """
    if (len(inputlst) % 2) != 0:
        log.critical(f"打卡记录非偶数\t{inputlst}")
        return

    # print(inputlst)
    totalminute: int = 0
    for i in range(0, len(inputlst), 2):
        frtlst = inputlst[i].split(":")
        # print(frtlst, end='\t')
        frtmin = int(frtlst[0]) * 60
        frtmin += int(frtlst[1])
        seclst = inputlst[i + 1].split(":")
        # print(seclst)
        secmin = int(seclst[0]) * 60
        secmin += int(seclst[1])
        totalminute += secmin - frtmin

    return totalminute


def tongjichuqinjishigong(inputs: pd.Series):
    """
    统计工时
    :param inputs: 打卡，Series
    :return: 出勤天数，分钟数累计，工时数
    """
    df = pd.DataFrame(inputs)
    df.columns = ['打卡记录']
    # print(df)
    df['整理'] = df[df.columns[0]].apply(lambda x: splitjs(str(x)) if x else None)
    df['分钟'] = df[df.columns[1]].apply(lambda x: computejishi(x) if x else None)

    return df['分钟'].count(), df['分钟'].sum(), math.ceil(df['分钟'].sum() / 60)


def tongjichuqinixingzheng():
    pass


if __name__ == '__main__':
    log.info(f'运行文件\t{__file__}')

    qdlst = chuqinjiluzhengli()
    # print(qdlst)
    biaoti = qdlst[-1][0]
    print(biaoti)
    jilusdf = qdlst[-1][4]
    ptnsep = re.compile('[,，]')
    jslst = re.split(ptnsep, getinivaluefromnote('xingzheng', '计时工'))
    xzlst = re.split(ptnsep, getinivaluefromnote('xingzheng', '行政岗位'))
    for name in jilusdf.columns:
        if name in jslst:
            chugongtianshu: int
            fenzhongleiji: int
            gongshi: int
            chugongtianshu, fenzhongleiji, gongshi = tongjichuqinjishigong(jilusdf[name])
            print(f"计时工\t{name}\t{chugongtianshu}\t{fenzhongleiji}\t{gongshi}")
        elif name in xzlst:
            print(f"行政岗位\t{name}")
        else:
            print(f"正常岗位\t{name}")
    # print(qdlst)

    log.info(f'文件{__file__}运行结束')
