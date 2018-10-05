# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext_format_version: '1.3'
#   jupytext_formats: py:light
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
#   language_info:
#     codemirror_mode:
#       name: ipython
#       version: 3
#     file_extension: .py
#     mimetype: text/x-python
#     name: python
#     nbconvert_exporter: python
#     pygments_lexer: ipython3
#     version: 3.6.6
#   widgets:
#     application/vnd.jupyter.widget-state+json:
#       state: {}
#       version_major: 2
#       version_minor: 0
# ---

# +
from pathlib import Path

directory = Path("/etc")
filepath = directory / "hosts" / 'home'
print(filepath)

if filepath.exists():
    print('hosts exist')
else:
    print('not exists')

# +
# 更好的方法，使用 yield from
def dup(n):
    for i in range(n):
        yield from [i, i]
        
cf = dup(5)
print(cf)

# +
import requests
from bs4 import BeautifulSoup
r = requests.get('http://www.wise.xmu.edu.cn/people/faculty')
html = r.content

soup = BeautifulSoup(html,'html.parser')    #html.parser是解析器
div_people_list = soup.find('div', attrs={'class': 'people_list'})
a_s = div_people_list.find_all('a', attrs={'target': '_blank'})
for a in a_s:
    url = a['href']
    name = a.get_text()
    print(f'{name},{url}')

# -

import sys
print(sys.path)


