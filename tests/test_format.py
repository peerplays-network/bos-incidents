import unittest

from bos_incidents.format import string_to_incident, incident_to_string


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
        self.assertEqual(
            incident_dict,
            {
                'arguments': {'whistle_start_time': '2018-03-22T23:10:45.718Z'},
                'call': 'in_progress',
                'id': {'away': 'memphis-grizzlies',
                       'event_group_name': 'nba-regular-season',
                       'home': 'charlotte-hornets',
                       'sport': 'basketball',
                       'start_time': '2018-03-22T23:00:00Z'},
                'timestamp': incident_dict["timestamp"],
                'provider_info': {'name': 'my_provider', 'pushed': incident_dict["provider_info"]["pushed"]},
                'unique_string': '2018-03-22t230000z__basketball__nba-regular-season__charlotte-hornets__memphis-grizzlies__in_progress__2018-03-22t231045718z'
            }
        )
