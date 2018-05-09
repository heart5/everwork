# encoding:utf-8

from imp4nb import *


def readmail():
    import imaplib
    mailserver = imaplib.IMAP4_SSL('imap.gmail.com', 993)
    username = 'baiyefeng@gmail.com'
    password = 'zysm100080gg'
    mailserver.login(username, password)
    status, count = mailserver.select('Sent')
    print(status)
    print(count)
    status, data = mailserver.fetch(count[0], '(UID BODY[TEXT])')
    print(data[0][1])
    mailserver.close()
    mailserver.logout()


# readmail()


def parseHeader(message):
    """ 解析邮件首部 """
    # 时间
    date = email.utils.parsedate_to_datetime(message.get('date'))
    localdate = date.astimezone(datetime.timezone(datetime.timedelta(hours=8)))
    print('Date:', localdate)
    subject = message.get('subject')
    # 主题
    print(subject)
    subjectdecoded = email.header.make_header(email.header.decode_header(subject))
    print(subjectdecoded)
    # 发件人
    print('From:', email.utils.parseaddr(message.get('from'))[1])
    # 收件人
    # print(message.get('to'))
    print('To:', email.utils.parseaddr(message.get('to'))[1])
    # print('To:', message.get('to'))
    # 抄送人
    # print('Cc:', email.utils.parseaddr(message.get_all('cc'))[1])


def parseBody(message, msgencoding):
    """ 解析邮件/信体 """
    # 循环信件中的每一个mime的数据块
    for part in message.walk():
        # 这里要判断是否是multipart，是的话，里面的数据是一个message 列表
        if not part.is_multipart():
            charset = part.get_charset()
            print('charset: ', charset)
            contenttype = part.get_content_type()
            print('content-type', contenttype)
            name = part.get_param("name")  # 如果是附件，这里就会取出附件的文件名
            if name:
                # 有附件
                # 下面的三行代码只是为了解码象=?gbk?Q?=CF=E0=C6=AC.rar?=这样的文件名
                fh = email.header.Header(name)  # =?gb18030?B?tbyz9sr9vt0ueGxz?=
                print(fh)
                fdh = email.header.decode_header(fh)  # [(b'=?gb18030?B?tbyz9sr9vt0ueGxz?=', 'us-ascii')]
                print(fdh)
                fnamestr = fdh[0][0].decode(fdh[0][1])  # bytes to str with it's encoding
                fname = email.header.make_header(email.header.decode_header(fnamestr))  # Header类型的数据，内容为导出数据.xls
                fname = str(fname)  # 字符串格式的“导出数据.xls”
                # fname = fdh[0][0]
                # print('附件名:', fname)
                # print('附件名:', str(fname))
                # fname = str(email.header.make_header(email.header.decode_header(str(fname))))
                print('附件名:', fname)
                attach_data = part.get_payload(decode=True)  # 解码出附件数据，然后存储到文件中

                datamulu = 'data\\work\\'
                try:
                    f = open(datamulu + fname, 'wb')  # 注意一定要用wb来打开文件，因为附件一般都是二进制文件
                except Exception as e:
                    print(e)
                    print('附件名有非法字符，自动换一个')
                    f = open('aaaa', 'wb')
                f.write(attach_data)
                f.close()
            else:
                # 不是附件，是文本内容
                # print(bodytext)
                # print(part)
                partdecode = part.get_payload(decode=True)
                # print(partdecode)
                print(partdecode.decode(msgencoding))  # 解码出文本内容，直接输出来就可以了。
            # pass
            # print '+'*60 # 用来区别各个部分的输出


def getMail(host, username, password, port=993):
    try:
        serv = imaplib.IMAP4_SSL(host, port)
    except Exception as e:
        serv = imaplib.IMAP4(host, port)

    serv.login(username, password)
    # serv.debug = 4
    typ, dirs = serv.list()
    print(dirs)
    typ, dirs = serv.list(directory='study')
    print(dirs)
    print(serv.status('Work', '(messages)'))
    # print(serv.status('"[Gmail]/All Mail"','(messages)'))
    # print(serv.status('Ifttt/Notification','(UIDVALIDITY)'))
    # print(serv.status('Ifttt/SmsLog','(UIDNEXT)'))
    # print(serv.select('"&TgCCLH9RU8s-"'))
    print(serv.select('Work'))
    # 搜索邮件内容
    # typ, data = serv.search(None, '(TO "heart5.4ab86@m.evernote.com" subject "sms")' )
    # typ, data = serv.search(None, '(from "baiyefeng@gmail.com")' )
    # typ, data = serv.search(None, '(subject "%s" since "01-Jan-2017")' %zhuti)
    # typ, data = serv.search(None, '(unseen subject "Status")')
    zhuti = '导出'
    serv.literal = zhuti.encode('utf-8')
    # typ, data = serv.uid('SEARCH', 'CHARSET', 'UTF-8',  'Since','22-Jan-2018', 'text')
    # typ, data = serv.search('utf-8', 'Since','01-Feb-2018','text')
    typ, data = serv.search('utf-8', 'text')
    # typ, data = serv.search(None, 'text "Android"')
    # typ, data = serv.search(None, 'ALL')
    print(data)
    print(len(data[0].split()))

    count = 1
    pcount = 1
    for num in data[0].split()[::-1]:
        typ, data = serv.fetch(num, '(RFC822)')
        print(data)
        text = data[0][1]
        # text = text.replace('gb-2312','gb2312')
        message = email.message_from_bytes(text)  # 转换为email.message对象
        pattern = re.compile(r"(UTF-8)|(gb2312)|(gbk)|(gb18030)", re.I)
        subject = message.get('subject')
        # print(subject)
        # if not str(subject).find('sms'):
        #     break
        # print(subject)
        resultre = re.search(pattern, str(subject))
        if resultre:
            mailencodings = resultre.group()
        else:
            mailencodings = 'UTF-8'
        print(mailencodings)
        # print(message)
        parseHeader(message)
        parseBody(message, mailencodings)
        print()
        pcount += 1
        if pcount > count:
            break

    serv.close()
    serv.logout()


import imaplib
import email
from email.parser import Parser

if __name__ == '__main__':
    host = "imap.gmail.com"  # "pop.mail_serv.com"
    username = "baiyefeng@gmail.com"
    password = "zysm100080gg"
    getMail(host, username, password)
