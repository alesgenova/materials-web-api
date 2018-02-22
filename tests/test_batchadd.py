import unittest
from tests.env import BASE_URL, CSV_FILE

from tests.local_utils import csv_to_compounds
from tests.api_utils import api_batchadd

class TestApiBatchAdd(unittest.TestCase):
    
    def test_batchadd(self):
        compounds = csv_to_compounds(CSV_FILE)
        response = api_batchadd(BASE_URL, compounds)
        self.assertEqual(response.status_code, 201)

