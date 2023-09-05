# encoding:utf-8
# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     formats: ipynb,py:percent
#     notebook_metadata_filter: jupytext,-kernelspec,-jupytext.text_representation.jupytext_version
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
# ---

# %%
"""
手机联系人信息管理
"""
import os
import time
import re
# import datetime
import sqlite3 as lite
import pandas as pd
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
from bs4 import BeautifulSoup

# %%
import pathmagic
with pathmagic.context():
    from func.logme import log
    from func.first import touchfilepath2depth, getdirmain
    from func.litetools import ifnotcreate
    from func.configpr import getcfpoptionvalue, setcfpoptionvalue
    from func.termuxtools import termux_contact_list, termux_sms_list
    from etc.getid import getdeviceid
    from func.pdtools import lststr2img
    from func.sysfunc import sha2hexstr    
    from func.evernttest import findnotefromnotebook, get_notestore, evernoteapijiayi
    from func.nettools import trycounttimes2


# %%
def checkphoneinfotable(dbname: str):
    """
    检查联系人和短信数据表是否已经构建，设置相应的ini值避免重复打开关闭数据库文件进行检查
    """
    # 联系人数据表检查构建
    if not (phonecontactdb := getcfpoptionvalue('everpim', str(getdeviceid()), 'phonecontacttable')):
        tablename = "phone"
        print(phonecontactdb, tablename)
        csql = f"create table if not exists {tablename} (number str PRIMARY KEY not null unique on conflict ignore, name str, appendtime datetime)"
        ifnotcreate(tablename, csql, dbname)
        setcfpoptionvalue('everpim', str(getdeviceid()), 'phonecontacttable', str(True))
        logstr = f"数据表{tablename}在数据库{dbname}中构建成功"
        log.info(logstr)
        
    # 短信数据表检查构建
    if not (phonecontactdb := getcfpoptionvalue('everpim', str(getdeviceid()), 'phonesmstable')):
        tablename = "sms"
        print(phonecontactdb, tablename)
        # smsdfdone.columns = ['sent', 'sender', 'number', 'time', 'content', 'smsuuid']
        csql = f"create table if not exists {tablename} (type str,sent bool, name str, number str, time datetime, content str,smsuuid str PRIMARY KEY not null unique on conflict ignore)"
        ifnotcreate(tablename, csql, dbname)
        setcfpoptionvalue('everpim', str(getdeviceid()), 'phonesmstable', str(True))
        logstr = f"数据表{tablename}在数据库{dbname}中构建成功"
        log.info(logstr)

    # 联系人描述数据表检查构建
    if not (phonecontactdb := getcfpoptionvalue('everpim', str(getdeviceid()), 'phonectdesctable')):
        tablename = "ctdesc"
        print(phonecontactdb, tablename)
        # smsdfdone.columns = ['sent', 'sender', 'number', 'time', 'content', 'smsuuid']
        csql = f"create table if not exists {tablename} (name str,desc str)"
        ifnotcreate(tablename, csql, dbname)
        setcfpoptionvalue('everpim', str(getdeviceid()), 'phonectdesctable', str(True))
        logstr = f"数据表{tablename}在数据库{dbname}中构建成功"
        log.info(logstr)


# %%
def df2smsdb(indf: pd.DataFrame, tablename = "sms"):
    dbname = touchfilepath2depth(getdirmain() / "data" / "db" / f"phonecontact_{getdeviceid()}.db")
    checkphoneinfotable(dbname)
    conn = lite.connect(dbname)
    recordctdf = pd.read_sql(f"select * from {tablename}", con=conn)
    indf.to_sql(tablename, con=conn, if_exists="append", index=False)
    afterinsertctdf = pd.read_sql(f"select * from {tablename}", con=conn)
    conn.close()
    logstr = f"记录既有数量：\t{recordctdf.shape[0]}，" + f"待添加的记录数量为：\t{indf.shape[0]}，" + f"后的记录数量总计为：\t{afterinsertctdf.shape[0]}"
    log.info(logstr)


# %%
def splitcontentfromnote(noteguid: str):
    
    @trycounttimes2('evernote服务器')
    def gettitleandcontent(ntguid: str):
        ns = get_notestore()
        nttitle = ns.getNote(ntguid, False, False, False, False).title
        evernoteapijiayi()
        ntcontent = ns.getNoteContent(ntguid)
        evernoteapijiayi()
        
        return nttitle, ntcontent
    nstitle, notecontent = gettitleandcontent(noteguid)
    print(nstitle)
    nclines = BeautifulSoup(notecontent, 'lxml').find('en-note')
#     print(nclines.text)
    validlines = [line for line in nclines.text.split("\n") if len(line) > 0]
    log.info(f"有内容的行共有：\t{len(validlines)}")
    yuefentuple = "(?:(?:January|February|March|April|May|June|July|August|September|October|November|December)|(?:Jan|Feb|Mar|Apr|Aug|Sept|Oct|Nov|Dec))"
    # yuefentuple = "(January|February|March|April|May|June|July|August|September|October|November|December)"
    ptntimestr = f"{yuefentuple}" + "\s\d{2}, \d{4} at \d{2}:\d{2}[AP]M"
    ptntime = re.compile(ptntimestr, re.M)
    
    # Phone call placed to 林常德 8613975648088 Call length: 19 seconds April 26, 2014 at 10:31PM
    # November 11, 2014 at 10:53AM，Phone call placed to 罗峰 13647208959 Call length: 37 seconds 
    # 先处理这个再进入所谓常规流程
    ncphonecall = [line.strip() for line in nclines.text.split("\n") if re.findall("(Phone call)", line)]
    if len(ncphonecall) > 0:
        phonecalllststr = "\n".join(ncphonecall)
        pcsplitlst = ncphonecall[0].split(f"\s*Phone call placed to ")
        print(pcsplitlst)
        descpc = ("", pcsplitlst[0])[re.findall(ptntime, pcsplitlst[0]) is None]
        print(f"Phone call desc is :\t{descpc}")
        pclst = [[pd.to_datetime(re.findall(ptntime, item)[0])] + [initem.strip() for initem in some[0]] for item in ncphonecall if (some := re.findall("(\w*)?\s?(\d+) Call length: (.+)", re.sub(ptntime, "", re.sub("\s*Phone call placed to ", "", item))))]
        # [[Timestamp('2014-09-14 09:21:00'), '余晗', '18008623925', '29 seconds']]
        # columns=['sender', 'time', 'number', 'body', 'type', 'sent']
        pcdone = [[item[1], item[0], item[2], item[3], "call", True] for item in pclst]
    else:
        descpc = ""
        pcdone = []
    log.info(f"可以被拆分成有效（Phone call）条目：\t{len(pcdone)}")
        
    ncnormal = [line for line in nclines.text.split("\n") if not re.findall("Phone call", line)]
#     print(ncnormal)
    
    splitcontent = [line.strip() for line in re.split(ptntime, "\n".join(ncnormal))]
    descnormal = splitcontent[0]
    splittime = [pd.to_datetime(line) for line in re.findall(ptntime, "\n".join(ncnormal))]
    log.info(f"可以被拆分成有效（非Phone call）条目：\t{len(splittime)}")
    ptnwenbiao = re.compile("\W*(?:发来短信|短信发出|电话打给|电话来自|错过来电)", re.M)
    wenbiaolst = [line for line in zip(splittime, splitcontent[1:]) if re.findall(ptnwenbiao, line[1])]
    log.info(f"其中用短语分隔的有：\t{len(wenbiaolst)}")
    wenbiaobody = [([line[0]] + (re.split(ptnwenbiao, line[1].strip("， ,")))) for line in wenbiaolst]
    wenbiaotype = [re.findall(ptnwenbiao, line[1])[0].strip("， ,") for line in wenbiaolst]
    
    def detecttype(instr: str):
        if instr == '发来短信':
            return ['sms', False]
        elif instr == "短信发出":
            return ['sms', True]
        elif instr == "电话来自":
            return ['call', False]
        elif instr == "电话打给":
            return ['call', True]
        elif instr == "错过来电":
            return ['call', False]

    wenbiaotypesplit = [detecttype(line) for line in wenbiaotype]
    wenbiaoall = [[nstitle] +line[0] + list(line[1]) for line in zip(wenbiaobody, wenbiaotypesplit)]
    wenbiaosms = [line for line in wenbiaoall if line[-2] == 'sms']
    wenbiaocall = [line for line in wenbiaoall if line[-2] == 'call']
    print(wenbiaocall[:3])
    wenbiaocallformat = [[line[0], line[1], re.findall("\d+", line[3])[0], re.sub("^([\w\(\)（）]+\s\d+，?)", "", line[3]), line[4], line[5]] for line in wenbiaocall]
    wenbiaodone = wenbiaosms + wenbiaocallformat
    
    fubiaolst = [line for line in zip(splittime, splitcontent[1:]) if not re.findall(ptnwenbiao, line[1])]
    print(fubiaolst[:3])
    log.info(f"其中用符号分隔的有：\t{len(fubiaolst)}")
    fubiaothree = [[line[0]] + line[1].rsplit('，', 1) for line in fubiaolst]
    fubiaofinal = [[nstitle, pd.to_datetime(line[0]), line[2].split("||| ")[1], line[1].strip("："), "sms", False] for line in fubiaothree]

    def normalname(nameold, number, content):
        if nameold == "Mailed in note":
            return number
        ptnname = re.compile("(?:【(\w+)】$|^【(\w+)】|\[(\w+)\]$|^\[(\w+)\])")
        tiqu = [[x for x in item if len(x) > 0][0] for item in re.findall(ptnname, content) if (rst :=re.findall(ptnname, content) and len(item) > 0)]
        if content.startswith("【"):
            print(nameold, number, content)
            print(tiqu)
        if len(tiqu) == 0:
            return nameold
        else:
            return tiqu[-1]
    alllst = pcdone + wenbiaodone + fubiaofinal
    alldone = [[normalname(item[0], item[2], item[3]), item[1], item[2], item[3], item[4], item[5]] for item in alllst]
    smsnotedf = pd.DataFrame(alldone, columns=['name', 'time', 'number', 'content', 'type', 'sent'])
    smsnotedf['smsuuid'] = smsnotedf[['sent', 'number', 'time', 'content']].apply(lambda x: sha2hexstr(list(x.values)), axis=1)
    
    return [nstitle, descpc + descnormal], smsnotedf[['sent', 'name', 'number', 'time', 'content', 'smsuuid', 'type']].sort_values('time', ascending=False)


# %%
def smsfromnotes2smsdb(notebookguid: str):
    notelst = findnotefromnotebook(notebookguid)    
    for item in notelst:
        if not (guidchuli := getcfpoptionvalue('everpim', "noteguid", 'noteguid')):
            guidchulilst = []
        else:
            guidchulilst = guidchuli.split(',')
        if item[0] not in guidchulilst:
            log.info(item[0])
            desclst, smsnotedf = splitcontentfromnote(item[0])
            log.info(desclst)
            df2smsdb(pd.DataFrame([desclst], columns=['name', 'desc']), tablename='ctdesc')
            df2smsdb(smsnotedf)
            guidchulilst.append(item[0])
            setcfpoptionvalue('everpim', "noteguid", 'noteguid', ','.join(guidchulilst))


# %%
def splitcontentfromnotemysms(noteguid: str):
    
    @trycounttimes2('evernote服务器')
    def gettitleandcontent(ntguid: str):
        ns = get_notestore()
        nttitle = ns.getNote(ntguid, False, False, False, False).title
        evernoteapijiayi()
        ntcontent = ns.getNoteContent(ntguid)
        evernoteapijiayi()
        
        return nttitle, ntcontent
    nstitle, notecontent = gettitleandcontent(noteguid)
    titlesplitlst = nstitle.split(" ")
    name = titlesplitlst[0]
    number = titlesplitlst[1].replace("+86", "")
    print(name, number)
    nclines = BeautifulSoup(notecontent, 'lxml').find('en-note').find_all('div')
    tiqulst = [[(False, True)[re.findall("float:(left|right)", item.attrs['style'])[0] == 'right']] + [line.strip() for line in item.text.split(":", 1)] for item in nclines]
    ptntime = re.compile("\d+:\d+\s+[A|P]M, \d+/\d+/\d+")
    tiqudonelst = [[line[0], name, number, re.sub(ptntime, "", line[2]), pd.to_datetime(re.findall(ptntime, line[2])[0]), 'sms'] for line in tiqulst]

    smsnotedf = pd.DataFrame(tiqudonelst, columns=['sent', 'name', 'number', 'content', 'time', 'type'])
    smsnotedf['smsuuid'] = smsnotedf[['sent', 'number', 'time', 'content']].apply(lambda x: sha2hexstr(list(x.values)), axis=1)
    
    return [name], smsnotedf[['sent', 'name', 'number', 'time', 'content', 'smsuuid', 'type']].sort_values('time', ascending=False)


# %%
def mysmsfromnotes2smsdb(notebookguid: str):
    notelst = findnotefromnotebook(notebookguid)    
    for item in notelst:
        if not (guidchuli := getcfpoptionvalue('everpim', "notemysmsguid", 'noteguid')):
            guidchulilst = []
        else:
            guidchulilst = guidchuli.split(',')
        if item[0] not in guidchulilst:
            log.info(item[0])
            desclst, smsnotedf = splitcontentfromnotemysms(item[0])
            log.info(desclst)
            df2smsdb(smsnotedf)
            guidchulilst.append(item[0])
            setcfpoptionvalue('everpim', "notemysmsguid", 'noteguid', ','.join(guidchulilst))


# %%
def phonesms2db():
    """
    手机短信数据入库
    """
    if not (phonecontactdb := getcfpoptionvalue('everpim', str(getdeviceid()), 'smsfirstrun')):
        readnum = 50000
    else:
        readnum = 500
    smslst = termux_sms_list(num=readnum)
    smsdf = pd.DataFrame(smslst)
    smsdfclean = smsdf[smsdf.type != 'failed']
    ptn = re.compile("^\+86")
    smsdfclean['sent'] = smsdfclean['type'].apply(lambda x: True if x =='sent' else False)
    smsdfclean['number'] = smsdfclean['number'].apply(lambda x: re.sub(ptn, '', x))
    smsdfdone = smsdfclean[['sent', 'sender', 'number', 'received', 'body']]
    smsdfdone['smsuuid'] = smsdfdone.apply(lambda x: sha2hexstr(list(x.values)), axis=1)
    smsdfdone['type'] = 'sms'
    smsdfdone.columns = ['sent', 'name', 'number', 'time', 'content', 'smsuuid', 'type']
    
    df2smsdb(smsdfdone)
    if not (phonecontactdb := getcfpoptionvalue('everpim', str(getdeviceid()), 'smsfirstrun')):
        setcfpoptionvalue('everpim', str(getdeviceid()), 'smsfirstrun', str(True))


# %%
def phonecontact2db():
    """
    手机联系人数据入库
    """
    ctstr = termux_contact_list()
    ctlst = eval(ctstr)
    ctdf = pd.DataFrame(ctlst)
    ctdf['number'] = ctdf['number'].apply(lambda x: x.replace(" ", ''))
    ctdf.drop_duplicates('number', inplace=True)
    ctdf['appendtime'] = time.time()
    print(ctdf.shape[0])
    tablename = "phone"
    dbname = touchfilepath2depth(getdirmain() / "data" / "db" / f"phonecontact_{getdeviceid()}.db")
    checkphoneinfotable(dbname)
    conn = lite.connect(dbname)
    recordctdf = pd.read_sql(f"select * from {tablename}", con=conn)
    ctdf.to_sql(tablename, con=conn, if_exists="append", index=False)
    afterinsertctdf = pd.read_sql(f"select * from {tablename}", con=conn)
    conn.close()
    logstr = f"联系人记录既有数量：\t{recordctdf.shape[0]}，" + f"待添加的联系人记录数量为：\t{ctdf.shape[0]}，" + f"添加后的联系人记录数量总计为：\t{afterinsertctdf.shape[0]}"
    log.info(logstr)


# %%
def getphoneinfodb():
    """
    从联系人信息数据表提取数据（DataFrame）
    """
#     tablename = "wcdelaynew"
    dbname = touchfilepath2depth(getdirmain() / "data" / "db" / f"phonecontact_{getdeviceid()}.db")
    tablename="phone"
    checkphoneinfotable(dbname)

    conn = lite.connect(dbname)
    recordctdf = pd.read_sql(f"select * from {tablename}", con=conn)
    conn.close()
    
    recordctdf["appendtime"] = recordctdf["appendtime"].apply(
            lambda x: pd.to_datetime(time.strftime("%Y-%m-%d %H:%M:%S", 
                   time.localtime(x))))

    if (tdfsize := recordctdf.shape[0]) != 0:
        print(f"联系人记录共有{tdfsize}条")
        jujinmins = int((pd.to_datetime(time.ctime()) - recordctdf['appendtime'].max()).total_seconds() / 3600)
    else:
        jujinmins = 0
        logstr = f"数据表{tablename}还没有数据呢"
        log.info(logstr)

    print(recordctdf.iloc[-3:])

    return jujinmins, recordctdf


# %%
def showinfostream(keyin):
    pass


# %%
def showphoneinfoimg(jingdu: int = 300, showincell=False):
    '''
    show the img for phone info
    
    '''
    jujinm, ctdf = getphoneinfodb()
    print(f"记录新鲜度：刚过去了{jujinm}小时")

    register_matplotlib_converters()

    contactoutstr = f"目前联系人共有{ctdf.shape[0]}个，有效添加次数为：{ctdf.groupby('appendtime').count().shape[0]}，最近一次添加时间为：{ctdf['appendtime'].max()}。\n"

    dayrange = 30
    descbegintime = pd.to_datetime(time.ctime()) + pd.Timedelta(f'-{dayrange}d')

    contactoutstr += f"最近{dayrange}天添加的联系人如下(前20位）：\n"
    ctrecentstr = ctdf[ctdf.appendtime > descbegintime][-20:].to_string(justify='left', show_dimensions=True, index=False)
    contactoutstr += ctrecentstr

    return lststr2img(contactoutstr, title="手机联系人综合描述", showincell=showincell)


# %%
if __name__ == "__main__":
    logstrouter = "运行文件\t%s" %__file__
    log.info(logstrouter)
    phonecontact2db()
    phonesms2db()
#     smsnbguid = "25f718c1-cb76-47f6-bdd7-b7b5ee09e445"
#     smsfromnotes2smsdb(smsnbguid)
#     mysmsnbguid = "39625f3f-8ee7-486b-ab73-e6ca4f325be6"
#     mysmsfromnotes2smsdb(mysmsnbguid)
    xinxian, tdf = getphoneinfodb()
    print(xinxian)
    print(tdf.sort_index(ascending=False))
    logstrouter = "文件%s运行结束" %(__file__)
    log.info(logstrouter)
