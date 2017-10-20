#!/usr/bin/env python3
"""Script for deleting old service logs.

Deletes partitions for given dates and service in logger database.
Usable i.e. for deleting old logs from `mojeid`.

Run with -h option to print all available options.
"""
import argparse
import logging
import sys
from datetime import date

from psycopg2 import DatabaseError

from logger_maintenance.common import DateAction, FatalScriptError, LoggerMaintenanceScript, add_months


class DropPartsScript(LoggerMaintenanceScript):
    """Script class for deleting old service logs."""

    def process_args(self, args):
        """Set up long opts and their default values."""
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-c", "--config_file", dest="config_filename", required=True,
            help="json config file"
        )
        parser.add_argument(
            "-s", "--service",
            help="service name (i.e. `mojeid`)"
        )
        parser.add_argument(
            "-d", "--from-date", dest="date_from", action=DateAction,
            help="YYYY-MM date of log partition to be deleted (or the first one to be deleted, "
                 "if --date_to is supplied)",
        )
        parser.add_argument(
            "--to-date", dest="date_to", action=DateAction,
            help="YYYY-MM date of last log partition to be deleted"
        )
        parser.add_argument(
            "--dry-run", dest="dry_run", action='store_true',
            help="Just echo the SQL commands to be executed"
        )
        self.args = parser.parse_args(args)
        self._set_default_args()

    def _set_default_args(self):
        """Set default values in case that command line arguments are not supplied."""
        # If --from-date not set, substract 6 months from the current date
        if self.args.date_from is None:
            self.args.date_from = add_months(date.today(), -6)

        # If --to-date not set, let it be equal to --from-date
        if self.args.date_to is None:
            self.args.date_to = self.args.date_from

        # --to-date cannot preceed --from-date
        if self.args.date_to < self.args.date_from:
            self.args.date_to = self.args.date_from

    def list_services(self):
        """List available services."""
        with self.connect_db() as conn:
            with conn.cursor() as cursor:
                try:
                    # NOTE: The `service` table was not originally designed for providing list of
                    # services and may change in the future. We need to strip trailing underscore
                    # from the `partition_postfix` column.
                    cursor.execute(
                        "SELECT trim(trailing '_' from partition_postfix), name FROM service ORDER BY id"
                    )
                except DatabaseError as err:
                    logging.error("DatabaseError: " + str(err))
                    conn.rollback()
                    raise FatalScriptError(err)
                else:
                    print("You have to pass -s/--service argument. Available choices:")
                    services = cursor.fetchall()
                    for name, description in services:
                        print("  {:15}{}".format(name, description))

    def execute(self):
        """Drop database partitions."""
        if self.args.dry_run:
            logging.info("=== DRY-RUN ===")

        with self.connect_db() as conn:
            with conn.cursor() as cursor:
                try:
                    sql = cursor.mogrify(
                        "SELECT drop_parts(%(from)s::timestamp, %(to)s::timestamp, %(service)s, %(dry_run)s)",
                        {
                            'from': self.args.date_from.strftime("%Y-%m-01"),
                            'to': self.args.date_to.strftime("%Y-%m-01"),
                            'service': self.args.service,
                            'dry_run': self.args.dry_run
                        }
                    )
                    logging.info(sql.decode())
                    cursor.execute(sql)

                except DatabaseError as err:
                    logging.error("DatabaseError: " + str(err))
                    conn.rollback()
                    raise FatalScriptError(err)
                else:
                    queries = cursor.fetchall()
                    if queries:
                        for (query,) in queries:
                            logging.info(query)
                    else:
                        logging.info("No such partitions")

                    if self.args.dry_run:
                        conn.rollback()
                    else:
                        conn.commit()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        script = DropPartsScript(sys.argv[1:])
        script.read_config()
        if script.args.service is not None:
            script.execute()
        else:
            script.list_services()
    except FatalScriptError:
        sys.exit(1)
