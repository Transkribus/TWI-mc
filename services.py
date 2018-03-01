import warnings
import functools

from urllib import parse
import requests

@functools.lru_cache(maxsize=256)
def camelize(string):
    return ''.join(
        s.title() if i > 0 else s
        for i, s in enumerate(string.split('_'))
    )


class CamelCaseDict:

    def __init__(self, data):
        assert isinstance(data, dict)
        self._data = data

    def __contains__(self, key):
        if '_' in key:
            return camelize(key) in self._data
        return key in self._data

    def __getattr__(self, key):
        if self._data is None:
            self._data = self._req.execute()

        if '_' in key:
            return self._data[camelize(key)]

        return self._data.get(key)

    def __repr__(self):
        return "<%r: %s>" % (self.__class__.__name__, repr(self._data))


class LazyJsonRequestFactory:

    def __init__(self, headers=None, cookies=None):

        if isinstance(headers, dict):
            self._headers = headers
        else:
            self._headers = {}

        if isinstance(cookies, dict):
            self._cookies = cookies
        else:
            self._cookies = None

    def make(self, method, url, **kwargs):

        params = {}

        if self._headers:
            params['headers'] = self._headers.copy()

        if 'headers' in kwargs:
            params['headers'].update(kwargs.pop('headers'))

        params.update(kwargs)

        if self._cookies:
            params['cookies'] = self._cookies

        return LazyJsonRequest(method, url, **params)

    def __call__(self, *args, **kwargs):
        return self.make(*args, **kwargs)


class LazyJsonClient:

    def __init__(self, base_url, headers=None):

        self._url = base_url

        if isinstance(headers, dict):
            self._headers = headers
        else:
            self._headers = {}

        self._request_factory = LazyJsonRequestFactory(headers)
        self._list_class = LazyList
        self._object_class = LazyObject

        self.__assert()

    def __assert(self):
        u = parse.urlsplit(self._url)
        assert u.scheme in ('http', 'https')
        assert u.netloc

    def _build_url(self, path):
        return parse.urljoin(self._url, path)

    def _build_object(self, method, path, data=None):
        return self._object_class(
            self._request_factory(
                method, self._build_url(path), data=data, headers=self._headers))
        
    def _build_list(self, method, path):
        return self._list_class(
            self._request_factory(
                method, self._build_url(path), headers=self._headers))

    def set_header_default(self, key, value):
        self._headers[key] = value

    def post_login(self, username, password):
        assert username and password
        return self._build_object('POST', 'auth/login', {
            'user': username,
            'pw': password
        })

    def get_col_list(self):
        return self._build_list('GET', 'collections/list')

    def get_doc_list(self, col_id):
        return self._build_list('GET', 'collections/%d/list' % col_id)

    def get_doc_meta_data(self, col_id, doc_id):
        return self._build_object('GET', 'collections/%d/%d/metadata' % (col_id, doc_id))


class LazyJsonRequest:

    def __init__(self, method, url, **kwargs):
        self._method = method
        self._url = url
        self._kwargs = kwargs

    def execute(self, params=None ):
        r = requests.request(self._method, self._url, params=params, **self._kwargs)
        r.raise_for_status()

        return r.json()

    def __repr__(self):
        return '<%r: {"url": %r}>' % (self.__class__.__name__, self._url);


class LazyList:

    def __init__(self, request):
        self._req = request
        self._items = None

    def __iter__(self):
        warnings.warn("Iterating over *all* list items ...")
        return (CamelCaseDict(data) for data in self._req.execute())

    def __getitem__(self, maybe_slice):
        if not isinstance(maybe_slice, slice):
            raise NotImplementedError
        slice_ = maybe_slice

        if None in (slice_.start, slice_.stop):
            raise NotImplementedError("Index must be of type %r" % int)

        self._items = self._req.execute({
            'index': slice_.start,
            'nValues': slice_.stop - slice_.start
        })

        assert isinstance(self._items, (tuple, list))

        return [CamelCaseDict(data) for data in self._items]


class LazyObject(CamelCaseDict):

    def __init__(self, request):
        self._req = request
        self._data = None

def main():

    from mock import requests

    import logging

    logging.basicConfig(level=logging.INFO)

    req = LazyJsonRequest('GET', 'https://whatever.org/collections/list')

    print(req)

    req.execute()

    factory = LazyJsonRequestFactory()

    req = factory.make('GET', 'https://whatever.org/collections/list')

    lazy_list = LazyList(req)
    r = lazy_list[0:1]

    for i in r:
        print(i.url)

        try:
            i.does_not_exist
        except KeyError:
            pass
        else:
            assert False, "Should have thrown an exception"

    print(r)

    client = LazyJsonClient('https://api.example.org', headers={'Accept': 'application/json'})
    r = client.get_col_list()

    for i in r:
        print(i.url)

    r = client.get_doc_list(2805)

    r = client.post_login('john.doe', 1243)
    print(r)

    print(r.firstname)

    print(r.sessionId)
    print(r.session_id)

    print('session_id' in r)    


    r = client.get_doc_meta_data(2805, 6320)
    r.meh

    return

    s = LazyList(request)
    print(s[0:5])
    print(s[0:10])
    print(s[10:20])

    print(s[50:60])


    print(s[95:100])
    print(s[95:105])
    print(s[95:1000])
    print(s[95:1000])

    o = LazyObject()

    print(o.value)

    try:
        print(o.meh)
    except AttributeError as e:
        print(e)

if __name__ == '__main__':
    main()
