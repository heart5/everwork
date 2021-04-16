# encoding:utf-8
# %%
"""
date time function related
getstartdate
gethumantimedelay
"""

# %% [markdown]
# # 引入库

# %%
import arrow
from datetime import datetime, timedelta
from dateutil import tz

import pathmagic
with pathmagic.context():
    from func.logme import log
    from func.sysfunc import not_IPython
# print(f"{__file__} is loading now...")

# %%
def getstartdate(period, thedatetime):
    """
    return date depend on period idicated for certain datetime input
    period list: ['日', '周', '旬', '月', '年', '全部']
    """
    if period == '日':
        zuijindatestart = arrow.get(arrow.get(thedatetime).date()).naive
    elif period == '周':
        weekstarttime = thedatetime - timedelta(days=thedatetime.weekday())  # Monday
        zuijindatestart = arrow.get(arrow.get(weekstarttime).date()).naive
    elif period == '旬':
        # 连用两次三元操作，减缩代码行数
        frtday = 1 if thedatetime.day < 10 else (10 if thedatetime.day < 20 else 20)
        tmpdt = arrow.get(thedatetime).replace(day=frtday)
        zuijindatestart = arrow.get(tmpdt.date()).naive
    elif period == '月':
        zuijindatestart = arrow.get(arrow.get(thedatetime).replace(day=1).date()).naive
    elif period == '年':
        zuijindatestart = arrow.get(arrow.get(thedatetime).replace(month=1, day=1).date()).naive
    else:
        zuijindatestart = thedatetime

    return zuijindatestart


# %%
def test_getstartdate():
    periodlst = ['日', '周', '旬', '月', '年', '全部']
    for pr in periodlst:
        tned = getstartdate(pr, datetime.now())
        print(f"{datetime.now()}\t{pr}:\t{tned}\t{type(tned)}")


# %%
def gethumantimedelay(inputlocaltime, intervalseconds=120):
    """
    返回输入时间和当前时间差值的人类可读字符串
    默认对超过120秒（两分钟）的差值有效，否则返回False
    """
    # 默认用当地时间运算
    intime = arrow.get(inputlocaltime, tzinfo=tz.tzlocal())
    if (elasptime := arrow.now() - intime) and (elasptime.seconds > intervalseconds):
        # print(elasptime, elasptime.seconds)
        return intime.humanize(locale='zh_cn')
    else:
        return False


# %%
def test_gethumantimedelay():
    hmtimetestlst= ["20210227 01:04:23", arrow.get("20210227 02:04:23",
                                        tzinfo=tz.tzlocal()), "19761006"]
    for htt in hmtimetestlst:
        hmstr = gethumantimedelay(htt)
        print(hmstr)


# %% [markdown]
# # 运行主函数main

# %%
if __name__ == '__main__':
    if not_IPython():
        log.info(f'运行文件\t{__file__}')

    test_gethumantimedelay()
    test_getstartdate()
    
    if not_IPython():
        log.info(f"文件\t{__file__}\t运行结束。")

# %%
