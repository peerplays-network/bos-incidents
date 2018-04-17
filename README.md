# Peerplays BOS incident storage

Clone this repository next to the project that has the dependency on the incident storage and 
include it as egg in requirements.txt via

    -e file:../bos-incidents#egg=peerplays_bos_incidents

Default implementation requires a mongodb server running locally (localhost:27017)

    >>> from bos_incidents import factory
    >>> storage = factory.get_incident_storage()
    >>> incidents = storage.get_incidents_by_id({
                "home": "Charlotte Hornets",
                "start_time": "2018-03-22T23:00:00Z",
                "event_group_name": "NBA Regular Season",
                "away": "Memphis Grizzlies",
                "sport": "Basketball"
            }
        )