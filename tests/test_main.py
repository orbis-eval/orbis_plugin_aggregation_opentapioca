# -*- coding: utf-8 -*-

from orbis_plugin_aggregation_opentapioca.main import Main
from orbis_eval.core.rucksack import Rucksack

import requests_mock
import unittest
import json

class TestMain(unittest.TestCase):

    def setUp(self):
        self.config = {
            "aggregation": {
                "service": {
                    "language": "en",
                    "location": "web"
                },
                "input": {
                    "data_set": {
                        "name": "rss1"
                    }
                }
            },
            "file_name": "rss1_opentapioca_web.yaml"
        }
        self.rucksack = Rucksack(self.config)
        self.main = Main(rucksack=self.rucksack)       

    def test_get_service_url(self):	
        query = "Much to learn you still have… my old padawan. This is just the beginning!"
        expectedURL = "https://opentapioca.org/api/annotate?query=Much+to+learn+you+still+have%E2%80%A6+my+old+padawan.+This+is+just+the+beginning%21"
        self.assertEqual(self.main.get_service_url(query), expectedURL)

if __name__ == '__main__':
    unittest.main()