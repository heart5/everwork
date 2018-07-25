# encoding:utf-8
"""
印象笔记相关功能函数
"""

import time, hashlib, binascii, \
    evernote.edam.type.ttypes as Ttypes, evernote.edam.error.ttypes as Etypes, \
    evernote.edam.userstore.constants as UserStoreConstants, \
    evernote.edam.notestore.NoteStore as NoteStore
from evernote.api.client import EvernoteClient
from func.configpr import getcfp
from func.logme import log


def get_notestore():
    # Real applications authenticate with Evernote using OAuth, but for the
    # purpose of exploring the API, you can get a developer token that allows
    # you to access your own Evernote account. To get a developer token, visit
    # https://SERVICE_HOST/api/DeveloperToken.action
    #
    # There are three Evernote services:
    #
    # Sandbox: https://sandbox.evernote.com/
    # Production (International): https://www.evernote.com/
    # Production (China): https://app.yinxiang.com/
    #
    # For more information about Sandbox and Evernote China services, please
    # refer to https://dev.evernote.com/doc/articles/testing.php
    # and https://dev.evernote.com/doc/articles/bootstrap.php

    global log
    # auth_token = token
    auth_token = getcfp('everwork').get('evernote', 'token')  # 直接提取，唯一使用

    if auth_token == "your developer token":
        print("Please fill in your developer token\nTo get a developer token, visit "
              "https://sandbox.evernote.com/api/DeveloperToken.action")
        log.critical('请填入从evernote官方网站申请的有效token！程序终止并退出！！！')
        exit(1)

    # To access Sandbox service, set sandbox to True
    # To access production (International) service, set both sandbox and china to False
    # To access production (China) service, set sandbox to False and china to True
    sandbox = False
    china = False

    # Initial development is performed on our sandbox server. To use the production
    # service, change sandbox=False and replace your
    # developer token above with a token from
    # https://www.evernote.com/api/DeveloperToken.action

    client = EvernoteClient(token=auth_token, sandbox=sandbox, china=china)

    trytimes = 3
    sleeptime = 20
    for i in range(trytimes):
        try:
            userstore = client.get_user_store()
            # evernoteapijiayi()
            version_ok = userstore.checkVersion(
                "Evernote EDAMTest (Python)",
                UserStoreConstants.EDAM_VERSION_MAJOR,
                UserStoreConstants.EDAM_VERSION_MINOR
            )
            if not version_ok:
                log.critical('Evernote API版本过时，请更新之！程序终止并退出！！！')
                exit(1)
            # print("Is my Evernote API version up to date? ", str(version_ok))
            note_store = client.get_note_store()
            # evernoteapijiayi()
            log.debug('成功连接Evernote服务器！构建notestore：%s' % note_store)
            return note_store
        except Exception as eee:
            log.critical("第%d次（最多尝试%d次）连接evernote服务器时失败，将于%d秒后重试。%s"
                         % (i + 1, trytimes, sleeptime, eee))
            if i == (trytimes - 1):
                log.critical('evernote服务器连接失败，只好无功而返。')
                raise eee
            time.sleep(sleeptime)


def imglist2note(notestore, imglist, noteguid, notetitle, neirong=''):
    """
    更新note内容为图片列表
    :param notestore:
    :param imglist:
    :param noteguid:
    :param notetitle:
    :param neirong:object
    :return:
    """
    global log
    note = Ttypes.Note()
    # print(type(note))
    note.guid = noteguid
    note.title = notetitle

    # To include an attachment such as an image in a note, first create a Resource
    # for the attachment. At a minimum, the Resource contains the binary attachment
    # data, an MD5 hash of the binary data, and the attachment MIME type.
    # It can also include attributes such as filename and location.

    # Now, add the new Resource to the note's list of resources
    # print(len(note.resources))
    # print(noteguid)
    # note.resources = notestore.getNote(token, noteguid, True, True, True,True).resources
    # evernoteapijiayi()
    # if not note.resources:
    #     note.resources = []

    note.resources = []
    # print(len(note.resources))
    # for img, imgtitle in imglist:
    for img in imglist:
        image = open(img, 'rb').read()
        md5 = hashlib.md5()
        md5.update(image)
        imghash = md5.digest()
        data = Ttypes.Data()  # 必须要重新构建一个Data（），否则内容不会变化
        data.size = len(image)
        data.bodyHash = imghash
        data.body = image
        resource = Ttypes.Resource()
        resource.mime = 'image/png'
        resource.data = data
        note.resources.append(resource)

    # The content of an Evernote note is represented using Evernote Markup Language
    # (ENML). The full ENML specification can be found in the Evernote API Overview
    # at http://dev.evernote.com/documentation/cloud/chapters/ENML.php
    nbody = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
    nbody += "<!DOCTYPE en-note SYSTEM \"http://xml.evernote.com/pub/enml2.dtd\">"
    nbody += "<en-note>"
    if note.resources:
        # To display the Resource as part of the note's content, include an <en-media>
        # tag in the note's ENML content. The en-media tag identifies the corresponding
        # Resource using the MD5 hash.
        # nBody += "<br />" * 2
        for resource in note.resources:
            if resource.guid or True:
                hexhash = binascii.hexlify(resource.data.bodyHash)
                str1 = "%s" % hexhash  # b'cd34b4b6c8d9279217b03c396ca913df'
                # print (str1)
                str1 = str1[2:-1]  # cd34b4b6c8d9279217b03c396ca913df
                # print (str1)
                nbody += "<en-media type=\"%s\" hash=\"%s\" align=\"center\" /><br />" % (resource.mime, str1)
    nbody += neirong
    nbody += "</en-note>"

    note.content = nbody
    # print (note.content)

    # Finally, send the new note to Evernote using the updateNote method
    # The new Note object that is returned will contain server-generated
    # attributes such as the new note's unique GUID.
    trytimes = 3
    sleeptime = 20
    for i in range(trytimes):
        try:
            if notestore is None:
                log.info(f'notestore失效，重新构建evernote服务器连接以便进行笔记《{note.title}》的内容更新操作。')
                updated_note = get_notestore().updateNote(note)
            else:
                updated_note = notestore.updateNote(note)
            # evernoteapijiayi()
            log.info('成功更新了笔记《%s》，guid：%s。' % (updated_note.title, updated_note.guid))
            break
        except Exception as eee:
            log.critical("第%d次（最多尝试%d次）更新笔记《%s》时失败，将于%d秒后重试。%s"
                         % (i + 1, trytimes, note.title, sleeptime, eee))
            if i == (trytimes - 1):
                log.critical(f'更新笔记《{note.title}》失败，只好无功而返。')
                raise eee
            time.sleep(sleeptime)


if __name__ == '__main__':
    log.info('测试evernt')
    get_notestore()
