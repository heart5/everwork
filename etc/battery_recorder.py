import pathmagic
with pathmagic.context():
    from func.logme import log
    from func.first import touchfilepath2depth, getdirmain
    from etc.battery_manage import batteryrecord2db
    
if __name__ == "__main__":
    logstrouter = "运行文件\t%s" %__file__
    log.info(logstrouter)
    dbnameouter = touchfilepath2depth(getdirmain() / "data" / "db" / f"batteryinfo.db")
    batteryrecord2db(dbnameouter)
    logstrouter = "文件%s运行结束" %(__file__)
    log.info(logstrouter)