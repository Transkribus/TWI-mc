from django.conf import settings

class TranskribusRouter:

    DATABASE_NAME = 'UIBK'
    APP_NAME = 'library'

    def db_for_read(self, model, **hints):

        if settings.DEBUG == True:
            return False

        if model._meta.app_label == self.APP_NAME:
            return self.DATABASE_NAME
        return None

    def db_for_write(self, model, **hints):

        if settings.DEBUG == True:
            return False

        if model._meta.app_label == self.APP_NAME:
            return self.DATABASE_NAME
        return None

    def allow_relation(self, obj1, obj2, **hints):

        if settings.DEBUG == True:
            return False

        if obj1._meta.app_label == self.APP_NAME or \
           obj2._meta.app_label == self.APP_NAME:
           return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):

        if settings.DEBUG == True:
            return False

        if app_label == self.APP_NAME:
            return db == self.DATABASE_NAME
        return None
