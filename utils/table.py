import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

PATH = '/root/studhsebot' # path to your project dir


class Table:
    def __connect_google_api(self):
        token_path = f'{PATH}/token.json' # you should also create the JSON with required token
        scopes = ['https://www.googleapis.com/auth/spreadsheets']

        credentials = None
        if os.path.exists(token_path):
            credentials = Credentials.from_authorized_user_file(token_path, scopes)

        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    f'{PATH}/credentials.json', scopes)
                credentials = flow.run_local_server(port=0)
                with open(token_path, 'w') as token:
                    token.write(credentials.to_json())

        self.service = build('sheets', 'v4', credentials=credentials)

    def __init__(self, spreadsheet_id):
        self.__connect_google_api()

        self.sheet_name = None
        self.spreadsheet_id = None

        self.set_spreadsheet(spreadsheet_id)

    def set_spreadsheet(self, ss_id):
        self.spreadsheet_id = ss_id

    def set_sheet(self, name):
        self.sheet_name = name

    def append_row(self, *elements):
        return self.service.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id,
            body=dict(values=[elements]),
            valueInputOption='USER_ENTERED',
            range=f'{self.sheet_name}!A:Z',
        ).execute()

    def get(self, rng='A:Z'):
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range=f'{self.sheet_name}!{rng}'
        ).execute()
        return result.get('values', [])

    def update(self, elements, rng):
        self.service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id,
            body=dict(values=elements),
            valueInputOption='USER_ENTERED',
            range=f'{self.sheet_name}!{rng}',
        ).execute()
