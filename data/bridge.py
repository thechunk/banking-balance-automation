from datetime import date
from data.processing import banks_to_rows, banks_to_headers

class AccountSummarySheetBridge(object):
    def __init__(self, gs):
        self.gs = gs # GoogleSheetsConnector instance
        self.rows = []

    def add_values(self, balance):
        values = banks_to_rows(balance)
        if not self.gs.initialized():
            self.rows = banks_to_headers(balance)

        values.insert(0, date.today().isoformat())
        self.rows.append(values)

    def commit_rows(self):
        self.gs.append_rows(self.rows)