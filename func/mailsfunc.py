# encoding:utf-8
"""
功能描述
"""
import datetime
import email
import imaplib
import os
import re
import socket
import threading
from bs4 import BeautifulSoup

import pathmagic

with pathmagic.context():
    from func.configpr import cfp, getcfpoptionvalue, setcfpoptionvalue
    from func.first import dirmainpath, getdirmain
    from func.logme import log
    from func.datatools import getfilepathnameext
    from func.nettools import trycounttimes2
    from func.evernttest import timestamp2str, imglist2note, note_store, getinivaluefromnote
    from etc.getid import getdeviceid
    from etc.mailfun import mailfun
    from func.termuxtools import termux_sms_send


def getmail(hostmail, usernamemail, passwordmail, port=993, debug=False, mailnum=100000, dirtarget='Inbox',
            unseen=False,
            topicloc='subject', topic='', datadir=os.path.join(getdirmain(), 'data', 'work')):

    def parseheader(message):
        headermsg = []

        """ 解析邮件首部 """
        # 发件人
        # mailfrom = email.utils.parseaddr(message.get('from'))[1]
        # print('From:', mailfrom)

        # 时间
        datestr = message.get('date')
        if datestr is None:
            log.error('从邮件头部提取时间失败，只好从邮件内容中寻找时间信息。')
            pattern = re.compile(r'(?:X-smssync-backup-time: )(?P<date>\d{1,2} \w{3} \d{4} \d{2}:\d{2}:\d{2})', re.I)
            items = re.split(pattern, str(message))
            if len(items) > 1:
                print(items[1])
                datemail = datetime.datetime.strptime(items[1], '%d %b %Y %H:%M:%S')
            else:
                log.critical("从邮件内容中也没有找到有效的时间信息。")
                datemail = None
                # print(message)
        else:
            datemail = email.utils.parsedate_to_datetime(message.get('date'))

        localdate = datemail.astimezone(datetime.timezone(datetime.timedelta(hours=8)))
        # print('Date:', localdate)
        headermsg.append(localdate)
        # if mailfrom.startswith('baiyefeng@gmail.com'):
        #     headermsg.append(str(localdate) + '\t发出\t')
        # else:
        #     headermsg.append(str(localdate) + '\t收到\t')

        # 主题
        subject = message.get('subject')
        # print(subject)
        subjectdecoded = str(email.header.make_header(email.header.decode_header(subject)))
        # print(subjectdecoded)
        headermsg.append(subjectdecoded)

        # 发件人
        mailfrom = email.utils.parseaddr(message.get('from'))[1]
        # print('From:', mailfrom)
        headermsg.append(mailfrom)

        # 收件人
        # print(message.get('to'))
        mailto = email.utils.parseaddr(message.get('to'))[1]
        # print('To:', mailto)
        headermsg.append(mailto)
        # print('To:', message.get('to'))
        # 抄送人
        # print('Cc:', email.utils.parseaddr(message.get_all('cc'))[1])

        return headermsg

    def parsebody(message, msgencoding):
        bodymsg = []
        """ 解析邮件/信体 """
        # 循环信件中的每一个mime的数据块
        for part in message.walk():
            partitem = []
            # 这里要判断是否是multipart，是的话，里面的数据是一个message 列表
            if not part.is_multipart():
                # charset = part.get_charset()
                # print('charset: ', charset)
                contenttype = part.get_content_type()
                # print('content-type', contenttype)
                namepart = part.get_param("name")  # 如果是附件，这里就会取出附件的文件名
                if namepart:
                    # 有附件
                    # 下面的三行代码只是为了解码象=?gbk?Q?=CF=E0=C6=AC.rar?=这样的文件名
                    fh = email.header.Header(namepart)  # =?gb18030?B?tbyz9sr9vt0ueGxz?=
                    # print(fh)
                    fdh = email.header.decode_header(fh)  # [(b'=?gb18030?B?tbyz9sr9vt0ueGxz?=', 'us-ascii')]
                    # print(fdh)
                    fnamestr = fdh[0][0].decode(fdh[0][1])  # bytes to str with it's encoding
                    fname = email.header.make_header(email.header.decode_header(fnamestr))  # Header类型的数据，内容为“导出数据.xls”
                    fname = str(fname)  # 字符串格式的“导出数据.xls”
                    log.info('附件名:', fname)
                    attach_data = part.get_payload(decode=True)  # 解码出附件数据，然后存储到文件中

                    pointat = fname.rfind('.')
                    timenowstr = datetime.datetime.now().strftime('__%Y%m%d%H%M%S_%f')
                    datadiri = datadir
                    if fname.startswith('销售订单'):
                        # print(fname)
                        datadiri = os.path.join(datadiri, '销售订单')
                    elif fname.startswith('订单明细'):
                        # print(fname)
                        datadiri = os.path.join(datadiri, '订单明细')

                    attachfile = os.path.join(datadiri, fname[:pointat] + timenowstr + fname[pointat:])
                    try:
                        fattach = open(attachfile, 'wb')  # 注意一定要用wb来打开文件，因为附件一般都是二进制文件
                    except Exception as eeee:
                        print(eeee)
                        attachfile = os.path.join(datadiri, '未名文件' + timenowstr)
                        fattach = open(attachfile, 'wb')
                    fattach.write(attach_data)
                    fattach.close()
                    partitem.append('attach')
                    partitem.append(attachfile)
                else:
                    # 不是附件，是文本内容
                    # print(part)
                    if not contenttype == 'text/plain':  # 只要plain文本部分
                        continue
                    partdecode = part.get_payload(decode=True)
                    # print(partdecode)
                    bodystr = partdecode.decode(msgencoding)  # 解码出文本内容
                    # print(bodystr)
                    bodystr = BeautifulSoup(bodystr, "html.parser"). \
                        get_text().replace('\r', '').replace('\n', '').replace('\t', '')  # 文本化后去掉回车、换行符等
                    # print(bodystr)
                    partitem.append('text')
                    partitem.append(bodystr)
                # pass
                # print '+'*60 # 用来区别各个部分的输出
            if len(partitem) > 0:
                bodymsg.append(partitem)

        return bodymsg

    @trycounttimes2(f'{hostmail}邮箱服务器')
    def getservmail():
        servmail = imaplib.IMAP4_SSL(hostmail, port)
        servmail.login(usernamemail, passwordmail)
        log.info(f'成功登陆到邮箱：{hostmail}。{servmail}')
        return servmail

    serv = getservmail()

    # if debug:
    #     serv.debug = 4
    if debug:
        typ, dirs = serv.list()
        # print(dirs)
        for itemdirs in dirs:
            print(itemdirs.decode('ascii').split(') \"/\" \"')[1][:-1], end='\t')
        print()
    typ, dirs = serv.list(directory=dirtarget)
    # print(dirs)
    if unseen:
        statutuplestr = '(unseen)'
    else:
        statutuplestr = '(messages)'
    # print(statutuplestr)
    # print(serv.status(dirtarget,statutuplestr))
    # print(serv.status('"[Gmail]/All Mail"','(messages)'))
    # print(serv.status('Ifttt/Notification','(UIDVALIDITY)'))
    # print(serv.status('Ifttt/SmsLog','(UIDNEXT)'))
    # print(serv.select('"&TgCCLH9RU8s-"'))
    mailstatus = list()
    typess, data = serv.select(dirtarget)
    mailstatus.append(int(data[0].decode('ascii')))
    if len(topic) > 0:
        # 搜索邮件内容
        # typ, data = serv.search(None, '(TO "heart5.4ab86@m.evernote.com" subject "sms")' )
        # typ, data = serv.search(None, '(from "baiyefeng@gmail.com")' )
        # typ, data = serv.search(None, '(subject "%s" since "01-Jan-2017")' %zhuti)
        # typ, data = serv.search(None, '(unseen subject "Status")')
        zhuti = topic
        serv.literal = zhuti.encode('utf-8')
        # typ, data = serv.uid('SEARCH', 'CHARSET', 'UTF-8',  'Since','22-Jan-2018', 'text')
        # typ, data = serv.search('utf-8', 'Since','01-Feb-2018','text')
        if unseen:
            typ, data = serv.search('utf-8', 'unseen', topicloc)
        else:
            typ, data = serv.search('utf-8', topicloc)

        # typ, data = serv.search(None, 'text "Android"')
    else:
        if unseen:
            typ, data = serv.search(None, 'unseen')
        else:
            typ, data = serv.search(None, 'ALL')

    serv.close()
    serv.logout()

    mailstatus.append(len(data[0].split()))
    if debug:
        print(data[0].decode('ascii').split()[::-1])
        print(mailstatus)

    numlist = data[0].decode('ascii').split()[::-1]

    if len(numlist) == 0:  # 无新邮件则返回False
        newstr = '新' if unseen else ''
        topicstr = '主题为“%s”的' % topic if len(topic) > 0 else ''
        log.info('邮箱目录《%s》中没有%s%s邮件' % (dirtarget, topicstr, newstr))
        return False

    if len(numlist) > mailnum:
        numlist = numlist[:mailnum]

    def getnummail(numlistinside, mailitemsinside):
        countstart = len(mailitemsinside)
        counttarget = len(numlistinside)
        log.info('已有%d封邮件，准备处理%d封邮件……' % (countstart, counttarget))

        servinner = getservmail()
        type, data = servinner.select(dirtarget)

        count = 0
        totalcount = 0
        for num in numlistinside:
            # print(num)
            if (totalcount - count) >= 20:
                log.critical('无法正确处理的邮件超过%d封，此邮件编码列表跳过正常处理流程。%s' % (totalcount - count, numlistinside))
                log.info('实际处理邮件%d封，该邮件编码列表总数量为%d。' % (count, len(numlistinside)))
                return numlistinside

            totalcount += 1
            mailitem = []
            message = None
            try:
                typ, data = servinner.fetch(num, '(RFC822)')
                # print(data)
                text = data[0][1]
                # text = text.replace('gb-2312','gb2312')
                message = email.message_from_bytes(text)  # 转换为email.message对象
                # print(message)
                pattern = re.compile(r"(UTF-8)|(gb2312)|(gbk)|(gb18030)|(cp936)", re.I)
                subject = message.get('subject')
                resultre = re.search(pattern, str(subject))
                if resultre:
                    mailencodings = resultre.group()
                    if mailencodings.lower().startswith('gb'):  # gb18030是最大的字符集，向下兼容gb2312和gbk
                        mailencodings = 'gb18030'
                else:
                    mailencodings = 'UTF-8'
                # print(mailencodings)
                # print(message)
                mailitem.append(parseheader(message))
                mailitem.append(parsebody(message, mailencodings))
                # print(mailitem)
                mailitemsinside.append(mailitem)
                count = count + 1
            except ConnectionAbortedError as cae:
                log.critical("获取邮件[%s,%d/%d]时出现ConnectionAbortedError错误。%s" % (num, count, totalcount, str(cae)))
            except OSError as ose:
                if ose.errno == 10053:
                    log.critical("获取邮件[%s,%d/%d]时出现操作系统错误，和服务器的连接被强行终止。%s" % (num, count, totalcount, str(ose)))
                else:
                    log.critical("获取邮件[%s,%d/%d]时出现操作系统错误。%s" % (num, count, totalcount, str(ose)))
            except imaplib.IMAP4.error as iie:
                log.critical("获取邮件[%s,%d/%d]时出现imaplib.IMAP4.error错误。%s" % (num, count, totalcount, str(iie)))
            except imaplib.IMAP4.abort as iia:
                log.critical(
                    "获取邮件[%s,%d/%d]时出现imaplib.IMAP4.abort错误，和服务器的连接被强行终止。%s" % (num, count, totalcount, str(iia)))
            except UnicodeDecodeError as ude:
                log.critical("处理邮件[%s,%d/%d]内容时出现UnicodeDecodeError错误。%s" % (num, count, totalcount, str(ude)))
            except AttributeError as abe:
                log.critical("处理邮件[%s,%d/%d]时出现AttributeError错误。%s" % (num, count, totalcount, str(abe)))
            except TypeError as te:
                log.critical("处理邮件[%s,%d/%d]时出现TypeError错误。%s" % (num, count, totalcount, str(te)))
                print(message)
            except Exception as eeefetch:
                log.critical("处理邮件[%s,%d/%d]时出现未名错误。%s" % (num, count, totalcount, str(eeefetch)))
            finally:
                log.info(f"邮件编码列表：{numlistinside}")
                log.info(f"邮件主题列表：{mailitemsinside}")

        servinner.close()
        servinner.logout()
        log.info('实际处理邮件%d封，该邮件编码列表总数量为%d。' % (count, len(numlistinside)))

    mailitemsresult = list()
    kelidu = 200
    fenjie = int((len(numlist)) / kelidu)
    threadlist = []
    for i in range(fenjie + 1):
        inputnumlist = numlist[(i * kelidu):(i + 1) * kelidu]
        # print(inputnumlist)
        t = threading.Thread(target=getnummail, args=(inputnumlist, mailitemsresult,))
        threadlist.append(t)

    log.info('处理邮箱目录%s，共计有%d个线程准备运行。' % (dirtarget, len(threadlist)))
    threadnum = 8
    threadzushu = int(len(threadlist) / threadnum)
    for i in range(threadzushu + 1):
        threadxiaozu = threadlist[(i * threadnum):(i + 1) * threadnum]
        # if i > 0:
        #     break
        # threadxiaozu = threadlist[140:141]
        log.info('此批次启动%d个线程：' % len(threadxiaozu))
        for t in threadxiaozu:
            t.start()
        # log.info('%d个线程全部启动……' % len(threadxiaozu))
        for t in threadxiaozu:
            t.join()
        log.info('累积有[%d/%d]个线程执行完毕。' % (i * threadnum + len(threadxiaozu), len(threadlist)))
    log.info('总计的%d个线程全部执行完毕！' % len(threadlist))

    return mailitemsresult


def jilugmail(direc, mingmu, fenleistr='', topic='', bodyonly=True):
    """
    从指定邮件目录读取包含关键字的新邮件并更新至txt文件
    :param direc: 待处理的邮件目录
    :param mingmu: 名目，txt文件命名使用
    :param fenleistr: 分类，txt文件命名使用
    :param topic: 搜索邮件的关键字，默认置空
    :param bodyonly: 只要邮件body，默认为真
    :return: 带换行的规范字符串列表
    """

    def readfromtxt(fn):
        if not os.path.exists(fn):
            newfile = open(fn, 'w', encoding='utf-8')
            newfile.close()
        with open(fn, 'r', encoding='utf-8') as fff:
            itemsr = [line.strip() for line in fff if len(line.strip()) > 0]
            # for line in f:
            #     print(line)
        log.info("《%s-%s》现有%d条记录。" % (mingmu, fenleistr, len(itemsr)))
        return itemsr

    hostg = cfp.get('gmail', 'host')
    usernameg = cfp.get('gmail', 'username')
    passwordg = cfp.get('gmail', 'password')
    mailitemsjilu = []
    try:
        mailitemsjilu = getmail(hostg, usernameg, passwordg, debug=False, dirtarget=direc, unseen=True, topic=topic)
    except socket.error as se:
        log.critical("构建socket连接时出错。%s" % str(se))
        return
    except Exception as e:
        log.critical('处理邮件时出现严重错误。%s' % str(e))
        return

    itemslst = []
    if mailitemsjilu is False:
        log.info('%s-%s没有新的邮件记录' % (mingmu, fenleistr))
    else:
        for headerjilu, bodyjilu in mailitemsjilu:
            for textjilu, textstrjilu in bodyjilu:
                if textjilu.startswith('text'):  # 只取用纯文本部分
                    if bodyonly:  # 只要邮件body文本，否则增加邮件标题部分内容
                        itemslst.append(textstrjilu)
                    elif headerjilu[1].startswith('SMS with') or headerjilu[1].endswith('的短信记录') \
                            or headerjilu[1].endswith('的通话记录'):  # 对特别记录增补时间戳
                        itemslst.append(headerjilu[1] + '\t' + str(headerjilu[0]) + '，' + textstrjilu)
                    else:
                        itemslst.append(headerjilu[1] + '\t' + textstrjilu)

    txtfilename = str(dirmainpath / 'data' / 'ifttt' / f'{mingmu}_gmail_{fenleistr}.txt')
    if len(itemslst) > 0:  # or True:
        items = itemslst + readfromtxt(txtfilename)
        fb = open(txtfilename, 'w', encoding='utf-8')
        for item in items:
            fb.write(item + '\n')
        fb.close()
    else:
        items = readfromtxt(txtfilename)
    log.info("《%s-%s》共有%d条记录。" % (mingmu, fenleistr, len(items)))
    return items


def findnewthenupdatenote(qrfile, cfpfile, cfpsection, pre, desc, sendsms=False):
    qrfile = os.path.abspath(qrfile)
    if os.path.exists(qrfile):
        # print(qrfile)
        # print(os.path.abspath(qrfile))
        qrfiletimeini = getcfpoptionvalue(cfpfile, cfpsection, f'{pre}filetime') 
        qrfilesecsnew = os.stat(qrfile).st_mtime
        qrfiletimenew = str(qrfilesecsnew)
        if qrfiletimeini: # or True:
            qrftlst = qrfiletimeini.split(',')
            print(f"{timestamp2str(float(qrftlst[0]))}\t{qrfile}")
            if (qrfiletimenew > qrftlst[0]): # or True:
                (*full, ext) = getfilepathnameext(qrfile)
                # print(full)
                # print(ext)
                ext = ext.lower()
                targetimglst = []
                filecontent = str(qrfile)
                if ext in ['.png', '.jpg', 'bmp', 'gif']:
                    targetimglst = [qrfile]
                else:
                    filecontent = open(qrfile, 'r').read()
                qrtstr = f"{qrfiletimenew},{qrfiletimeini}"
                qrtstrlst = qrtstr.split(',')
                qrtstrflst = [timestamp2str(float(x)) for x in qrtstrlst]
                targetstr = f'<pre>{filecontent}</pre><pre>--------------\n'+'\n'.join(qrtstrflst)+'</pre>'
                qrnoteguid = getinivaluefromnote(cfpsection, f"{pre}{getdeviceid()}")
                # print(targetimglst)
                # print(targetstr)
                imglist2note(note_store, targetimglst, qrnoteguid,
                             f"{getinivaluefromnote('device', getdeviceid())} {desc}", targetstr)
                mailfun(qrfile)
                if sendsms:
                    termux_sms_send(f"{desc}\t有新的更新，请尽快处置。")
                setcfpoptionvalue(cfpfile, cfpsection, f'{pre}filetime', qrtstr)
        else:
            mailfun(qrfile, True)
            setcfpoptionvalue(cfpfile, cfpsection, f'{pre}filetime',qrfiletimenew)
    else:
        log.critical(f"{qrfile}不存在，请检查文件名称")


if __name__ == '__main__':
    # log.info(f'运行文件\t{__file__}')
    # fl = 'QR.png'
    # qrfile = getdirmain() / fl
    # findnewthenupdatenote(qrfile, 'everwebchat', 'webchat', 'qr', 'QR微信二维码')

    cronfile = '/data/data/com.termux/files/usr/var/spool/cron/crontabs/u0_a133'
    findnewthenupdatenote(cronfile, 'everwork', 'everwork', 'cron',
                          'cron自动运行排期表')
    # log.info(f"文件\t{__file__}\t运行结束。")
