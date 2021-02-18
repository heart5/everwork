# encoding:utf-8
"""
date time function related
"""

from datetime import datetime, timedelta

import pathmagic
with pathmagic.context():
    from func.logme import log
print(f"{__file__} is loading now...")


def getstartdate(period, thedatetime):
    """
    return date depend on period idicated for certain datetime input
    period list: ['日', '周', '旬', '月', '年', '全部']
    """
    if period == '日':
        zuijindatestart = datetime.strptime(thedatetime.strftime("%Y-%m-%d"), "%Y-%m-%d")
    elif period == '周':
        weekstarttime = thedatetime - timedelta(days=thedatetime.weekday())  # Monday
        zuijindatestart = datetime.strptime(weekstarttime.strftime("%Y-%m-%d"), "%Y-%m-%d")
    elif period == '旬':
        if thedatetime.day < 10:
            frtday = 1
        elif thedatetime.day < 20:
            frtday = 10
        else:
            frtday = 20
        zuijindatestart = datetime.strptime(thedatetime.strftime(f"%Y-%m-{frtday}"), "%Y-%m-%d")
    elif period == '月':
        zuijindatestart = datetime.strptime(thedatetime.strftime("%Y-%m-1"),  "%Y-%m-%d")
    elif period == '年':
        zuijindatestart = datetime.strptime(thedatetime.strftime("%Y-1-1"),  "%Y-%m-%d")
    else:
        zuijindatestart = thedatetime

    return zuijindatestart


if __name__ == '__main__':
    log.info(f'运行文件\t{__file__}')

    periodlst = ['日', '周', '旬', '月', '年', '全部']
    for pr in periodlst:
        tned = getstartdate(pr, datetime.now())
        print(f"{pr}:\t{tned}")

    log.info(f"文件\t{__file__}\t运行结束。")
