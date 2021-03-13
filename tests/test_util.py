from unittest.mock import patch
from freezegun import freeze_time

from datetime import datetime
import unittest
import util


class TestUtil(unittest.TestCase):
    @freeze_time('2021-01-01')
    @patch('builtins.print')
    def test_log_event(self, mock_print):
        util.log_event('hello', module='connected_database')
        mock_print.assert_called_with('[connected_database | 00:00:00] hello')
        util.log_event('hello')
        mock_print.assert_called_with('[00:00:00] hello')
    
    def test_itemid(self):
        self.assertEqual(util.itemid(datetime(year=2021, month=1, day=1), 'food'), '01/21:food')

    def test_parse_itemid(self):
        itemid = util.itemid(datetime(year=2021, month=1, day=1), 'food')
        self.assertEqual(util.parse_itemid(itemid), (datetime(year=2021, month=1, day=1), 'food'))

if __name__ == '__main__':
    unittest.main()