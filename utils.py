from django.test.runner import DiscoverRunner


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
