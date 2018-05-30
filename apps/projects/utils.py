from django.test.runner import DiscoverRunner

import collections

PAGE_STATE = {
    'NEW': "new",
    'IN_PROGRESS': "in progress",
    'DONE': "ready for review",
    'FINAL': "completed",
    'GT': "completed"
}

class Stats:

    NAMES = PAGE_STATE

    def __init__(self, data):
        self._data = data

    @property
    def progress(self):
        return self._calculate_progress(self._data, self.NAMES)

    def _calculate_progress(self, data, names):

        counts = collections.OrderedDict({
            'NEW': data.get('nrOfNew', 0),
            'IN_PROGRESS': data.get('nrOfInProgress', 0),
            'DONE': data.get('nrOfDone', 0),
            'FINAL': data.get('nrOfFinal', 0) + data.get('nrOfGT', 0),
            # 'GT': data.nr_of_G_T
        })

        total = sum(counts.values())

        return [
            {
                'class_name': '-'.join(name.split('_')).lower(),
                'name': names[name].title(),
                'count': value,
                'percent': 0 if total == 0 else round(100 * value / total, 1),
            } for name, value in counts.items()
        ]


class PageList:

    def __init__(self, data):
        self._data = data

    def _get_most_recent_transcript(self, data):
        return data['tsList']['transcripts'][0]

    def _extract(self, page_data):
        data = self._get_most_recent_transcript(page_data)

        progress = [
            {
                'class_name': 'transcribed',
                'name': "Transcribed",
                'count': data['nrOfTranscribedLines'],
                'percent': 0 if data.get('nrOfLines', 0) == 0 else round(100 * data['nrOfTranscribedLines'] / data['nrOfLines'], 1)
            },
            {
                'class_name': 'not-transcribed',
                'name': "Not Yet Transcribed",
                'count': data.get('nrOfLines') - data.get('nrOfTranscribedLines'),
                'percent': 0 if data.get('nrOfLines', 0) == 0 else round(100 * (data['nrOfLines'] - data['nrOfTranscribedLines']) / data['nrOfLines'], 1)
            }
        ]

        return {
            'id': page_data['pageNr'],
            'num': page_data['pageNr'],
            'status': PAGE_STATE[data['status']].title(),
            'user': data['userName'] if not '@' in data['userName'] else data['userName'][:data['userName'].index('@')],
            'num_lines_total': data['nrOfLines'],
            'num_lines_done': data['nrOfTranscribedLines'],
            'progress': progress
        }

    def __iter__(self):
        return (
            self._extract(page_data)
            for page_data in self._data['pageList']['pages']
        )

class UnManagedModelTestRunner(DiscoverRunner):

    # http://blog.birdhouse.org/2015/03/25/django-unit-tests-against-unmanaged-databases
    # https://dev.to/patrnk/testing-against-unmanaged-models-in-django

    def setup_test_environment(self, *args, **kwargs):
        from django.apps import apps
        self.unmanaged_models = [m for m in apps.get_models() if not m._meta.managed]
        for m in self.unmanaged_models:
            m._meta.managed = True

        super(UnManagedModelTestRunner, self).setup_test_environment(*args, **kwargs)

    def teardown_test_environment(self, *args, **kwargs):
        super(UnManagedModelTestRunner, self).teardown_test_environment(*args, **kwargs)
        # reset unmanaged models
        for m in self.unmanaged_models:
            m._meta.managed = False
