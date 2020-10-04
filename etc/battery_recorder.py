# -*- coding: utf-8 -*-
import pathmagic
with pathmagic.context():
    from func.logme import log
    from func.first import touchfilepath2depth, getdirmain
    from etc.battery_manage import batteryrecord2db
    from func.sysfunc import not_IPython

if __name__ == "__main__":
    if not_IPython():
        logstrouter = "运行文件\t%s" % __file__
        log.info(logstrouter)
    dbnameouter = touchfilepath2depth(getdirmain() / "data" / "db" / f"batteryinfo.db")
    batteryrecord2db(dbnameouter)
    if not_IPython():
        logstrouter = "文件%s运行结束" % (__file__)
        log.info(logstrouter)

