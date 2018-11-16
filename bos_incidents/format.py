import os
import io
import json
import jsonschema
import re
import unicodedata

from .datestring import date_to_string, string_to_date
from .validator import IncidentValidator

from bookiesports.normalize import IncidentsNormalizer
import hashlib


DELIMITER = "__"
SPACE_REPLACEMENT = "-"

MASK = None

INCIDENT_CALLS = [
    "create",
    "in_progress",
    "finish",
    "result",
    "canceled",
    "dynamic_bmgs",
]


def slugify(value, allow_unicode=False):
    """ Converts to a file name suitable string

    Convert to ASCII if 'allow_unicode' is False. Convert spaces to hyphens.
    Remove characters that aren't alphanumerics, underscores, or hyphens.
    Convert to lowercase. Also strip leading and trailing whitespace.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode(
            'ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    return re.sub(r'[\s]+', "-", value)


def get_masked_provider(provider_info, mask):
    masked_name = provider_info["name"] + mask
    masked_name = hashlib.md5(masked_name.encode()).hexdigest()
    # masking removes everything besides name and pushed
    return {
        "name": masked_name,
        "pushed": provider_info["pushed"]
    }


def string_to_incident(incident, provider_info=None, mask=None):
    delimited = incident.split(DELIMITER)

    # must be sorted according to serialization
    argument_keys = {
        "create": lambda: ["season"],
        "in_progress": lambda: {"format": lambda x: date_to_string(string_to_date(x)), "keys": ["whistle_start_time"]},
        "finish": lambda: {"format": lambda x: date_to_string(string_to_date(x)), "keys": ["whistle_end_time"]},
        "result": lambda: ["home_score", "away_score"],
        "dynamic_bmgs": lambda: [],
        "canceled": lambda: ["reason"]
    }[delimited[5]]()

    arguments_dict = {}
    if type(argument_keys) == list:
        for idx, key in enumerate(argument_keys):
            arguments_dict[key] = delimited[6 + idx]
    else:
        for idx, key in enumerate(argument_keys["keys"]):
            arguments_dict[key] = argument_keys["format"](delimited[6 + idx])

    incident_dict = {
        "id": {
            "start_time": date_to_string(string_to_date(delimited[0])),
            "sport": delimited[1],
            "event_group_name": delimited[2],
            "home": delimited[3],
            "away": delimited[4]
        },
        "call": delimited[5],
        "arguments": arguments_dict,
        "timestamp": date_to_string()
    }
    if provider_info is not None:
        if type(provider_info) == str:
            provider_info = {
                "name": provider_info,
                "pushed": date_to_string()
            }
        incident_dict["provider_info"] = provider_info
        if mask is not None:
            incident_dict["provider_info"] = get_masked_provider(incident_dict["provider_info"], mask)
    return ensure_incident_format(incident_dict)


def incident_to_string(incident):
    arguments_as_string = serialize_arguments(incident["call"], incident["arguments"])

    if arguments_as_string is not None and not arguments_as_string == "":
        arguments_as_string = DELIMITER + arguments_as_string

    return slugify(
        get_id_as_string(incident["id"]) + DELIMITER + incident["call"] + arguments_as_string
    )


def reformat_datetimes(formatted_dict):
        """ checks every value, if date found replace with rfc3339 string """
        for (key, value) in formatted_dict.items():
            if value:
                if isinstance(value, dict):
                    reformat_datetimes(value)
                elif type(value) == str and len(value) == 19 and\
                        re.match('\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d', str(value)):
                    formatted_dict[key] = date_to_string(value)


def validate(formatted_dict):
    IncidentValidator().validate_incident(formatted_dict)


def serialize_arguments(call, arguments):
    if call == "result":
        return arguments["home_score"] + "-" + arguments["away_score"]
    elif call == "dynamic_bmgs":
        sorted_types = sorted(arguments["types"], key=lambda k: k["type"] + k["value"] + k.get("participant", ""))
        return "-".join([k["type"] + "-" + k["value"] + "-" + k.get("participant", "") for k in sorted_types])
    else:
        return ", ".join(filter(None, (str(x) for x in arguments.values())))


def get_id_as_string(incident_id):
    return incident_id["start_time"] \
        + DELIMITER + incident_id["sport"] \
        + DELIMITER + incident_id["event_group_name"] \
        + DELIMITER + incident_id["home"] \
        + DELIMITER + incident_id["away"]


def ensure_incident_format(raw_dict):
    """
        reformats dates, validates the json and creates unique_string identifier
    """
    reformat_datetimes(raw_dict)
    IncidentValidator().validate_incident(raw_dict)

    # normalize before creating unique_string
    formatted_dict = IncidentsNormalizer().normalize(raw_dict)

    formatted_dict["unique_string"] = incident_to_string(formatted_dict)

    return formatted_dict
