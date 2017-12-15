"""Test module for logger-maintenance."""

import json
import sys
import unittest.mock as mock
from datetime import date
from io import StringIO
from unittest import TestCase
from unittest.mock import patch

from psycopg2 import DatabaseError, InterfaceError
from testfixtures import LogCapture

from create_parts import CreatePartsScript
from drop_parts import DropPartsScript
from logger_maintenance.common import ConfigError, FatalScriptError, add_months


class AddMonthTestCase(TestCase):
    """Test class for add_month function."""

    def test_add_month(self):
        """Test add_month function."""
        d = date(2017, 10, 31)

        self.assertEqual(add_months(d, 15), date(2019, 1, 1))
        self.assertEqual(add_months(d, -22), date(2015, 12, 1))
        self.assertEqual(add_months(d, 0), date(2017, 10, 1))


@patch('drop_parts.sys.stdout', new=StringIO())
@patch('create_parts.sys.stdout', new=StringIO())
class ScriptTestCase(object):
    """Common tests for all scripts."""

    script_args = []
    script_class = None

    @patch('drop_parts.sys.stderr', new=StringIO())
    @patch('create_parts.sys.stderr', new=StringIO())
    def test_init_fail(self):
        """Test init with wrong arguments."""
        with self.assertRaises(SystemExit):
            self.script_class([])
        self.assertRegex(sys.stderr.getvalue().strip(), "^usage: ")
        with self.assertRaises(FatalScriptError):
            with self.assertRaises(ValueError):
                self.script_class(self.script_args + ["-d", "0000-00-00"])

    def test_init_ok(self):
        """Test standard init."""
        self.script_class(self.script_args)

    @patch('builtins.open', mock.mock_open(read_data='foo\nbar\nbaz\n'))
    def test_config_wrong_json(self):
        """Test wrong format of configuration file."""
        with self.assertRaises(FatalScriptError) as err:
            script = self.script_class(self.script_args)
            script.read_config()
        self.assertEqual(type(err.exception.error), json.JSONDecodeError)

    @patch('builtins.open', mock.mock_open(read_data='{"database": {"host": "host", "user": "user"}}'))
    def test_config_missing_items(self):
        """Test configuration file in right format, but with mandatory items missing."""
        with self.assertRaises(FatalScriptError) as err:
            script = self.script_class(self.script_args)
            script.read_config()
        self.assertEqual(type(err.exception.error), ConfigError)

    @patch('builtins.open',
           mock.mock_open(read_data='{"database": {"host": "myhost", "user": "myuser", "database": "db"}}'))
    def test_config_ok(self):
        """Test that configuration loaded properly."""
        script = self.script_class(
            self.script_args + ["--from-date", "2017-06", "--to-date", "2015-01"]
        )
        script.read_config()
        self.assertEqual(script.args.date_from, date(2017, 6, 1))
        self.assertEqual(script.args.date_to, date(2017, 6, 1))
        self.assertEqual(script.config["database"]["host"], "myhost")

    @patch('psycopg2.connect')
    @patch('builtins.open',
           mock.mock_open(read_data='{"database": {"host": "myhost", "user": "myuser", "database": "db"}}'))
    def test_db_ok(self, mock_connect):
        """Test OK connection to database."""
        script = self.script_class(self.script_args)
        script.read_config()
        script.connect_db()

    @patch('psycopg2.connect', side_effect=InterfaceError('if_error'))
    @patch('builtins.open',
           mock.mock_open(read_data='{"database": {"host": "myhost", "user": "myuser", "database": "db"}}'))
    def test_db_error(self, mock_connect):
        """Test error while connecting to database."""
        script = self.script_class(self.script_args)
        script.read_config()
        with self.assertRaises(FatalScriptError) as err:
            script.connect_db()
        self.assertEqual(type(err.exception.error), InterfaceError)


class DropPartsScriptTestCase(ScriptTestCase, TestCase):
    """Test class for DropPartsScript."""

    def setUp(self):
        """Set default args and set up log handler."""
        self.script_args = ["-c", "whatever", "-s", "mojeid"]
        self.script_class = DropPartsScript

        self.log_handler = LogCapture()

    def tearDown(self):
        """Throw away log handler."""
        self.log_handler.uninstall()

    @patch('psycopg2.connect')
    @patch('builtins.open',
           mock.mock_open(read_data='{"database": {"host": "myhost", "user": "myuser", "database": "db"}}'))
    def execute(self, result, error, mock_connect):
        """Call script execute function with various results and/or errors."""
        mock_cursor = mock_connect().__enter__().cursor().__enter__()
        mock_cursor.fetchone.return_value = result
        if error is not None:
            mock_cursor.execute.side_effect = error

        script = DropPartsScript(self.script_args + ["-d", "2054-01"])
        script.read_config()

        if error is not None:
            with self.assertRaises(FatalScriptError) as err:
                script.execute()
            self.assertEqual(type(err.exception.error), error)
        else:
            script.execute()

            mock_cursor.mogrify.assert_called_once_with(
                "SELECT drop_parts(%(from)s::timestamp, %(to)s::timestamp, %(service)s, %(dry_run)s)",
                {
                    'from': '2054-01-01',
                    'to': '2054-01-01',
                    'service': 'mojeid',
                    'dry_run': False
                }
            )

            mock_cursor.execute.assert_called_with(mock_cursor.mogrify.return_value)

    def test_execute_ok(self):
        """Test execute() that deleted some parts."""
        self.execute(["sql_1\nsql_2"], None)

    def test_execute_empty(self):
        """Test execute() that didn't delete any parts."""
        self.execute([""], None)

    def test_execute_error(self):
        """Test execute() that throws DatabaseError."""
        self.execute([""], DatabaseError)

    @patch('drop_parts.sys.stdout', new=StringIO())
    @patch('psycopg2.connect')
    @patch('builtins.open',
           mock.mock_open(read_data='{"database": {"host": "myhost", "user": "myuser", "database": "db"}}'))
    def test_list_services(self, mock_connect):
        """Test listing services when --service argument missing."""
        script = self.script_class(["-c", "whatever.conf"])
        script.read_config()
        script.list_services()
        self.assertRegex(sys.stdout.getvalue().strip(), "^You have to pass ")


class CreatePartsScriptTestCase(ScriptTestCase, TestCase):
    """Test class for CreatePartsScript."""

    def setUp(self):
        """Set default args and set up log handler."""
        self.script_args = ["-c", "whatever"]
        self.script_class = CreatePartsScript

        self.log_handler = LogCapture()

    def tearDown(self):
        """Throw away log handler."""
        self.log_handler.uninstall()

    @patch('psycopg2.connect')
    @patch('builtins.open',
           mock.mock_open(read_data='{"database": {"host": "myhost", "user": "myuser", "database": "db"}}'))
    def execute(self, error, mock_connect):
        """Call script execute function with various results and/or errors."""
        mock_cursor = mock_connect().__enter__().cursor().__enter__()
        mock_cursor.fetchall.return_value = [["table_1"], ["table_2"]]
        if error is not None:
            mock_cursor.execute.side_effect = error

        script = CreatePartsScript(self.script_args + ["-d", "2054-01"])
        script.read_config()
        script.connect_db()

        if error is not None:
            with self.assertRaises(FatalScriptError) as err:
                script.execute()
            self.assertEqual(type(err.exception.error), error)
        else:
            script.execute()
            mock_cursor.mogrify.assert_any_call(
                "SELECT create_parts(%(from)s::timestamp, %(to)s::timestamp)",
                {
                    'from': '2054-01-01',
                    'to': '2054-01-01',
                }
            )
            mock_cursor.mogrify.assert_any_call(
                "GRANT SELECT ON %(table)s TO view",
                {'table': 'table_1'}
            )
            mock_cursor.mogrify.assert_any_call(
                "GRANT SELECT ON %(table)s TO view",
                {'table': 'table_2'}
            )

    def test_execute_ok(self):
        """Test execute() that runs OK."""
        self.execute(None)

    def test_execute_error(self):
        """Test execute() that throws DatabaseError."""
        self.execute(DatabaseError)
