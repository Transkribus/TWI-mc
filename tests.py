from .services import LazyJsonClient
from django.test import TestCase
import settings


class TestLazyJsonClient(TestCase):
    def setUp(self):
        pass

    def test_make_client(self):
        client = LazyJsonClient(settings.TRP_URL, headers={'Accept': 'application/json'})
        print("client: ",client)

    def test_auth(self):
        client = LazyJsonClient(settings.TRP_URL, headers={'Accept': 'application/json'})
        r = client.post_login('<valid_username>', '<valid_password>')
        self.assertEquals(r.firstname,'<users firstname')
        self.assertTrue('sessionId' in r)
        self.assertTrue('session_id' in r)

    def test_get_col_list(self):         
        client = LazyJsonClient(settings.TRP_URL, headers={'Accept': 'application/json'})
        r = client.post_login('<valid_username>', '<valid_password>')
        self.assertEquals(r.firstname,'<users firstname>')
        client._request_factory._cookies = {'JSESSIONID': r.sessionId}
        r = client.get_col_list()
        print(r)
        for i in r:
            print(i)


