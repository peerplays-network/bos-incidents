import unittest

from bos_incidents import factory

import os
import io
import json
from datetime import datetime
from bos_incidents.exceptions import IncidentNotFoundException,\
    InvalidIncidentFormatException
from time import sleep


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

    def _get_in_progress_different_call_different_provider(self):
        return {
            "arguments": {
                "season": "2018"
            },
            "call": "create",
            "provider_info": {
                "name": "enetpulse",
                "source_file": "20180323-001101_69528886-0754-4df5-93d4-4bffaab79a34.xml",
                "pushed": "2018-03-22T23:11:02.503Z",
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

    def test_insert(self):
        self.storage.insert_incident(self._get_in_progress_different_call())
        self.storage.insert_incident(self._get_in_progress_different_call_different_provider())
        self.storage.insert_incident(self._get_in_progress())
        self.storage.insert_incident(self._get_in_progress_different_provider())

        event = self.storage.get_event_by_id(self._get_in_progress_different_call())

        assert len(event["create"]["incidents"]) == 2
        assert len(event["in_progress"]["incidents"]) == 2

    def test_update_status(self):
        self.storage.insert_incident(self._get_in_progress_different_call())
        self.storage.insert_incident(self._get_in_progress_different_call_different_provider())
        self.storage.insert_incident(self._get_in_progress())
        self.storage.insert_incident(self._get_in_progress_different_provider())

        self.storage.update_event_status_by_id(self._get_in_progress_different_call(),
                                               "create",
                                               status_name="pending",
                                               status_expiration=datetime.utcnow())

        event = self.storage.get_event_by_id(self._get_in_progress_different_call(), resolve=False)

        assert event["create"]["status"]["name"] == "pending"

    def test_status_expiration_query(self):
        self.test_update_status()

        event = self.storage.get_event_by_id(self._get_in_progress_different_call(), resolve=False)

        noW = datetime.utcnow()

        events = self.storage.get_events_by_call_status("create", "pending", noW)

        self.assertEqual(event, list(events)[0])

        self.storage.update_event_status_by_id(self._get_in_progress_different_call(),
                                               "create",
                                               status_name="pending",
                                               status_expiration=datetime.utcnow())

        events = self.storage.get_events_by_call_status("create", "pending", noW)

        assert list(events) == []

    def test_get(self):
        self.test_update_status()

        event = self.storage.get_event_by_id(self._get_in_progress_different_call())

        assert event["create"]["incidents"][0]["arguments"]

    def test_resolve_to_incident(self):
        self.test_update_status()

        self.maxDiff = None

        for event in self.storage.get_events(resolve=False):
            for _incident in event.get("create", {"incidents": {}})["incidents"]:
                incident = self.storage.resolve_to_incident(_incident)
                if incident["provider_info"]["name"] == "scorespro" and incident["unique_string"] == "2018-03-22t230000z-basketball-nba-regular-season-charlotte-hornets-memphis-grizzlies-create-2018":
                    self.assertEqual(incident, {'arguments': {'season': '2018'}, 'call': 'create', 'provider_info': {'name': 'scorespro', 'source_file': '20180323-001101_69528886-0574-4df5-93d4-4bffaab79a34.xml', 'pushed': '2018-03-22T23:12:01.503Z', 'bitArray': '00000001100', 'match_id': '1487356', 'source': 'direct string input'}, 'unique_string': '2018-03-22t230000z-basketball-nba-regular-season-charlotte-hornets-memphis-grizzlies-create-2018', 'id': {'home': 'Charlotte Hornets', 'start_time': '2018-03-22T23:00:00Z', 'event_group_name': 'NBA Regular Season', 'away': 'Memphis Grizzlies', 'sport': 'Basketball'}, 'timestamp': '2018-03-22T23:11:01.542156Z'})

    def test_add_all_from_dump(self):
        for file in os.listdir("dump"):
            abs_path = os.path.join("dump", file)
            if os.path.isfile(abs_path):
                incident = json.loads(io.open(abs_path).read())
                self.storage.insert_incident(incident)

        event = self.storage.get_event_by_id(incident)
