import click
import logging

from prettytable import PrettyTable, ALL as ALLBORDERS
from click_datetime import Datetime
from dateutil import parser
from datetime import datetime
from pprint import pprint

from .format import INCIDENT_CALLS

from .ui import (
    format_incidents,
    resend_incidents,
    format_event_incidents,
    format_event_incident_statuses,
)


log = logging.getLogger(__name__)


@click.group()
def main():
    """ Main group for python-click so we can offer subcommands in a single cli
        tool
    """
    pass


@main.group()
def events():
    """ EventS! specific calls
    """
    pass


@main.group()
def event():
    """ Single-Event specific calls
    """
    pass


@main.group()
def incidents():
    """ Incident specific calls
    """
    pass


@main.command()
@click.argument(
    "filename",
    type=click.File('rb'))
@click.option(
    "--proposer",
)
@click.option(
    "--approver",
)
@click.option(
    "--call",
    default=None,
    type=click.Choice(INCIDENT_CALLS)
)
@click.option(
    "--dry-run/--no-dry-run",
    default=False)
@click.option(
    "--url",
    default="http://localhost:8010/trigger"
)
def replay_from_file(filename, proposer, approver, url, call, dry_run):
    """ Replay incidents from a file
    """
    from tqdm import tqdm
    import requests
    for line in tqdm(filename.readlines()):
        data = eval(line)
        data.update(dict(approver=approver, proposer=proposer))

        # Filter by "call"
        if call and call.lower() != data["call"]:
            continue

        # Print
        pprint(data)

        # Request
        if dry_run:
            log.warning("Skipping push fue to 'dry-run'")
            continue

        resend_incidents(url, data)


# Events #################################################################
@events.command()
@click.option("--call")
@click.option("--status")
@click.option("--providers")
def list(call, status):
    """ List events
    """
    from bos_incidents import factory
    t = PrettyTable(["identifier", "Incidents", "status"], hrules=ALLBORDERS)
    t.align = 'l'
    storage = factory.get_incident_storage()
    if not call:
        events = storage.get_events(resolve=False)
    else:
        events = storage.get_events_by_call_status(call=call, status_name=status)
    for event in events:
        t.add_row([
            event["id_string"],
            format_event_incidents(event),
            format_event_incident_statuses(event)
        ])
    click.echo(str(t))


# Event ##################################################################
@event.command()
@click.argument("identifier")
def show(identifier):
    """ Show event
    """
    from bos_incidents import factory
    t = PrettyTable(["identifier", "Incidents"], hrules=ALLBORDERS)
    t.align = 'l'

    storage = factory.get_incident_storage()
    event = storage.get_event_by_id(identifier)
    incidents = format_incidents(event)
    id = event["id"]
    id["start_time"] = parser.parse(id["start_time"]).replace(
        tzinfo=None)
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


@event.command()
@click.argument("identifier")
@click.argument("call", required=False, default="*")
@click.argument("status_name", required=False)
@click.option(
    "--url",
    default="http://localhost:8010/trigger"
)
def replay(identifier, call, status_name, url):
    """ replay from event
    """
    from bos_incidents import factory
    storage = factory.get_incident_storage()
    event = storage.get_event_by_id(identifier, resolve=False)

    for incident_call, content in event.items():

        if not content or "incidents" not in content:
            continue

        if call and call != "*" and incident_call != call:
            continue

        if status_name and content["status"]["name"] != status_name:
            continue

        for _incident in content["incidents"]:
            incident = storage.resolve_to_incident(_incident)

            pprint(incident)
            incident.update(dict(skip_storage=True))
            resend_incidents(url, incident)


if __name__ == "__main__":
    main()


