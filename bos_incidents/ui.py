import click
import requests
import logging

from prettytable import PrettyTable
from pprint import pprint

from .format import INCIDENT_CALLS

log = logging.getLogger(__name__)


def format_incidents(event):
    incidents = PrettyTable(
        ["call", "status", "incident uid", "incident provider"],
    )
    incidents.align = 'l'
    for call, content in event.items():
        if "incidents" not in content:
            log.warning("no 'incidents' in content: {}".format(content))

        try:  # FIXME why can some incidents not be resolved?
            incidents.add_row([
                call,
                "\n".join(["{}: {}".format(k, v) for (k, v) in content["status"].items()]),
                "\n".join([x["unique_string"] for x in content["incidents"]]),
                "\n".join([x["provider_info"]["name"] for x in content["incidents"]])
            ])
        except Exception:
            pass
    return incidents


def dictToFormatedList(d):
    return "\n".join(["{:<15}: {}".format(k, v) for k, v in d.items()])


def format_event_incidents(event):
    return dictToFormatedList({x: len(event.get(x, [])) for x in INCIDENT_CALLS})


def format_event_incident_statuses(event):
    return dictToFormatedList({x: "{}".format(
        event.get(x, {}).get("status",{}).get("name", "")
    ) for x in INCIDENT_CALLS})


def resend_incidents(url, data):
    try:
        ret = requests.post(
            url,
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        if ret.status_code != 200:
            raise Exception("Status code: {}: {}".format(
                ret.status_code,
                ret.text))
    except Exception as e:
        log.error("[Error] Failed pushing")
        log.error(str(e))
