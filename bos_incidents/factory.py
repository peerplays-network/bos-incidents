import logging

from . import Config
from .mongodb_storage import EventStorage


def get_incident_storage(use=None, purge=False):
    """ This factory initializes an IncidentStor object specified by use.
        If necessary, the database is purged before use.

        :param use: Indicates which implementation of IOperationStorage will be used
                    Available:
                        mongodb
                    Default: as configured in config.yaml
        :type use: String
        :param purge: Indicates if the database should be purged
        :type purge: boolean, for default behavior set to None.
                     no purge for real connections,
                     purge for test connections
    """

    printConfig = False
    if not use:
        # default operation storage is wanted, print config for clarification
        printConfig = True
        use = Config.get("bos_incidents", "database", "use")

    config = Config.get("bos_incidents", "database")
    use_config = config[use]

    if printConfig:
        logging.getLogger(__name__).debug("Incident storage initialized with use=" + use)

    return EventStorage(mongodb_config=use_config, purge=purge)
