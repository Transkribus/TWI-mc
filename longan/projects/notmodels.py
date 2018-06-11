class Collection:

    def __init__(self, data):
        self._data = data

    @property
    def name(self):
        return self._data['col_name']

    @property
    def id(self):
        return self._data['col_id']

    @property
    def description(self):
        return self._data['description']

    def num_docs(self):
        return self._data['nr_of_documents']

    @property
    def thumb_url(self):
        return self._data.get('thumb_url')
        
    @property
    def project(self):
        return Project(self._data['crowd_project'])


class Project:

    def __init__(self, data):
        self._data = data
