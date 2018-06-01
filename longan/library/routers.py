from django.conf import settings

class TranskribusRouter:

    DATABASE_NAME = 'UIBK'
    APP_NAME = 'collections'

    def db_for_read(self, model, **hints):

        if settings.DEBUG is True:
            return None

        if model._meta.app_label == self.APP_NAME:
            return self.DATABASE_NAME

        return None

    def db_for_write(self, model, **hints):
        # NOTE: no opinion results in default database being used
        return None

    def allow_relation(self, obj1, obj2, **hints):

        if settings.DEBUG is True:
            return None

        if obj1._meta.app_label == self.APP_NAME or \
           obj2._meta.app_label == self.APP_NAME:
           return True

        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):

        # NOTE: do not allow migrate on uibk db
        if db == self.DATABASE_NAME:
            return False

        return None
