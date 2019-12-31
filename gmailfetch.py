from __future__ import print_function
import pickle
import os.path
import base64
import pprint
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


import pathmagic
with pathmagic.context():
    from func.first import getdirmain
 

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def main():
    """
    Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            cjpath = getdirmain() / "data" / 'imp' / 'gmail_credentials.json'
            flow = InstalledAppFlow.from_client_secrets_file(cjpath, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    # Call the Gmail API
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    if not labels:
        print('No labels found.')
    else:
        print('Labels:')
        for label in labels:
            # print(label['name'], label['id'], label['messagesTotal'], label['messagesUnread'])
            print(label)
            # print(label['name'], label['id'], label['type'])
    
    label4work = service.users().labels().get(userId='me', id='Label_22').execute()
    print(label4work)
    msg4work = service.users().messages().list(userId='me', labelIds=['Label_22'], q='is:unread').execute()
    print(msg4work)
    print(f"未读邮件数量为：{msg4work['resultSizeEstimate']}")
    for msg in msg4work['messages']:
        mailmsg = service.users().messages().get(userId='me', id=msg['id']).execute()
        print(msg['id'])
        pprint.pprint(mailmsg)
        print(f"{mailmsg['snippet']}")
        pprint.pprint(mailmsg['payload']['parts'])
        for part in mailmsg['payload']['parts']:
            if part['filename']:
                print(part)
                attach = service.users().messages().attachments().get(userId='me', id=part['body']['attachmentId'], messageId=msg['id']).execute()
                file_data = base64.urlsafe_b64decode(attach['data'].encode('utf-8'))
                path = getdirmain() / part['filename']
                print(path, attach['size'])
                f = open(path, 'wb')
                f.write(file_data)
                f.close()
        # modifylabeldict = {'addLabelIds':[], 'removeLabelIds':['Unread']}
        # modifymsg = service.users().messages().modify(userId='me', id=msg['id'], body=modifylabeldict).execute()
        print(f"邮件{msg['id']}处理完毕，标记为已读")


if __name__ == '__main__':
    main()


