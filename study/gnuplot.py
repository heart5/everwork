# encoding:utf-8
"""
功能描述
"""

from func.logme import log

import numpy as np
import gnuplotlib as gp

x = np.linspace(-5, 5, 100)
print(x)

gp.plot(x, np.sin(x))

gp.plot((x, np.sin(x), {'with': 'boxes'}), (x, np.cos(x), {'legend': 'cosine'}),
        _with='lines',
        terminal='dumb 80,40',
        unset='grid')

if __name__ == '__main__':
    log.info(f'运行文件\t{__file__}')

    print('Done.完毕。')
