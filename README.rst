==================
Logger-maintenance
==================

FRED utilities: Scripts for audit-log database maintanence.

Project contains scripts for database partitions manipulation in logger component.

Contained scripts
=================

**create_parts.py**


* Creates partitions for given dates in logger database.

**drop_parts.py**


* Deletes partitions for given dates and service in logger database.
* Usable i.e. for deleting old logs from ``mojeid``.

**Command line options**


* ``-c``, ``--config-file``
  Path to configuration file (see *JSON configuration*).
* ``-d``, ``--from-date``
  Date from which should be partitions created / deleted.
* ``--to-date``
  Date to which should be partitions created / deleted.
  If ommited, ``--from-date`` is used.
* ``-s``, ``--service``
  Name of service whose logs are to be deleted (``drop_parts.py`` only).
* ``--dry-run``
  Doesn't make changes to database, just prints SQL that would be executed
  (``drop_parts.py`` only).

JSON configuration
==================

Example configurations is available in ``logger.conf.example``. Available
configuration items:

.. code-block:: json

    {
        "database": {
            "host": ...,
            "port": ...,
            "user": ...,
            "database": ...,
            "password": ...
        }
    }

The ``host``, ``user`` and ``database`` items are mandatory. Script will use
password from ``.pgpass`` if ``password`` is omitted.
