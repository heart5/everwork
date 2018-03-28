"""
4524187f-c131-4d7d-b6cc-a1af20474a7f notification 笔记本
4a940ff2-74a8-4584-be46-aa6d68a4fa53 everworklog 笔记

"""

from imp4nb import *


def log2notetimer(token, jiangemiao):
    loglines = []
    with open('log\\everwork.log', 'r', encoding='utf-8') as f:
        while True:
            line = f.readline()
            if len(line) == 0:
                break
            if line.find('CRITICAL') >= 0:
                # print(line, end='')
                loglines.append(line)
        loglinestr = ''.join(loglines[::-1])
        loglinestr = loglinestr.replace('<', '《')
        loglinestr = loglinestr.replace('>', '》')
        loglinestr = '<pre>' + loglinestr + '</pre>'
        f.close()
    # print(loglinestr)

    noteguid_lognote = '4a940ff2-74a8-4584-be46-aa6d68a4fa53'
    try:
        imglist2note(get_notestore(token), [], noteguid_lognote, 'everworklog', loglinestr)
        log.info('log信息成功更新入笔记，将于%d秒后再次自动检查并更新' % jiangemiao)
    except Exception as e:
        log.critical('处理log信息到笔记时出现未名错误。%s' % (str(e)))

    global timer_log2note
    timer_log2note = Timer(jiangemiao, log2notetimer, (token, jiangemiao))
    # print(timer_weather)
    timer_log2note.start()
