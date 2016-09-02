from django.apps import AppConfig


class StorageConfig(AppConfig):

    name = 'django-mongo-storage'
    verbose_name = "Django-Mongo-Storage"

    def ready(self):
        import django_mongo_storage.signals



