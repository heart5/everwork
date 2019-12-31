from __future__ import print_function

import datetime
import pickle
import os.path
import base64
import pprint
from pathlib import Path

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


import pathmagic

with pathmagic.context():
    from func.first import getdirmain, touchfilepath2depth
    from func.logme import log
    from func.configpr import getcfpoptionvalue, setcfpoptionvalue

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
service: None = None


def getservice():
    """
    构建Gmail连接服务service，全局化，可以复用
    """

    global service

    if service:
        log.info(f"Gmail连接服务已经存在，无需重新构建\t{service}")
        return service

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    imppath = getdirmain() / "data" / 'imp'
    picklepath = imppath / 'token.pickle'
    credentialspath = imppath / 'gmail_credentials.json'
    if os.path.exists(picklepath):
        with open(picklepath, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentialspath, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(picklepath, 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    log.info(f"成功构建Gmail连接服务\t{service}")

    return service


def getworknewmail():
    """
    获取work标签下的新邮件并保存附件
    """

    global service

    service = getservice()
    # Call the Gmail API
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    """获取目标label的id"""
    worklabelid = None
    if not labels:
        print('No labels found.')
    else:
        # print('Labels:')
        # pprint.pprint(labels)
        for label in labels:
            # print(label['name'], label['id'], label['messagesTotal'], label['messagesUnread'])
            if label['name'] == 'Work':
                # pprint.pprint(label)
                worklabelid = label['id']

    # 获取目标label下的未读邮件信息
    label4work = service.users().labels().get(userId='me', id=worklabelid).execute()
    pprint.pprint(label4work)
    msg4work = service.users().messages().list(userId='me', labelIds=[worklabelid], q='is:unread').execute()
    pprint.pprint(msg4work)
    print(f"未读邮件数量为：{msg4work['resultSizeEstimate']}")

    # 从配置文件读出已处理邮件列表并装配成list待用
    msgidsrecordstr = getcfpoptionvalue('evergmailc', 'mail', '已处理')
    if not msgidsrecordstr:
        msgidsrecordlst = []
    else:
        msgidsrecordlst = msgidsrecordstr.split(',')

    # 遍历待处理邮件并做相应处置
    msgidlst = list()
    for msg in msg4work['messages']:
        # 遍历，通过头部插入实现升序排列
        msgidlst.insert(0, msg['id'])

    msgchulilst = list()
    for msgid in msgidlst:
        # 判断是否在已处理列表中，是则跳过继续循环
        if msgid in msgidsrecordlst:
            print(f"邮件\t{msgid}\t已处理过")
            continue

        # 获取邮件
        mailmsg = service.users().messages().get(userId='me', id=msgid).execute()
        print(msgid)
        # pprint.pprint(mailmsg)
        # print(f"{mailmsg['snippet']}")

        # 处理邮件标题
        hnamelst = list()
        hvaluelst = list()
        for headerinner in mailmsg['payload']['headers']:
            hnamelst.append(headerinner['name'])
            hvaluelst.append(headerinner['value'])
        headercontentdict = dict(zip(hnamelst, hvaluelst))
        pprint.pprint(headercontentdict)
        msgheader = headercontentdict['Subject']
        print(msgheader)

        # 处理邮件中的附件
        pprint.pprint(mailmsg['payload']['parts'])
        msgattachmentslst = list()
        for part in mailmsg['payload']['parts']:
            attachname = part['filename']
            if attachname:
                pprint.pprint(part)
                attach = service.users().messages().attachments().get(userId='me',
                                                                      id=part['body']['attachmentId'],
                                                                      messageId=msgid).execute()
                file_data = base64.urlsafe_b64decode(attach['data'].encode('utf-8'))

                # 处理附件文件名，按照主题保存到相应的目录下
                datadirwork = getdirmain() / 'data' / 'work'
                pointat1 = attachname.rfind('.')
                timenowstr = datetime.datetime.now().strftime('__%Y%m%d%H%M%S_%f')
                datadiri = datadirwork
                if attachname.startswith('销售订单'):
                    # print(fname)
                    datadiri = os.path.join(datadirwork, '销售订单')
                elif attachname.startswith('订单明细'):
                    # print(fname)
                    datadiri = os.path.join(datadirwork, '订单明细')

                attachfile = os.path.join(datadiri, attachname[:pointat1] + timenowstr + attachname[pointat1:])

                print(attachfile, attach['size'])
                touchfilepath2depth(Path(attachfile))
                f = open(attachfile, 'wb')
                f.write(file_data)
                f.close()
                msgattachmentslst.append(attachname)

        print(msgattachmentslst)
        # credentials只有读取的权限，无法做出写入和更改处理，修改操作只能先注释掉
        # modifylabeldict = {'addLabelIds':[], 'removeLabelIds':['Unread']}
        # modifymsg = service.users().messages().modify(userId='me', id=msg['id'], body=modifylabeldict).execute()
        print(f"邮件{msgid}处理完毕，标记为已处理")
        msgidsrecordlst.insert(0, msgid)
        msgchulilst.append(msgid)
        log.info(f"邮件{msgid}\t{msgheader}处理完毕，附件列表为：{msgattachmentslst}")

    setcfpoptionvalue('evergmailc', 'mail', '已处理', ','.join(msgidsrecordlst))
    log.info(f"共有{len(msgchulilst)}封邮件处理完毕，邮件编号列表：{msgchulilst}")


if __name__ == '__main__':
    getworknewmail()
