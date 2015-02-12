# -*- encoding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import sys


os.environ['DJANGO_SETTINGS_MODULE'] = 'example_app.settings'
os.environ['DJANGO_SETTINGS_PROFILE'] = 'tests'

test_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, test_dir)


from django.conf import settings
from django.test.utils import get_runner


import django
if django.VERSION[1] >= 7:
    django.setup()


def runtests():
    test_runner = get_runner(settings)(verbosity=1, interactive=True)
    failures = test_runner.run_tests(['powerdns'])
    sys.exit(bool(failures))


if __name__ == '__main__':
    runtests()
