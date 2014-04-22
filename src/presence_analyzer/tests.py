# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
import os.path
import json
import datetime
import unittest

from presence_analyzer import main, views, utils


TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.csv'
)


# pylint: disable=E1103
class PresenceAnalyzerViewsTestCase(unittest.TestCase):
    """
    Views tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        self.client = main.app.test_client()

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_mainpage(self):
        """
        Test main page redirect.
        """
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)
        assert resp.headers['Location'].endswith('/presence_weekday.html')

    def test_api_users(self):
        """
        Test users listing.
        """
        resp = self.client.get('/api/v1/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 2)
        self.assertDictEqual(data[0], {u'user_id': 10, u'name': u'User 10'})

    def test_mean_time_weekday_view(self):
        """
        Test for view which returns mean presence time of given user grouped
        by weekday.
        """
        resp = self.client.get('/api/v1/mean_time_weekday/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 7)
        self.assertListEqual(
            data,
            [
                [u'Mon', 0],
                [u'Tue', 30047.0],
                [u'Wed', 24465.0],
                [u'Thu', 23705.0],
                [u'Fri', 0],
                [u'Sat', 0],
                [u'Sun', 0]
            ]
        )

        resp = self.client.get('/api/v1/mean_time_weekday/11')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 7)
        self.assertListEqual(
            data,
            [
                [u'Mon', 24123.0],
                [u'Tue', 16564.0],
                [u'Wed', 25321.0],
                [u'Thu', 22984.0],
                [u'Fri', 6426.0],
                [u'Sat', 0],
                [u'Sun', 0]
            ]
        )

    def test_presence_weekday_view(self):
        """
        Testing for view which returns total presence time of given user
        grouped by weekday.
        """
        resp = self.client.get('/api/v1/presence_weekday/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 8)
        self.assertListEqual(
            data,
            [
                [u'Weekday', u'Presence (s)'],
                [u'Mon', 0],
                [u'Tue', 30047],
                [u'Wed', 24465],
                [u'Thu', 23705],
                [u'Fri', 0],
                [u'Sat', 0],
                [u'Sun', 0],
            ]
        )

        resp = self.client.get('/api/v1/presence_weekday/11')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 8)
        self.assertListEqual(
            data,
            [
                [u'Weekday', u'Presence (s)'],
                [u'Mon', 24123],
                [u'Tue', 16564],
                [u'Wed', 25321],
                [u'Thu', 45968],
                [u'Fri', 6426],
                [u'Sat', 0],
                [u'Sun', 0],
            ]
        )


class PresenceAnalyzerUtilsTestCase(unittest.TestCase):
    """
    Utility functions tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_get_data(self):
        """
        Test parsing of CSV file.
        """
        data = utils.get_data()
        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11])
        sample_date = datetime.date(2013, 9, 10)
        self.assertIn(sample_date, data[10])
        self.assertItemsEqual(data[10][sample_date].keys(), ['start', 'end'])
        self.assertEqual(data[10][sample_date]['start'],
                         datetime.time(9, 39, 5))

    def test_group_by_weekday(self):
        """
        Test of group_by_weekday
        """
        self.assertDictEqual(
            utils.group_by_weekday(utils.get_data()[10]),
            {
                0: [],
                1: [30047],
                2: [24465],
                3: [23705],
                4: [],
                5: [],
                6: []
            }
        )

        self.assertDictEqual(
            utils.group_by_weekday(utils.get_data()[11]),
            {
                0: [24123],
                1: [16564],
                2: [25321],
                3: [22969, 22999],
                4: [6426],
                5: [],
                6: []
            }
        )

    def test_seconds_since_midnight(self):
        """
        Test of seconds_since_midnight.
        """
        self.assertEqual(
            utils.seconds_since_midnight(datetime.time(13, 37, 0)),
            13*60*60 + 37*60)

    def test_interval(self):
        """
        Test of interval
        """
        self.assertEquals(
            utils.interval(datetime.time(0, 0, 0), datetime.time(0, 30, 0)),
            30*60
        )

        self.assertEquals(
            utils.interval(datetime.time(0, 0, 0), datetime.time(12, 00, 0)),
            12*60*60
        )

        self.assertEquals(
            utils.interval(datetime.time(9, 0, 0), datetime.time(17, 00, 0)),
            8*60*60
        )

    def test_mean(self):
        """
        Test of utils.mean
        """

        self.assertEquals(utils.mean([5, 8, 7, 5, 7, 7]), 6.5)
        self.assertEquals(utils.mean([]), 0)
        self.assertEquals(utils.mean([8, 8, 8, -8, -16, 0]), 0)


def suite():
    """
    Default test suite.
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PresenceAnalyzerViewsTestCase))
    suite.addTest(unittest.makeSuite(PresenceAnalyzerUtilsTestCase))
    return suite


if __name__ == '__main__':
    unittest.main()
