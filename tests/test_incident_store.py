import unittest

from bos_incidents import factory

import os
import io
import json
from datetime import datetime
from bos_incidents.exceptions import IncidentNotFoundException,\
    InvalidIncidentFormatException


class TestMongoOperationStorage(unittest.TestCase):

    def setUp(self):
        super(TestMongoOperationStorage, self).setUp()
        self.storage = factory.get_incident_storage("mongodbtest", purge=True)

    def _get_in_progress(self):
        return {
            "arguments": {
                "whistle_start_time": "2018-03-22T23:10:45.718Z"
            },
            "call": "in_progress",
            "provider_info": {
                "name": "scorespro",
                "source_file": "20180323-001101_69528886-0774-4df5-93d4-4bffaab79a34.xml",
                "pushed": "2018-03-22T23:11:01.503Z",
                "bitArray": "00000001100",
                "match_id": "1487356",
                "source": "direct string input"
            },
            "unique_string": "2018-03-22t230000z-basketball-nba-regular-season-charlotte-hornets-memphis-grizzlies-in_progress-2018-03-22t231045718z",
            "id": {
                "home": "Charlotte Hornets",
                "start_time": "2018-03-22T23:00:00Z",
                "event_group_name": "NBA Regular Season",
                "away": "Memphis Grizzlies",
                "sport": "Basketball"
            },
            "timestamp": "2018-03-22T23:11:01.542156Z"
        }

    def _get_in_progress_different_call(self):
        return {
            "arguments": {
                "season": "2018"
            },
            "call": "create",
            "provider_info": {
                "name": "scorespro",
                "source_file": "20180323-001101_69528886-0574-4df5-93d4-4bffaab79a34.xml",
                "pushed": "2018-03-22T23:12:01.503Z",
                "bitArray": "00000001100",
                "match_id": "1487356",
                "source": "direct string input"
            },
            "unique_string": "2018-03-22t230000z-basketball-nba-regular-season-charlotte-hornets-memphis-grizzlies-create-2018",
            "id": {
                "home": "Charlotte Hornets",
                "start_time": "2018-03-22T23:00:00Z",
                "event_group_name": "NBA Regular Season",
                "away": "Memphis Grizzlies",
                "sport": "Basketball"
            },
            "timestamp": "2018-03-22T23:11:01.542156Z"
        }

    def _get_in_progress_different_provider(self):
        return {
            "arguments": {
                "whistle_start_time": "2018-03-22T23:10:45.718Z"
            },
            "call": "in_progress",
            "provider_info": {
                "name": "enetpulse",
                "source_file": "20180323-001101_69528886-0754-4df5-93d4-4bffaab79a34.xml",
                "pushed": "2018-03-22T23:11:02.503Z",
                "source": "direct string input"
            },
            "unique_string": "2018-03-22t230000z-basketball-nba-regular-season-charlotte-hornets-memphis-grizzlies-in_progress-2018-03-22t231045718z",
            "id": {
                "home": "Charlotte Hornets",
                "start_time": "2018-03-22T23:00:00Z",
                "event_group_name": "NBA Regular Season",
                "away": "Memphis Grizzlies",
                "sport": "Basketball"
            },
            "timestamp": "2018-03-22T23:11:01.542156Z"
        }

    def _get_in_progress_2(self):
        return {
            "arguments": {
                "whistle_start_time": "2018-03-22T23:10:45.718Z"
            },
            "call": "in_progress",
            "provider_info": {
                "name": "enetpulse",
                "source_file": "20180323-001101_69528886-0774-4df5-93d4-4bffaab79a34.xml",
                "pushed": "2018-03-22T23:11:01.503Z",
                "bitArray": "00000001100",
                "match_id": "1487356",
                "source": "direct string input"
            },
            "unique_string": "2018-03-22t230000z-basketball-nba-regular-season-charlotte-hornets-memphis-grizzlies-in_progress-2018-03-22t231045718z",
            "id": {
                "home": "Charlotte Hornets",
                "start_time": "2018-03-22T23:00:00Z",
                "event_group_name": "NBA Regular Season",
                "away": "Memphis Grizzlies",
                "sport": "Basketball"
            },
            "timestamp": "2018-03-22T23:11:01.542156Z"
        }

    def test_get_set_status(self):
        self.storage.get_status()

        insert = {"now": str(datetime.utcnow())}

        self.storage.set_status(insert)

        self.assertEqual(insert, self.storage.get_status())

        self.storage.set_status({"now": datetime.utcnow()})

    def test_insert(self):
        incident1 = self._get_in_progress()
        self.storage.insert_incident(incident1)

        incident2 = self._get_in_progress_2()
        self.storage.insert_incident(incident2)

        self.storage.delete_incident(incident1)

        self.assertRaises(IncidentNotFoundException,
                          self.storage.get_incident,
                          incident1)

    def test_delete(self):
        incident1 = self._get_in_progress()
        self.storage.insert_incident(incident1)

        count = self.storage.delete_incident(incident1)
        assert count == 1

        self.assertRaises(IncidentNotFoundException,
                          self.storage.delete_incident,
                          incident1)

        incident1 = self._get_in_progress()
        self.storage.insert_incident(incident1)

        incident2 = self._get_in_progress_different_provider()
        self.storage.insert_incident(incident2)

        count = self.storage.delete_incident(incident1["unique_string"])
        assert count == 2

        incident1 = self._get_in_progress()
        self.storage.insert_incident(incident1)

        incident2 = self._get_in_progress_different_call()
        self.storage.insert_incident(incident2)

        count = self.storage.delete_incidents_by_id(incident1)
        assert count == 2

    def test_get(self):
        incident = self._get_in_progress()
        self.storage.insert_incident(incident)

        incident_get = self.storage.get_incident(incident)

        self.assertEqual(incident,
                         incident_get)

        incident2 = self._get_in_progress_different_call()
        self.storage.insert_incident(incident2)

        incidents_get = list(self.storage.get_incidents_by_id(incident))
        self.assertIn(incident2,
                      incidents_get)
        self.assertIn(incident,
                      incidents_get)

    def test_exists(self):
        incident = self._get_in_progress()
        self.storage.insert_incident(incident)

        assert self.storage.incident_exists(incident)

        assert not self.storage.incident_exists(self._get_in_progress_different_call())

        self.storage.insert_incident(self._get_in_progress_different_call())
        self.storage.insert_incident(self._get_in_progress_different_provider())

        assert self.storage.incident_exists(incident)

        assert self.storage.incident_exists_by_id(incident)

        assert self.storage.incident_exists_by_id(incident, call="create")

        assert self.storage.incident_exists_by_id(incident, call="in_progress")

        assert not self.storage.incident_exists_by_id(incident, call="result")

    def test_invalid(self):
        incident = self._get_in_progress()
        incident.pop("id")

        self.assertRaises(InvalidIncidentFormatException,
                          self.storage.insert_incident,
                          incident)

    def test_add_all_from_dump(self):
        for file in os.listdir("dump"):
            abs_path = os.path.join("dump", file)
            if os.path.isfile(abs_path):
                incident = json.loads(io.open(abs_path).read())
                self.storage.insert_incident(incident)

        self.assertEqual(self.storage.get_incidents_count(),
                         12)
