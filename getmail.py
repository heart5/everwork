# encoding:utf-8

from imp4nb import *
from bs4 import BeautifulSoup
import imaplib
import email


def parseHeader(message):
    mailmsg = []
    """ 解析邮件首部 """
    # 时间
    date = email.utils.parsedate_to_datetime(message.get('date'))
    localdate = date.astimezone(datetime.timezone(datetime.timedelta(hours=8)))
    # print('Date:', localdate)
    mailmsg.append(localdate)

    # 主题
    subject = message.get('subject')
    # print(subject)
    subjectdecoded = str(email.header.make_header(email.header.decode_header(subject)))
    # print(subjectdecoded)
    mailmsg.append(subjectdecoded)

    # 发件人
    mailfrom = email.utils.parseaddr(message.get('from'))[1]
    # print('From:', mailfrom)
    mailmsg.append(mailfrom)

    # 收件人
    # print(message.get('to'))
    mailto = email.utils.parseaddr(message.get('to'))[1]
    # print('To:', mailto)
    mailmsg.append(mailto)

    # print('To:', message.get('to'))
    # 抄送人
    # print('Cc:', email.utils.parseaddr(message.get_all('cc'))[1])

    return mailmsg


def parseBody(message, msgencoding):
    bodystr = []
    """ 解析邮件/信体 """
    # 循环信件中的每一个mime的数据块
    for part in message.walk():
        # 这里要判断是否是multipart，是的话，里面的数据是一个message 列表
        if not part.is_multipart():
            charset = part.get_charset()
            # print('charset: ', charset)
            contenttype = part.get_content_type()
            # print('content-type', contenttype)
            if not contenttype == 'text/plain':
                continue
            name = part.get_param("name")  # 如果是附件，这里就会取出附件的文件名
            if name:
                # 有附件
                # 下面的三行代码只是为了解码象=?gbk?Q?=CF=E0=C6=AC.rar?=这样的文件名
                fh = email.header.Header(name)
                fdh = email.header.decode_header(fh)
                fname = fdh[0][0]
                print('附件名:', fname)
                # attach_data = par.get_payload(decode=True) #　解码出附件数据，然后存储到文件中

                # try:
                #     f = open(fname, 'wb') #注意一定要用wb来打开文件，因为附件一般都是二进制文件
                # except:
                #     print '附件名有非法字符，自动换一个'
                #     f = open('aaaa', 'wb')
                # f.write(attach_data)
                # f.close()
            else:
                # 不是附件，是文本内容
                # print(bodytext)
                # print(part)
                partdecode = part.get_payload(decode=True)
                # print(partdecode)
                bodystr = partdecode.decode(msgencoding)
                # 处理html标记符，并去除换行符\r\n等
                bodystr = BeautifulSoup(bodystr, "html.parser"). \
                    get_text().replace('\r', '').replace('\n', '')
                # print(bodystr) # 解码出文本内容，直接输出来就可以了。

            # pass
            # print '+'*60 # 用来区别各个部分的输出

    return bodystr


def getMail(host, username, password, port=993, mailnum=10000):
    try:
        serv = imaplib.IMAP4_SSL(host, port)
    except Exception as e:
        serv = imaplib.IMAP4(host, port)

    serv.login(username, password)
    print(serv.status('Ifttt/Weather', '(unseen)'))
    print(serv.select('Ifttt/Weather'))
    zhuti = '武汉每日天气 @行政管理 +'
    serv.literal = zhuti.encode('utf-8')
    typ, data = serv.search('utf-8', 'unseen', 'text')
    # typ, data = serv.search('utf-8','text')
    print(data)
    print(len(data[0].split()))

    pcount = 1
    mailmsglist = []
    for num in data[0].split():
        typ, data = serv.fetch(num, '(RFC822)')
        # print(data)
        text = data[0][1]
        # text = text.replace('gb-2312','gb2312')
        message = email.message_from_bytes(text)  # 转换为email.message对象
        pattern = re.compile(r"(UTF-8)|(gb2312)|(gbk)|(gb18030)", re.I)
        subject = message.get('subject')
        resultre = re.search(pattern, str(subject))
        if resultre:
            mailencodings = resultre.group()
        else:
            mailencodings = 'UTF-8'
        # print(mailencodings)
        # print(message)
        header = parseHeader(message)
        mailitem = header
        body = parseBody(message, mailencodings)
        mailitem.append(body)
        # print(mailitem)
        mailmsglist.append(body)

        pcount += 1
        if pcount > mailnum:
            break

    serv.close()
    serv.logout()

    return mailmsglist


if __name__ == '__main__':
    host = cfp.get('gmail', 'host')
    username = cfp.get('gmail', 'username')
    password = cfp.get('gmail', 'password')
    maillist = getMail(host, username, password, mailnum=20)
    print(maillist)
