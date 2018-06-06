"""
4524187f-c131-4d7d-b6cc-a1af20474a7f notification 笔记本
4a940ff2-74a8-4584-be46-aa6d68a4fa53 everworklog 笔记

"""

from imp4nb import *


def log2notetimer(jiangemiao):
    pathlog = 'log'
    files = os.listdir(pathlog)
    loglines = []
    for fname in files[::-1]:
        with open(pathlog + '\\' + fname, 'r', encoding='utf-8') as flog:
            loglines = loglines + [line.strip() for line in flog if line.find('CRITICAL') >= 0]

    print(len(loglines), end='\t')
    # global cfp, inifilepath
    everlogc = int(cfp.get('evernote', 'everlogc'))
    if len(loglines) <= everlogc:
        print('%s\t无新记录，不更新everworklog笔记' % str(datetime.datetime.now()))
    else:
        print('有新的记录，执行更新')
        loglinestr = '\n'.join(loglines[::-1])
        loglinestr = loglinestr.replace('<', '《')
        loglinestr = loglinestr.replace('>', '》')
        loglinestr = loglinestr.replace('&', '并符')
        loglinestr = loglinestr.replace('=', '等于')
        loglinestr = '<pre>' + loglinestr + '</pre>'
        # print(loglinestr)

        noteguid_lognote = '4a940ff2-74a8-4584-be46-aa6d68a4fa53'
        try:
            imglist2note(get_notestore(), [], noteguid_lognote, 'everworklog', loglinestr)
            cfp.set('evernote', 'everlogc', '%d' % len(loglines))
            cfp.write(open(inifilepath, 'w', encoding='utf-8'))
            log.info('log信息成功更新入笔记，将于%d秒后再次自动检查并更新' % jiangemiao)
        except Exception as eeee:
            log.critical('处理log信息到笔记时出现未名错误。%s' % (str(eeee)))

    global timer_log2note
    timer_log2note = Timer(jiangemiao, log2notetimer, [jiangemiao])
    timer_log2note.start()


if __name__ == '__main__':
    token = cfp.get('evernote', 'token')
    log2notetimer(60 * 32)
