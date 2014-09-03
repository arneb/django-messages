#!/usr/bin/env python
import os
import sys
from django import VERSION

sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.path.pardir))

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

    if VERSION < (1, 6):
        test_runners_args = {
            'TEST_RUNNER': 'discover_runner.DiscoverRunner',
        }
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
