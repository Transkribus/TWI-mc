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
        assert isinstance(data, dict), type(data)
        self._data = data

    def __contains__(self, key):
        if '_' in key:
            return camelize(key) in self._data
        return key in self._data

    def __getattr__(self, key):
        if self._data is None:
            self._data = self._req.execute()

        if '_' in key:
            camelized = camelize(key)
        else:
            camelized = key

        if camelized not in self._data:
            raise AttributeError(key)

        return self._data[camelized]

    def get(self, key, default=None):
        try:
            return self.__getattr__(key)
        except AttributeError:
            return default

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

        self._url = base_url.rstrip('/')

        if not isinstance(headers, dict):
            headers = {}

        # NOTE: do not remove this, ambiguous Accept header might result
        assert all(key.istitle() for key in headers)

        headers.update({'Accept': 'application/json'})

        self._request_factory = LazyJsonRequestFactory(headers)
        self._list_class = LazyList
        self._object_class = LazyObject
        self._headers = headers

        self.__assert()

    def __assert(self):
        u = parse.urlsplit(self._url)
        assert u.scheme in ('http', 'https')
        assert u.netloc

    def _build_url(self, path):

        assert not self._url.endswith('/'), self._url
        assert path.startswith('/'), path

        return self._url + path

    def _build_object(self, method, path, data=None):
        return self._object_class(
            self._request_factory(
                method, self._build_url(path), data=data, headers=self._headers))
        
    def _build_list(self, method, path):
        return self._list_class(
            self._request_factory(
                method, self._build_url(path), headers=self._headers))

    def _build_list_with_count(self, method, paths):

        list_, count = paths

        return LazyListWithCount(
            CompositeRequest(
                list_=self._request_factory(
                    method, self._build_url(list_), headers=self._headers),
                count=self._request_factory(
                    method, self._build_url(count), headers=self._headers)
            )
        )

    def set_header_default(self, key, value):
        self._headers[key] = value

    def post_login(self, username, password):
        assert username and password
        return self._build_object('POST', '/auth/login', {
            'user': username,
            'pw': password
        })

    def get_col_list(self, **kwargs):
        if len(kwargs) > 0:
            warnings.warn("Sorting not implemented")
        return self._build_list_with_count('GET', [
            '/collections/list', '/collections/count'])

    def get_doc_list(self, col_id):
        assert isinstance(col_id, int)
        return self._build_list_with_count('GET', [
            '/collections/%d/list' % col_id,
            '/collections/%d/count' % col_id
        ])

    def get_doc_meta_data(self, col_id, doc_id):
        return self._build_object('GET', '/collections/%d/%d/metadata' % (col_id, doc_id))


class Request:

    def __init__(self, *args, **kwargs):
        raise NotImplemented

    def execute(self):
        raise NotImplemented

    def __repr__(self):
        raise NotImplemented


class CompositeRequest(Request):

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class LazyJsonRequest(Request):

    def __init__(self, method, url, **kwargs):
        self._method = method
        self._url = url
        self._kwargs = kwargs
        self._result = None

    def execute(self, params=None ):

        if self._result is not None:
            return self._result

        r = requests.request(self._method, self._url, params=params, **self._kwargs)
        r.raise_for_status()

        self._result = r.json()
        return self._result

    def __repr__(self):
        return '<%r: {"url": %r}>' % (self.__class__.__name__, self._url);


class List:

    def __init__(self, *args, **kwargs):
        raise NotImplemented

    def __iter__(self):
        raise NotImplemented

    def __getitem__(self, maybe_slice):
        raise NotImplemented

    def __len__(self):
        raise NotImplemented


class LazyList(List):

    def __init__(self, request):
        self._req = request

    def __iter__(self):
        warnings.warn("Iterating over *all* list items ...")
        return (CamelCaseDict(data) for data in self._req.execute())

    def __getitem__(self, maybe_slice):
        raise NotImplemented

    def __len__(self):
        raise NotImplemented


class LazyListWithCount(List):

    def __init__(self, request):
        self._req = request

    def __iter__(self):
        warnings.warn("Iterating over *all* list items ...")
        return (CamelCaseDict(data) for data in self._req.list_.execute())

    def __getitem__(self, maybe_slice):

        if not isinstance(maybe_slice, slice):
            raise NotImplementedError
        slice_ = maybe_slice

        if None in (slice_.start, slice_.stop):
            raise NotImplementedError("Index must be of type %r" % int)

        items = self._req.list_.execute({
            'index': slice_.start,
            'nValues': slice_.stop - slice_.start
        })

        assert isinstance(items, (tuple, list))

        return [CamelCaseDict(data) for data in items]

    def __len__(self):
        return self._req.count.execute()


class LazyObject(CamelCaseDict):

    def __init__(self, request):
        self._req = request
        self._data = None


class Helpers:

    @staticmethod
    def get_session_id(req):
        return getattr(req.user.tsdata, 'session_id', getattr(
            req.user.tsdata, 'sessionId'))

    @staticmethod
    def create_client_from_request(req):
        from django.conf import settings

        if req.GET.get('test') != '1':
            assert hasattr(settings, 'TRP_URL')
            session_id = Helpers.get_session_id(req)
            return LazyJsonClient(settings.TRP_URL, {'Cookie': 'JSESSIONID=%s' % session_id})

        # prepare test client

        from unittest import mock
        MockClient = mock.Mock()

        class DocumentList:
            def __slice__(self, *args, **kwargs):
                return DOC_LIST
            def __len__(self):
                return 100

        class CollectionList:
            def __slice__(self, *args, **kwargs):
                return COL_LIST
            def __len__(self):
                    return 100

        DOC_LIST = [
            CamelCaseDict({
                'docId': 1,
                'title': 'Test Document',
                'nrOfPages': 132,
            })
        ] * 100

        COL_LIST = [
            CamelCaseDict({
                'colId': 1,
                'colName': 'Test Collection',
                'descr': "Descripton for Test Collection",
                'nrOfDocuments': 42,
                'role': 'Reader'
            })
        ] * 100

        MockClient.get_col_list.return_value = COL_LIST
        MockClient.get_doc_list.return_value = COL_LIST

        return MockClient
