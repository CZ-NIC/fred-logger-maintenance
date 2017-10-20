"""Module for logger db accessing scripts."""
import argparse
import json
import logging
from datetime import date
from json.decoder import JSONDecodeError

import psycopg2
from psycopg2 import InterfaceError, OperationalError


class ConfigError(Exception):
    """Raised when config file does not contain all required variables."""

    def __init__(self, message):
        """Initialize error message."""
        self.message = message


class FatalScriptError(Exception):
    """Raised when captured exception is fatal."""

    def __init__(self, error, message=None):
        """Initialize error message and original captured error."""
        self.error = error
        self.message = message


class DateAction(argparse.Action):
    """Action class to convert YYYY-MM string to date object."""

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        """Initialize convert action."""
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super(DateAction, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        """Convert YYYY-MM string to date object."""
        try:
            (year, month) = values.split('-')
            setattr(namespace, self.dest, date(int(year), int(month), 1))
        except ValueError:
            logging.error("Wrong date format")
            raise FatalScriptError(ValueError)


class LoggerMaintenanceScript(object):
    """Generic class for Logger maintenance scripts."""

    # Items that has to be present in configuration file
    MANDATORY_CONF = {"host", "user", "database"}

    def __init__(self, args):
        """Process command line arguments and read given configuration file.

        :param args: command line arguments
        """
        self.process_args(args)

    def process_args(self, args):
        """Process command line arguments."""
        raise NotImplementedError

    def execute(self):
        """Do all actual work in this function."""
        raise NotImplementedError

    def read_config(self, config_filename=None):
        """Read configuration from JSON file.

        :param str config_filename: path to configuration file
        :return: config dictionary
        """
        if config_filename is None:
            config_filename = self.args.config_filename

        try:
            with open(config_filename) as fconf:
                self.config = json.load(fconf)
            db_config = self.config["database"]

            # Mandatory config options
            if self.MANDATORY_CONF - set(db_config.keys()) != set():
                raise ConfigError("Incorrect config file - mandatory configuration missing")

            return self.config
        except (FileNotFoundError, PermissionError, JSONDecodeError, KeyError, ConfigError) as err:
            logging.error(err)
            raise FatalScriptError(err)

    def connect_db(self):
        """Connect to the database using credentials from configuration.

        :return: connection object
        """
        try:
            return psycopg2.connect(**self.config["database"])
        except (OperationalError, InterfaceError) as err:
            logging.error("DB connection failed: " + str(err))
            raise FatalScriptError(err)


def add_months(cur_date, months):
    """Add given number of months to the current date.

    :param date cur_date: the date from which the shift is computed
    :param int months: number of months to be added to cur_date (can be negative)

    :return: cur_date + number of months, normalized to the first day of the month

    WARNING: Function throws away day from the date. It is necessary, because there is not clear what date
             should be result of operatin such as such day as
             February 31st and similar.
    """
    (year, month) = (cur_date.year, cur_date.month)
    month += months
    year += (month-1) // 12
    month = (month-1) % 12 + 1

    return date(year, month, 1)
