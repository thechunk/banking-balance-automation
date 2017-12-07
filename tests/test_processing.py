import unittest
from data.processing import banks_to_headers, banks_to_rows
from data.processing import DataInconsistencyError

class Processing(unittest.TestCase):
    def setUp(self):
        self.data = {
            '12345': {'HKD Current': '123.00'},
            '67890': {'HKD Current': '678.00', 'HKD Savings': '901.00'}
        }
        self.inconsistent_data = {
            '12345': {'HKD Current': '123.00'},
            '67890': {'HKD Current': '', 'HKD Savings': ''}
        }

    def test_generate_headers(self):
        headers = banks_to_headers(self.data)
        self.assertListEqual(headers, [
            ['12345', '67890', '67890'],
            ['HKD Current', 'HKD Current', 'HKD Savings']
        ])

    def test_generate_row(self):
        row = banks_to_rows(self.data)
        self.assertListEqual(row, ['123.00', '678.00', '901.00'])

    def test_generate_row_inconsistent(self):
        with self.assertRaises(DataInconsistencyError):
            banks_to_rows(self.inconsistent_data)

if __name__ == '__main__':
    unittest.main()