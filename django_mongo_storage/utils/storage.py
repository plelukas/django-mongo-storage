import logging
import os

from urllib.parse import urljoin
from bson import ObjectId

from django.conf import settings
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible

from mongoengine.connection import get_db
from mongoengine.fields import GridFSProxy

logger = logging.getLogger(__name__)


@deconstructible
class MongoStorage(Storage):
    """
    Class to be used in Django model FileField, ImageField, etc. as storage parameter.
    Use case:
        class TestModel(models.Model):
            ...
            file = models.FileField(storage=MongoStorage(db_alias='db_alias', collection='collection'))

    To get mongo file (GridOut) use:
    file = TestModel.objects.all()[0].file
    mongo_file = file.storage.get_file(file.name)

        NOTE: param path in methods is made of:
            upload_to + filename (upload_to is Field class param)
    """
    def __init__(self, db_alias, collection, base_url=settings.STORAGE_URL):
        self.db_alias = db_alias
        self.collection = collection
        self.base_url = base_url

        self._db = None
        self._grid_proxy = None
        self._fs = None

    @property
    def db(self):
        if not self._db:
            self._db = get_db(alias=self.db_alias)
        return self._db

    @property
    def grid_proxy(self):
        if not self._grid_proxy:
            self._grid_proxy = GridFSProxy(db_alias=self.db_alias, collection_name=self.collection)
        return self._grid_proxy

    @property
    def fs(self):
        if not self._fs:
            self._fs = self.grid_proxy.fs
        return self._fs

    # just override not to allow django to change a name of the file
    def get_available_name(self, name, max_length=None):
        return name

    def _open(self, oid, *args, **kwargs):
        """
            Get file from GridFS (MongoDB)
            Used by django.
        :param oid: ObjectID
        :param mode: (doesn't matter in this case)
        :return: GridOUT (has a read() method)
        """
        return self.fs.get(ObjectId(oid))

    def _save(self, path, content):
        """
            Put content of the file given in path to GridFS (MongoDB)
            Content can be streamed or saved depending on if content has attribute chunks or not.
        :param path: String, can be filename
        :param content: Content of the file to save.
        :return: ObjectID in string of the file created in GridFS (is saved to FileField.name)
        """
        path, filename = os.path.split(path)

        kwargs = {}

        if hasattr(content.file, 'content_type'):
            kwargs.update(content_type=content.file.content_type)
        elif hasattr(content, 'content_type'):
            kwargs.update(content_type=content.content_type)

        if hasattr(content, 'height') and hasattr(content, 'width'):
            kwargs.update(width=content.width, height=content.height)

        if hasattr(content, 'chunks'):
            return self._stream(filename, content, **kwargs)

        oid = self.fs.put(content, filename=filename, **kwargs)
        return str(oid)

    def exists(self, oid):
        """
            Check if filename given in path exists in GridFS
        :param oid: ObjectID in string
        :return: bool
        """
        return self.fs.exists({'_id': ObjectId(oid)})

    def get_file(self, oid):
        """
            Get file from GridFS (MongoDB)
        :param oid: ObjectID in string
        :return: file from GridFS
        """
        return self.fs.get(ObjectId(oid))

    def delete(self, oid):
        self.fs.delete(ObjectId(oid))

    def _stream(self, filename, content, **kwargs):
        """
            Raises FileExists if field already has a file.
        :param filename: String
        :param content: content of file with available content.chunks() method
        :return: ObjectID in string
        """
        grid_in = None
        try:
            grid_in = self.fs.new_file(filename=filename, **kwargs)
            for chunk in content.chunks():
                grid_in.write(chunk)
            return str(grid_in._id)
        except Exception as e:
            logger.exception("Can't write mongo file using storage")
        finally:
            if grid_in:
                grid_in.close()

    def size(self, oid):
        return self.fs.get(ObjectId(oid)).length

    def get_file_name(self, oid):
        return self.fs.get(ObjectId(oid)).filename

    def listdir(self, path=None):
        """
        according to GridFS documentation, this returns a list of
        every filename in this particular instance of GridFS.
        """
        return self.fs.list()

    def created_time(self, oid):
        return self.fs.get(ObjectId(oid)).upload_date

    def url(self, oid, app_label=None, model_name=None, pk=None):
        """
            NOTE: app_label, model_name, pk optional for compatibility
            Returns url to view/download the file.
        :param oid: ObjectID in string
        :return: String
        """
        if app_label and model_name and pk:
            url = '{}/{}/{}/{}/'.format(app_label, model_name, pk, oid)
        else:
            url = oid
        return urljoin(self.base_url, url)


