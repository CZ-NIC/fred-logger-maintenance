#!/usr/bin/env python3
#
# Copyright (C) 2017-2021  CZ.NIC, z. s. p. o.
#
# This file is part of FRED.
#
# FRED is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# FRED is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with FRED.  If not, see <https://www.gnu.org/licenses/>.

"""Script for creating new db partitions.

Creates partitions for given dates and service in logger database.

Run with -h option to print all available options.
"""
import argparse
import logging
import sys
from datetime import date

from psycopg2 import DatabaseError

from logger_maintenance.common import DateAction, FatalScriptError, LoggerMaintenanceScript, add_months


class CreatePartsScript(LoggerMaintenanceScript):
    """Script class for creating new db partitions."""

    def process_args(self, args):
        """Set up long opts and their default values."""
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-c", "--config_file", dest="config_filename", required=True,
            help="json config file"
        )
        parser.add_argument(
            "-d", "--from-date", dest="date_from", action=DateAction,
            help="YYYY-MM date of log partition to be deleted (or the first one to be deleted, "
                 "if --date_to is supplied)"
        )
        parser.add_argument(
            "--to-date", dest="date_to", action=DateAction,
            help="YYYY-MM date of last log partition to be deleted"
        )
        self.args = parser.parse_args(args)
        self._set_default_args()

    def _set_default_args(self):
        """Set default values in case that command line arguments are not supplied."""
        # If --from-date not set, add 1 month to the current date
        if self.args.date_from is None:
            self.args.date_from = add_months(date.today(), 1)

        # If --to-date not set, let it be equal to --from-date
        if self.args.date_to is None:
            self.args.date_to = self.args.date_from

        # --to-date cannot preceed --from-date
        if self.args.date_to < self.args.date_from:
            self.args.date_to = self.args.date_from

    def execute(self):
        """Create database partitions."""
        with self.connect_db() as conn:
            with conn.cursor() as cursor:
                try:
                    sql_func = cursor.mogrify(
                        "SELECT create_parts(%(from)s::timestamp, %(to)s::timestamp)",
                        {
                            'from': self.args.date_from.strftime("%Y-%m-01"),
                            'to': self.args.date_to.strftime("%Y-%m-01"),
                        }
                    )
                    logging.info(sql_func.decode())
                    cursor.execute(sql_func)

                except DatabaseError as err:
                    logging.error("DatabaseError: " + str(err))
                    conn.rollback()
                    raise FatalScriptError(err)
                else:
                    conn.commit()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        script = CreatePartsScript(sys.argv[1:])
        script.read_config()
        script.execute()
    except FatalScriptError:
        sys.exit(1)
