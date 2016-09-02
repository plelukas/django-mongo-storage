from django.db import models
from mock import mock

from django_mongo_storage.fields import MongoFileField
from django_mongo_storage.utils.storage import MongoStorage

try:
    from PIL import Image
except ImportError:
    Image = None

class Document(models.Model):
    myfile = MongoFileField(MongoStorage(db_alias='Test', collection='test'))

    objects = mock.Mock()


# # if Pillow available
# if Image:
#

