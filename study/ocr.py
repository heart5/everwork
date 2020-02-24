# encoding:utf-8
"""
图片中中文字符的识别
"""
import pathmagic

with pathmagic.context():
    from func.logme import log

import requests
from aip import AipOcr

image = requests.get('https://res.pandateacher.com/python_classic.png').content

APP_ID = '16149264'
API_KEY = 'yxYg9r4OuAs4fYvfcl8tqCYd'
SECRET_KEY = 'yWg3KMds2muFsWs7MBSSFcgMQl8Wng4s'
client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
res = client.basicGeneral(image)
if 'words_result' in res.keys():
    for item in res['words_result']:
        print(item['words'])

else:
    APP_ID = '11756541'
    API_KEY = '2YhkLuyQGljPUYnmi1CFgxOP'
    SECRET_KEY = '4rrHe2BF828bI8bQy6bLlx1MelXqa8Z7'
    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    res = client.basicGeneral(image)
    if 'words_result' in res.keys():
        for item in res['words_result']:
            print(item['words'])
    else:
        print(res)

if __name__ == '__main__':
    log.info(f'运行文件\t{__file__}')

    log.info(f'文件{__file__}运行结束')
