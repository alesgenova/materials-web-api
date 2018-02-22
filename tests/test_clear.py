import unittest
from tests.env import BASE_URL, CSV_FILE

from tests.local_utils import csv_to_compounds
from tests.api_utils import api_clear

class TestApiClear(unittest.TestCase):
    
    def test_clear(self):
        response = api_clear(BASE_URL)
        self.assertEqual(response.status_code, 204)
