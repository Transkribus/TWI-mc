import os
import unittest

from django.test import TestCase
from django.conf import settings


class TestServices(TestCase):

    def setUp(self):
        pass

    def test_camel_case_dict(self):

        from .services import CamelCaseDict

        o = CamelCaseDict({'value': 42})

        self.assertEqual(o.value, 42)

        with self.assertRaises(AttributeError):
            o.does_not_exist

    def test_lazy_list_with_count(self):

        from .services import LazyListWithCount, CompositeRequest

        n_items = 100
        items = list({'colId': i, 'colName': str(i)} for i in range(n_items))

        is_executed = {}

        class Request:
            pass

        class List(Request):
            def execute(self, params):
                index, length = params.pop('index'), params.pop('nValues')
                r = items[index:index + length]
                is_executed[List] = True
                return r

        class Count(Request):
            def execute(self):
                is_executed[Count] = True
                return len(items)

        is_executed[List] = is_executed[Count] = False

        lazy_list = LazyListWithCount(CompositeRequest(list_=List(), count=Count()))

        self.assertFalse(is_executed[List])
        self.assertFalse(is_executed[Count])

        expected = 10
        page_size = 10

        results = lazy_list[10:10 + page_size]

        self.assertEqual(len(results), expected)

        self.assertEqual(min(results, key=lambda i: i.col_id).col_id, 10)
        self.assertEqual(max(results, key=lambda i: i.col_id).col_id, 19)

        self.assertEqual(len(lazy_list), n_items)

        self.assertTrue(is_executed[Count])

    @unittest.skip("username and password required")
    def test_make_client(self):

        from .services import LazyJsonClient

        client = LazyJsonClient(settings.TRP_URL, headers={'Accept': 'application/json'})

    @unittest.skip("username and password required")
    def test_auth(self):

        from .services import LazyJsonClient

        client = LazyJsonClient(settings.TRP_URL, headers={'Accept': 'application/json'})
        r = client.post_login(os.environ['USERNAME'], os.environ['PASSWORD'])
        self.assertTrue('session_id' in r)

    @unittest.skip("username and password required")
    def test_get_col_list(self):         

        from .services import LazyJsonClient

        client = LazyJsonClient(settings.TRP_URL)
        r = client.post_login(os.environ['USERNAME'], os.environ['PASSWORD'])

        headers = {
            'Cookie': 'JSESSIONID=%s' % r.sessionId
        }

        client = LazyJsonClient(settings.TRP_URL, headers=headers)

        # client._request_factory._cookies = {'JSESSIONID': r.sessionId}
        r = client.get_col_list()

        self.assertGreater(len(r), 0)

class TestPagination(TestCase):

    @unittest.skip("check if django paginator sanitizes page_size param")
    def test_page_size_is_none(self):

        from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger        

        p = Paginator(list(range(100)), -10)

        self.assertLess(p.count, 100)
