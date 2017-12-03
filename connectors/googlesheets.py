from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

class GoogleSheetsConnector(object):
    SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
    CLIENT_SECRET_FILE = 'client_id.json'
    APPLICATION_NAME = 'Automation - Banking'
    SPREADSHEET_ID = '1KnEM0WDqk7y64RlktSB_1TtZXxRqtERDdrmkiSSwLHE'

    def __init__(self):
        self.service = self.get_service()

    def get_credentials(self):
        """Gets valid user credentials from connectors.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """

        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                       'sheets.googleapis.com-automation-banking.json')

        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            flow = client.flow_from_clientsecrets(os.path.join(current_dir, '../{}'.format(self.CLIENT_SECRET_FILE)),
                                                  self.SCOPES)
            flow.user_agent = self.APPLICATION_NAME
            credentials = tools.run_flow(flow, store)
            print('Storing credentials to ' + credential_path)

        return credentials

    def get_service(self):
        credentials = self.get_credentials()
        http = credentials.authorize(httplib2.Http())
        discovery_url = ('https://sheets.googleapis.com/$discovery/rest?version=v4')
        return discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discovery_url)

    def read_range(self, range_name):
        result = self.service.spreadsheets().values().get(spreadsheetId=self.SPREADSHEET_ID, range=range_name).execute()
        values = result.get('values', [])
        return values

    def append_data(self):
        range_name = 'Sheet1!A:F'
        body = {
            'range': range_name,
            'values': [
                1, 2, 3, 4, 5
            ]
        }
        self.service.spreadsheets().values().append(spreadsheetId=self.SPREADSHEET_ID, range=range_name,
                                                    insertDataOption='INSERT_ROWS', body=body)