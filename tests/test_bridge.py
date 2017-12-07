import unittest
from datetime import date
from data.bridge import AccountSummarySheetBridge

class MockGoogleSheetsConnector(object):
    def __init__(self):
        self.x = True
        self.append_rows_called = 0

    def initialized(self):
        return self.x

    def append_rows(self, rows):
        self.append_rows_called += 1

class Processing(unittest.TestCase):
    def setUp(self):
        self.gs = MockGoogleSheetsConnector()
        self.br = AccountSummarySheetBridge(self.gs)
        self.data = {
            '12345': {'HKD Current': '123.00'},
            '67890': {'HKD Current': '678.00', 'HKD Savings': '901.00'}
        }

    def test_add_values_initialized(self):
        self.br.add_values(self.data)
        self.assertTrue(len(self.br.rows) == 1)

    def test_add_values_uninitialized(self):
        self.gs.x = False
        self.br.add_values(self.data)
        self.assertTrue(len(self.br.rows) == 3)
        self.assertEqual(self.br.rows[2][0], date.today().isoformat())

    def test_commit_rows(self):
        self.br.commit_rows()
        self.assertTrue(self.gs.append_rows_called == 1)

if __name__ == '__main__':
    unittest.main()
