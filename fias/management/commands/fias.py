#coding: utf-8
from __future__ import unicode_literals, absolute_import

import sys
from optparse import make_option

from django.core.management.base import BaseCommand

from fias.models import Status
from fias.management.utils.database import fill_database, update_database


class Command(BaseCommand):
    help = 'Fill or update FIAS database'
    usage_str = 'Usage: ./manage.py fias [--file <filename>|--remote-file] [--force-replace] [--really-replace] [--update [--skip]]'

    option_list = BaseCommand.option_list + (
        make_option('--file', action='store', dest='file', default=None,
            help='Load file into DB'),
        make_option('--remote-file', action='store_true', dest='remote', default=False,
            help='Download full archive and load it into DB'),
        make_option('--force-replace', action='store_true', dest='force', default=False,
            help='Force replace database'),
        make_option('--really-replace', action='store_true', dest='really', default=False,
            help='If data exist in any table, you should confirm their removal and replacement, as this may result in the removal of related data from other tables!'),
        make_option('--update', action='store_true', dest='update', default=False,
            help='Fetch `ver` and load into db'),
        make_option('--skip', action='store_true', dest='skip', default=False,
            help='Пропускать битые дельта-архивы при обновлении'),
    )

    def handle(self, *args, **options):
        remote = options.pop('remote')
        force = options.pop('force')
        really = options.pop('really')
        update = options.pop('update')
        skip = options.pop('skip')

        _file = options.pop('file') if not remote else None

        if _file is None and not remote and not update:
            self.error(self.usage_str)

        if (_file or remote) and Status.objects.count() > 0 and not really:
            self.error('One of the tables contains data. Truncate all FIAS tables manually '
                       'or enter key --really-replace, to clear the table by means of Django ORM')

        if force:
            Status.objects.all().delete()

        if _file or remote:
            fill_database(_file)

        if update:
            print ('Database updating...')
            update_database(skip)

    def error(self, message, code=1):
        print(message)
        sys.exit(code)