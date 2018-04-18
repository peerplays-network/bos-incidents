import os
import yaml
import logging
from logging.handlers import TimedRotatingFileHandler
from copy import deepcopy
import io
import urllib
import json
import collections


__VERSION__ = '0.0.2'


class Config():
    """ This class allows us to load the configuration from a YAML encoded
        configuration file.
    """

    ERRORS = {}

    data = None
    source = None

    @staticmethod
    def load(config_files=[], relative_location=False):
        """ Load config from a file

            :param str file_name: (defaults to ['config.yaml']) File name and
                path to load config from
        """

        if not Config.data:
            Config.data = {}

        if not config_files:
            # load all config files as default
            config_files.append("config-defaults.yaml")
        if type(config_files) == str:
            config_files = [config_files]

            for config_file in config_files:
                if relative_location:
                    file_path = config_file
                else:
                    file_path = os.path.join(
                        os.path.dirname(os.path.realpath(__file__)),
                        config_file
                    )
                stream = io.open(file_path, 'r', encoding='utf-8')
                with stream:
                    Config._nested_update(Config.data, yaml.load(stream))

            if not Config.source:
                Config.source = ""
            Config.source = Config.source + ";".join(config_files)

    @staticmethod
    def get_config(config_name=None):
        """ Static method that returns the configuration as dictionary.
            Usage:

            .. code-block:: python

                Config.get_config()
        """
        if not config_name:
            if not Config.data:
                raise Exception("Either preload the configuration or specify config_name!")
        else:
            if not Config.data:
                Config.data = {}
            Config.load(config_name)
        return deepcopy(Config.data)

    @staticmethod
    def get(*args, message=None, default=None):
        """
        This config getter method allows sophisticated and encapsulated access to the config file, while
        being able to define defaults in-code where necessary.

        :param args: key to retrieve from config, nested in order. if the last is not a string it is assumed to be the default, but giving default keyword is then forbidden
        :type tuple of strings, last can be object
        :param message: message to be displayed when not found, defaults to entry in ERRORS dict with the
                                key defined by the desired config keys in args (key1.key2.key2). For example
                                Config.get("foo", "bar") will attempt to retrieve config["foo"]["bar"], and if
                                not found raise an exception with ERRORS["foo.bar"] message
        :type message: string
        :param default: default value if not found in config
        :type default: object
        """

        # check if last in args is default value
        if type(args[len(args) - 1]) != str:
            if default:
                raise KeyError("There can only be one default set. Either use default=value or add non-string values as last positioned argument!")
            default = args[len(args) - 1]
            args = args[0:len(args) - 1]

        try:
            nested = Config.get_config()
            for key in args:
                if type(key) == str:
                    nested = nested[key]
                else:
                    raise KeyError("The given key " + str(key) + " is not valid.")
            if not nested:
                raise KeyError()
        except KeyError:
            lookup_key = '.'.join(str(i) for i in args)
            if not message:
                if Config.ERRORS.get(lookup_key):
                    message = Config.ERRORS[lookup_key]
                else:
                    message = "Configuration key {0} not found in {1}!"
                message = message.format(lookup_key, Config.source)
            if default is not None:
                logging.getLogger(__name__).debug(message + " Using given default value.")
                return default
            else:
                raise KeyError(message)

        return nested

    @staticmethod
    def reset():
        """ Static method to reset the configuration storage
        """
        Config.data = None
        Config.source = None

    @staticmethod
    def dump_current(file_name="config.json"):
        output = os.path.join(Config.get_config()["dump_folder"], file_name)
        with open(output, 'w') as outfile:
            json.dump(Config.data, outfile)

    @staticmethod
    def _nested_update(d, u):
        for k, v in u.items():
            if isinstance(v, collections.Mapping):
                d[k] = Config._nested_update(d.get(k, {}), v)
            else:
                d[k] = v
        return d


def set_global_logger():
    # setup logging
    # ... log to file system
    log_folder = os.path.join(Config.get("dump_folder", default="dump"), "logs")
    log_level = logging.getLevelName(Config.get("logs", "level", default="INFO"))

    os.makedirs(log_folder, exist_ok=True)
    log_format = ('%(asctime)s %(levelname) -10s: %(message)s')
    trfh = TimedRotatingFileHandler(
        os.path.join(log_folder, "clc-kyc.log"),
        "midnight",
        1
    )
    trfh.suffix = "%Y-%m-%d"
    trfh.setLevel(log_level)
    trfh.setFormatter(logging.Formatter(log_format))

    # ... and to console
    sh = logging.StreamHandler()
    sh.setLevel(log_level)
    sh.setFormatter(logging.Formatter(log_format))

    # global config (e.g. for werkzeug)
    logging.basicConfig(level=log_level,
                        format=log_format,
                        handlers=[trfh, sh])

    return [trfh, sh]


Config.load("config-defaults.yaml")
try:
    # overwrites defaults
    Config.load("incident_storage_config.yaml", True)
except FileNotFoundError:
    pass
