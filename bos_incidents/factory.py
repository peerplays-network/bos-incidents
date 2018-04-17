import logging

from . import Config
from .mongodb_storage import IncidentStorage


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
        use = Config.get("database", "use")

    def get_mongodb(use_config):
        return IncidentStorage(mongodb_config=use_config, purge=purge)

    def get_mongodb_test(use_config):
        return IncidentStorage(mongodb_config=use_config, purge=purge)

    config = Config.get("database")
    use_config = config[use]

    use_choice = {
        "mongodb": lambda: get_mongodb(use_config),
        "mongodbtest": lambda: get_mongodb_test(use_config)
    }

    if printConfig:
        logging.getLogger(__name__).debug("Incident storage initialized with use=" + use)

    return use_choice[use]()
