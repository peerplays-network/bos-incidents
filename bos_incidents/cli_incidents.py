import click
import logging

from prettytable import PrettyTable, ALL as ALLBORDERS
from click_datetime import Datetime
from dateutil import parser
from datetime import datetime
from pprint import pprint

from .ui import (
    format_incidents,
    resend_incidents,
    format_event_incidents,
    format_event_incident_statuses,
)

from .cli import incidents


log = logging.getLogger(__name__)


@incidents.command()
def list_providers():
    """ List events
    """
    from bos_incidents import factory
    t = PrettyTable(["Provider", "Incident Count"], hrules=ALLBORDERS)
    t.align = 'l'
    storage = factory.get_incident_storage()
    providers = storage.get_distinct("provider_info.name")

    for provider in providers:
        t.add_row([
            provider,
            str(storage.get_incidents_count({"provider_info.name": provider}))
        ])

    click.echo(t)


@incidents.command()
def purge():
    """ Purge the entire store
    """
    from bos_incidents import factory
    factory.get_incident_storage(purge=True)


@incidents.command()
@click.argument("begin", required=False, type=Datetime(format='%Y/%m/%d'))
@click.argument("end", required=False, type=Datetime(format='%Y/%m/%d'))
def list(begin, end):
    """ List incidents from the bos-incidents store
    """
    from bos_incidents import factory
    t = PrettyTable(["identifier", "Incidents"], hrules=ALLBORDERS)
    t.align = 'l'

    storage = factory.get_incident_storage()

    for event in storage.get_events(resolve=True):

        # pprint(event)
        if not ("id" in event and event["id"]):
            continue
        id = event["id"]
        id["start_time"] = parser.parse(id["start_time"]).replace(
            tzinfo=None)

        # Limit time
        if begin and end and (id["start_time"] < begin or id["start_time"] > end):
            continue

        incidents = format_incidents(event)

        t.add_row([
            "\n".join([
                id["sport"],
                id["event_group_name"],
                id["start_time"].strftime("%Y/%m/%d"),
                "home: {}".format(id["home"]),
                "away: {}".format(id["away"]),
            ]),
            str(incidents)
        ])

    click.echo(t)


@incidents.command()
@click.argument("unique_string", required=False, default=None)
@click.argument("provider", required=False, default=None)
def show(unique_string, provider):
    """ Show the content of a specific incidents
    """
    from bos_incidents import factory
    storage = factory.get_incident_storage()

    if provider is not None:
        incident = storage.get_incident_by_unique_string_and_provider(
            unique_string, provider)
        pprint(incident)
    else:
        if unique_string is not None:
            incidents = storage.get_incidents(
                dict(unique_string=unique_string)
            )
        else:
            incidents = storage.get_incidents()
        for incident in incidents:
            pprint(incident)


@incidents.command()
@click.argument("status_name")
def status(status_name):
    """ Show events that have a status 'status'
    """
    import builtins
    from bos_incidents import factory
    t = PrettyTable(["identifier", "Incidents", "Status"], hrules=ALLBORDERS)
    t.align = 'l'
    storage = factory.get_incident_storage()
    for call in INCIDENT_CALLS:
        events = storage.get_events_by_call_status(call=call, status_name=status_name)
        for event in events:
            full_event = storage.get_event_by_id(event["id_string"])
            t.add_row([
                full_event["id_string"],
                format_event_incidents(full_event),
                format_event_incident_statuses(full_event)
            ])
    click.echo(t)


@incidents.command()
@click.argument("unique_string")
@click.argument("provider")
def rm(unique_string, provider):
    """ Remove an incident from the store
    """
    from bos_incidents import factory
    storage = factory.get_incident_storage()
    incident = storage.get_incident_by_unique_string_and_provider(
        unique_string, provider)
    storage.delete_incident(incident)


@incidents.command()
@click.argument("unique_string")
@click.argument("provider")
@click.option(
    "--url",
    default="http://localhost:8010/trigger"
)
def resend(url, unique_string, provider):
    """ Resend one or more incidents from the store
    """
    from bos_incidents import factory
    storage = factory.get_incident_storage()
    incident = storage.get_incident_by_unique_string_and_provider(
        unique_string, provider)
    pprint(incident)
    incident.update(dict(skip_storage=True))
    resend_incidents(url, incident)


@incidents.command()
@click.argument("call", required=False, default="*")
@click.argument("status_name", required=False)
@click.argument("begin", required=False, type=Datetime(format='%Y/%m/%d'))
@click.argument("end", required=False, type=Datetime(format='%Y/%m/%d'))
@click.option(
    "--url",
    default="http://localhost:8010/trigger"
)
def resendall(url, call, status_name, begin, end):
    """ Resend everything in the store that matches a call and status_name
    """
    from bos_incidents import factory
    storage = factory.get_incident_storage()
    for event in storage.get_events(resolve=False):

        for incident_call, content in event.items():

            if not content or "incidents" not in content:
                continue

            if call and call != "*" and incident_call != call:
                continue

            if status_name and content["status"]["name"] != status_name:
                continue

            for _incident in content["incidents"]:
                incident = storage.resolve_to_incident(_incident)

                id = incident["id"]
                start_time = parser.parse(id["start_time"]).replace(
                    tzinfo=None)

                # Limit time
                if begin and end and (start_time < begin or start_time > end):
                    continue

                pprint(incident)
                incident.update(dict(skip_storage=True))
                resend_incidents(url, incident)


def load():
    # force load this module
    pass
