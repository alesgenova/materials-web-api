import unittest
from tests.env import BASE_URL, CSV_FILE

from tests.local_utils import csv_to_compounds
from tests.api_utils import api_add

class TestApiAdd(unittest.TestCase):
    
    def test_add(self):
        compounds = csv_to_compounds(CSV_FILE)
        # don't add all the compounds, since it's so slow to make an HTTP request for each
        n = min(10, len(compounds))
        for c in compounds[:n]:
            response = api_add(BASE_URL, c)
            self.assertEqual(response.status_code, 201)
