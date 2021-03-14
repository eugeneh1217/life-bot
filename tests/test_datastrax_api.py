from datastrax_api import DataStraxApi, BudgetKey

from datetime import datetime
from unittest.mock import patch

import unittest


class TestDatastraxApi(unittest.TestCase):

    dsa = DataStraxApi()

    @patch('cassandra.cluster.Cluster.connect')
    def test_get_all(self, mock_session):
        self.dsa.get('users')
        mock_session.execute.assert_called_with('SELECT * FROM users')
    
    @patch('cassandra.cluster.Cluster.connect')
    def test_get_primary_all(self, mock_session):
        self.dsa.get('users', primary_key=BudgetKey)
        

if __name__ == '__main__':
    unittest.main()