import pathmagic

with pathmagic.context():
    from func.logme import log
    from func.gmailfetch import getworknewmail

if __name__ == '__main__':
    log.info(f'运行文件\t{__file__}')
    # fetchworkfile_from_gmail('')
    getworknewmail()
    log.info(f'文件{__file__}运行结束！')
