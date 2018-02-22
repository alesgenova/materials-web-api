import unittest
from tests.env import BASE_URL, CSV_FILE

from tests.local_utils import csv_to_compounds, local_search
from tests.api_utils import api_batchadd, api_clear, api_search

class TestApiSearch(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
          This setUp is in common for all the test cases below, and it's only execuded once
          We are ensuring all the entries are in the database.
        """
        cls.local_compounds = csv_to_compounds(CSV_FILE)
        # clear the DB so we are sure that the local compounds are the same as the remote ones
        r = api_clear(BASE_URL)
        assert r.status_code == 204
        r = api_batchadd(BASE_URL, cls.local_compounds)
        assert r.status_code == 201

    
    def test_search_empty(self):
        the_filter = {}
        api_res = api_search(BASE_URL,the_filter)
        local_res = local_search(self.local_compounds,the_filter)
        # we just make sure that the number of compouds matches,
        # in the real world we should make sure that each compound is actually the same
        self.assertEqual(api_res.status_code, 200)
        self.assertEqual(len(api_res.json()), len(local_res))
    
    def test_search_name(self):
        the_filter = {
            "compound": {
                "value": "Pb",
                "logic": "contains"
            }
        }
        api_res = api_search(BASE_URL,the_filter)
        local_res = local_search(self.local_compounds,the_filter)
        # we just make sure that the number of compouds matches,
        # in the real world we should make sure that each compound is actually the same
        self.assertEqual(api_res.status_code, 200)
        self.assertEqual(len(api_res.json()), len(local_res))

    def test_search_full(self):
        the_filter = {
            "compound": {
                "value": "Se",
                "logic": "contains"
            },
            "properties": [
                {
                    "name": "Band gap",
                    "value": "3",
                    "logic": "lt"
                },
                {
                    "name": "Color",
                    "value": "Gray",
                    "logic": "contains"
                }
            ]
        }
        api_res = api_search(BASE_URL,the_filter)
        local_res = local_search(self.local_compounds,the_filter)
        # we just make sure that the number of compouds matches,
        # in the real world we should make sure that each compound is actually the same
        self.assertEqual(api_res.status_code, 200)
        self.assertEqual(len(api_res.json()), len(local_res))

    def test_search_wrong(self):
        the_filter = {
            "compound": {
                "wrong_value": "Se",
                "wrong_logic": "contains"
            }
        }
        # we expect a 400 response from the API, since the serializer wouldn't accept this filter
        api_res = api_search(BASE_URL,the_filter)
        self.assertEqual(api_res.status_code, 400)


