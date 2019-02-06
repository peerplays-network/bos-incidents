import unittest

from bos_incidents.format import string_to_incident, incident_to_string
from bos_incidents.datestring import date_to_string, string_to_date
from datetime import datetime, timezone

class TestMongoOperationStorage(unittest.TestCase):

    def setUp(self):
        pass

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

    def test_string_to_incident(self):
        self.assertEqual(
            incident_to_string(self._get_in_progress()),
            "2018-03-22t230000z__basketball__nba-regular-season__charlotte-hornets__memphis-grizzlies__in_progress__2018-03-22t231045718z"
        )

    def test_incident_to_string(self):
        incident_dict = string_to_incident(
            "2018-03-22t230000z__basketball__nba-regular-season__charlotte-hornets__memphis-grizzlies__in_progress__2018-03-22t231045718z",
            "my_provider"
        )
        self.maxDiff = None
        self.assertEqual(
            incident_dict,
            {
                'arguments': {'whistle_start_time': '2018-03-22T23:10:45.718Z'},
                'call': 'in_progress',
                'id': {'away': 'memphis-grizzlies',
                       'event_group_name': 'nba-regular-season',
                       'home': 'charlotte-hornets',
                       'sport': 'Basketball',
                       'start_time': '2018-03-22T23:00:00Z'},
                'timestamp': incident_dict["timestamp"],
                'provider_info': {'name': 'my_provider', 'pushed': incident_dict["provider_info"]["pushed"]},
                'unique_string': '2018-03-22t230000z__basketball__nba-regular-season__charlotte-hornets__memphis-grizzlies__in_progress__2018-03-22t231045718z'
            }
        )

    def test_date_to_string(self):
        date_to_string()
        date_to_string("2019-01-02 03:04:00")
        date_to_string("2019-01-02T030400Z")

        self.assertEqual(
            type(date_to_string()),
            str
        )
        date_obj = datetime(2019, 1, 2, 3, 4, tzinfo=timezone.utc)
        self.assertEqual(
            date_to_string(date_obj),
            "2019-01-02T03:04:00Z"
        )
        self.assertEqual(
            date_to_string(date_obj.timestamp()),
            "2019-01-02T03:04:00Z"
        )
        self.assertEqual(
            date_to_string(int(date_obj.timestamp())),
            "2019-01-02T03:04:00Z"
        )
        self.assertEqual(
            date_to_string(date_obj.timestamp() + 0.5),
            "2019-01-02T03:04:00.5Z"
        )
        self.assertLess(
            string_to_date(date_to_string()),
            string_to_date(date_to_string(2))
        )

    def test_string_to_date(self):
        string_to_date()
        string_to_date(None)
        string_to_date("20190102")
        string_to_date("2019-01-02")
        string_to_date("2019-01-02T030400Z")
        string_to_date("2019-01-02t030400000z")
        string_to_date("2019-01-02T03:04:00Z")
        string_to_date("2019-01-02T03:04:00Z")

        with self.assertRaises(Exception):
            string_to_date(datetime.now())
