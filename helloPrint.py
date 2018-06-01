#
# encoding:utf-8
#
"""
各种测试

"""

from imp4nb import *


def ttestprint():
    print('Hello')
    print('World')
    print('Hello')
    print('World')
    print('白', '晔', '峰')
    print('白', '晔', '峰')


def textspam():
    def spam(divideBy):
        try:
            return 42 / divideBy
        except ZeroDivisionError:
            print('Eror: Invalid argument')

    print(spam(3))
    print(spam(43))
    print(spam(1))
    print(spam(0))
    print(spam(9))


def textploterrorbar():
    # example data
    x = np.arange(0.1, 4, 0.5)
    y = np.exp(-x)

    fig, ax = plt.subplots()
    ax.errorbar(x, y, xerr=0.2, yerr=0.4)
    plt.show()

    print(plt.colors())


def ttesttimesplit():
    mailtext = b'Subject: =?UTF-8?B?U01TIHdpdGgg5pyx5bmz?=\r\nTo: =?UTF-8?B?5pyx5bmz?= <unknown_number@unknown.email>\r\nFrom: baiyefeng@gmail.com\r\nMIME-Version: 1.0\r\nContent-Type: text/plain;\r\n charset=utf-8\r\nContent-Transfer-Encoding: quoted-printable\r\nReferences: <ntmw1ushlemm96wkef557nqt.1454@sms-backup-plus.local>\r\nX-smssync-id: 1721\r\nX-smssync-address: +8618995645350\r\nX-smssync-type: 2\r\nX-smssync-date: 1.29247e+12\r\nX-smssync-thread: 212\r\nX-smssync-read: 1\r\nX-smssync-status: -1\r\nX-smssync-backup-time: 19 Dec 2010 15:54:36 GMT\r\nX-smssync-version: 111\r\n\r\n=E5=93=A5=E5=93=A5=E5=A5=BD=E3=80=82=E5=A4=A9=E5=86=B7=E6=B3=A8=E6=84=8F=E5=\r\n=8A=A0=E8=A1=A3=EF=BC=8C=E6=B3=A8=E6=84=8F=E5=AE=89=E5=85=A8=E3=80=82=E5=8F=\r\n=A6=EF=BC=8C=E9=82=A3=E4=B8=AA=E9=92=B1=E5=88=B0=E4=BD=8D=E6=B2=A1=E6=9C=89=\r\n=EF=BC=9F=E8=A6=81=E6=90=9E=E5=BF=AB=E7=82=B9=E5=93=A6=E3=80=82=E4=BC=A0=E6=\r\n=98=8E22=E6=97=A5=E5=9B=9E=EF=BC=8C=E5=88=AB=E6=90=9E=E7=9A=84=E4=BB=96=E5=\r\n=9B=9E=E6=9D=A5=E9=83=BD=E6=B2=A1=E6=8B=BF=E4=B8=8B=E6=89=A7=E7=85=A7=EF=BC=\r\n=8C=E9=82=A3=E5=B0=B1=E7=AC=91=E8=AF=9D=E4=BA=86=EF=BC=8C=E5=91=B5=E5=91=B5=\r\n=E3=80=82=E6=95=B4=E6=95=B4=E4=B8=A4=E4=B8=AA=E6=9C=88=E5=95=8A=EF=BC=81'

    pattern = re.compile(r'(?:X-smssync-backup-time: )(?P<date>\d{1,2} \w{3} \d{4} \d{2}:\d{2}:\d{2})', re.I)
    datetext = 'X-smssync-backup-time: 19 Dec 2010 15:54:36 GMT'

    items = re.split(pattern, datetext)
    print(items)
    for item in items:
        print(item)

    datetext = items[1]
    itemtime = time.strptime(datetext, '%d %b %Y %H:%M:%S')
    print(itemtime)

    print(time.mktime(itemtime))


def currentprocess():
    # fstream = os.popen('tasklist /fi "username ne NT authority\system"', 'r')
    fstream = os.popen('tasklist /fi "username ne NT authority\system" /fi "status eq running"', 'r')
    pattern = re.compile('(.*?)\s+(\d+)\s+(\w+?)\s+(\d+)\s+[0-9,]+\sK')
    items = []
    for line in fstream:
        splititems = re.split(pattern, line.strip())
        if len(splititems) == 6:
            items.append(splititems)
    print(items)
    prodf = pd.DataFrame(items, columns=['_', 'name', 'id', 'type', 'memory', 'p'])
    # print(prodf)
    prodf = prodf[['name', 'id', 'type', 'memory']]
    prodf['id'] = prodf['id'].astype(int)
    prodf.sort_values(['id'], ascending=False, inplace=True)
    prodf.sort_index(ascending=False, inplace=True)
    print(prodf)


if __name__ == '__main__':
    # ttesttimesplit()
    # currentprocess()
    token = cfp.get('evernote', 'token')
    findnotefromnotebook(token, 'c068e01f-1a7a-4e65-b8e4-ed93eed6bd0b', '进出')
