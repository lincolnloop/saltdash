from decimal import Decimal
from unittest import TestCase

from saltdash.dash.templatetags.dash_tags import pretty_time, clipped_page_range


class PrettyTimeTestCase(TestCase):

    def test_minutes(self):
        self.assertEqual(pretty_time(69305.23), "1:09.31 min")

    def test_seconds(self):
        self.assertEqual(pretty_time(20305.23), "20.31 sec")

    def test_milliseconds(self):
        self.assertEqual(pretty_time(305.23), "305 ms&nbsp;")


class ClippedPageRangeTestCase(TestCase):

    def test_long(self):
        clipped = clipped_page_range(list(range(1, 21)), 10)
        self.assertListEqual(clipped, [1, 2, None, 8, 9, 10, 11, 12, None, 19, 20])

    def test_short(self):
        clipped = clipped_page_range(list(range(1, 8)), 5)
        self.assertListEqual(clipped, [1, 2, 3, 4, 5, 6, 7])

    def test_left(self):
        clipped = clipped_page_range(list(range(1, 21)), 2)
        self.assertListEqual(clipped, [1, 2, 3, 4, None, 19, 20])

    def test_right(self):
        clipped = clipped_page_range(list(range(1, 21)), 18)
        self.assertListEqual(clipped, [1, 2, None, 16, 17, 18, 19, 20])
