# Peerplays BOS incident store

Default implementation requires a mongodb server running locally.

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