# encoding:utf-8
"""
功能描述
"""
import time
from func.logme import log
import requests
from bs4 import BeautifulSoup


def trycounttimes(jutifunc, returnresult=False, servname='服务器'):
    trytimes = 3
    sleeptime = 15
    for i in range(trytimes):
        try:
            if returnresult:
                result = jutifunc()
                return result
            else:
                jutifunc()
            break
        except (WindowsError, ConnectionRefusedError, ConnectionError) as eee:
            if eee.errno == 11001:
                log.critical(f'寻址失败，貌似网络不通。{eee}')
            elif eee.errno == 10061:
                log.critical(f'被主动拒绝，好没面啊！{eee}')
            elif eee.errno == 10060:
                log.critical(f'够不着啊，是不是在墙外？！{eee}')
            elif eee.errno == 10054:
                log.critical(f'主机发脾气，强行断线了。{eee}')
            elif eee.errno == 8:
                log.critical(f'和evernote服务器握手失败。{eee}')
            else:
                log.critical(f'连接失败。{eee}')
            log.critical(f"第{i+1}次（最多尝试{trytimes}次）连接“{servname}”时失败，将于{sleeptime}秒后重试。")
            # log.critical(f'{eee.args}\t{eee.errno}\t{eee.filename}\t{eee.filename2}\t{eee.strerror}\t{eee.winerror}')
            if i == (trytimes - 1):
                log.critical(f'“{servname}”连接失败，只好无功而返。')
                # raise eee
            time.sleep(sleeptime)


if __name__ == '__main__':
    log.info(f'测试文件\t{__file__}')


    def fetchfromnet():
        r = requests.get('http://www.wise1.xmu.edu.cn/people/faculty')
        html = r.content
        return html


    html2 = trycounttimes(fetchfromnet, True, 'xmu.edu.cn网站服务器')
    soup = BeautifulSoup(html2, 'html.parser')  # html.parser是解析器
    div_people_list = soup.find('div', attrs={'class': 'people_list'})
    a_s = div_people_list.find_all('a', attrs={'target': '_blank'})
    for a in a_s:
        url = a['href']
        name = a.get_text()
        print(f'{name},{url}')

    print('Done.测试完毕。')
