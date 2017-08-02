#!/usr/bin/env python
import os
import sys
from django.conf import settings


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dj_torrent.tests.testproject.settings")
    if len(sys.argv) <= 1:
        from django.test.utils import get_runner
        import django
        django.setup()
        TestRunner = get_runner(settings)
        test_runner = TestRunner()
        result = test_runner.run_tests(["dj_torrent.tests"])
        return
    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        # The above import may fail for some other reason. Ensure that the
        # issue is really that Django is missing to avoid masking other
        # exceptions on Python 2.
        try:
            import django
        except ImportError:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            )
        raise
    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()
