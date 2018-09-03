import os
import yaml
import logging
from copy import deepcopy
import io
import collections


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
                    Config.data = Config._nested_update(
                        Config.data, yaml.load(stream))

            if not Config.source:
                Config.source = ""
            Config.source = Config.source + ";" + ";".join(config_files)

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
    def get(*args, **kwargs):
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
        default_given = "default" in kwargs
        default = kwargs.pop("default", None)
        message = kwargs.pop("message", None)
        # check if last in args is default value
        if type(args[len(args) - 1]) != str:
            if default_given:
                raise KeyError("There can only be one default set. Either use default=value or add non-string values as last positioned argument!")
            default = args[len(args) - 1]
            args = args[0:len(args) - 1]

        try:
            nested = Config.data
            for key in args:
                if type(key) == str:
                    nested = nested[key]
                else:
                    raise KeyError("The given key " + str(key) + " is not valid.")
            if nested is None:
                raise KeyError()
        except KeyError:
            lookup_key = '.'.join(str(i) for i in args)
            if not message:
                if Config.ERRORS.get(lookup_key):
                    message = Config.ERRORS[lookup_key]
                else:
                    message = "Configuration key {0} not found in {1}!"
                message = message.format(lookup_key, Config.source)
            if default_given:
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
    def _nested_update(d, u):
        for k, v in u.items():
            if isinstance(v, collections.Mapping):
                d[k] = Config._nested_update(d.get(k, {}), v)
            else:
                if d:
                    d[k] = v
                else:
                    d = {}
                    d[k] = v
        return d


if not Config.data:
    Config.load("config-defaults.yaml")
    notify = False
    try:
        # overwrites defaults
        Config.load("incident_storage_config.yaml", True)
        notify = True
    except FileNotFoundError:
        pass

    if notify:
        logging.getLogger(__name__).info("Custom config has been loaded " + Config.source)
