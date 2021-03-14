from datastrax_api import DataStraxApi, BudgetKey

from datetime import datetime
from unittest.mock import patch

import unittest

@patch('cassandra.cluster.Cluster.connect')
class TestDatastraxApi(unittest.TestCase):

    dsa = DataStraxApi()

    @patch('datastrax_api.DataStraxApi.session.execute')
    def test_get_all(self, mock_execute):
        self.dsa.get('users')
        mock_session.execute.assert_called_with('SELECT * FROM users')

    @patch('cassandra.cluster.Cluster.connect.execute')
    def test_get_primary_key_budget(self, mock_session):
        self.dsa.get('users', primary_key=BudgetKey('lougene', '03/2021', 'food'))
        execute.assert_called_with("SELECT * FROM budgets WHERE owner='lougene' AND date='03/2021' AND name='food'")
        

if __name__ == '__main__':
    unittest.main()