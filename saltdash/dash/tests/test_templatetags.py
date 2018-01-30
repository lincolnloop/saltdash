from decimal import Decimal
from unittest import TestCase

from saltdash.dash.templatetags.dash_tags import pretty_time


class DashTagsTestCase(TestCase):

    def test_minutes(self):
        self.assertEqual(pretty_time(69305.23),
                         '1:09.31 min')

    def test_seconds(self):
        self.assertEqual(pretty_time(20305.23),
                         '20.31 sec')

    def test_milliseconds(self):
        self.assertEqual(pretty_time(305.23),
                         '305 ms&nbsp;')
