import os
import time
import logging
from gridfs.errors import NoFile

from django.utils._os import safe_join
from django.conf import settings
from django.db import models
from django.db.models.fields.files import FieldFile, ImageFieldFile
from django.core.exceptions import ObjectDoesNotExist

logger = logging.getLogger(__name__)


class _MongoFieldFile(FieldFile):
    """
    Class to be used in MongoFileField attr_class attribute.
    """

    RETRY_LIMIT = 4

    # url to be a link to in admin change model view
    @property
    def url(self):
        self._require_file()
        for i in range(self.RETRY_LIMIT - 1):
            try:
                url = self.storage.url(self.name, self.instance._meta.app_label,
                                       self.instance.__class__.__name__.lower(), self.instance.pk)
                return url
            except NoFile as e:
                time.sleep(0.5)

        # last call if file not found should raise an error
        return self.storage.url(self.name, self.instance._meta.app_label,
                                self.instance.__class__.__name__.lower(), self.instance.pk)

    # name that is shown in admin change model view
    def __html__(self):
        for i in range(self.RETRY_LIMIT):
            try:
                html = self.storage.get_file_name(self.name)
                return html
            except NoFile as e:
                time.sleep(0.5)

        # if file not found return empty string
        return ""

    # in change admin view delete the old file (replace it)
    def save(self, name, content, save=True):
        try:
            obj = self.instance.__class__.objects.get(pk=self.instance.pk)
            # the model already exists so we have to replace desired file inside it
            obj_field_file = getattr(obj, self.field.name)
            try:
                obj_field_file.storage.delete(obj_field_file.name)
                logger.debug("Deleted file:{} from {} model, {} field.".format(
                    obj_field_file.name,
                    self.instance.__class__.__name__,
                    self.field.name
                ))
            except:
                pass
        except ObjectDoesNotExist:
            # if the file did not exist before, that's totally fine, just proceed
            pass
        super(_MongoFieldFile, self).save(name, content, save)

    # method saving the file from mongo to media dir in local filesystem
    def save_to_media(self):
        self._require_file()

        # prepare location and make dirs if they don't exist
        location = settings.MEDIA_ROOT
        location = safe_join(location, self.instance._meta.app_label, self.storage.collection)
        os.makedirs(location, exist_ok=True)

        # get filename from mongo
        mongo_file = self.storage.get_file(self.name)
        location = safe_join(location, mongo_file.filename)

        # stream content to the filesystem's file
        try:
            with open(location, 'xb') as file:
                for chunk in mongo_file:
                    file.write(chunk)
        except FileExistsError:
            pass

        return location


class _MongoImageFieldFile(ImageFieldFile):
    """
    Class to be used in MongoImageField attr_class attribute.
    Identical to _MongoFieldFile, just other parent.
    """

    RETRY_LIMIT = 4

    # url to be a link to in admin change model view
    @property
    def url(self):
        self._require_file()
        for i in range(self.RETRY_LIMIT - 1):
            try:
                url = self.storage.url(self.name, self.instance._meta.app_label,
                                       self.instance.__class__.__name__.lower(), self.instance.pk)
                return url
            except NoFile as e:
                time.sleep(0.5)

        # last call if file not found should raise an error
        return self.storage.url(self.name, self.instance._meta.app_label,
                                self.instance.__class__.__name__.lower(), self.instance.pk)

    # name that is shown in admin change model view
    def __html__(self):
        for i in range(self.RETRY_LIMIT):
            try:
                html = self.storage.get_file_name(self.name)
                return html
            except NoFile as e:
                time.sleep(0.5)

        # if file not found return empty string
        return ""

    # in change admin view delete the old file (replace it)
    def save(self, name, content, save=True):
        try:
            obj = self.instance.__class__.objects.get(pk=self.instance.pk)
            # the model already exists so we have to replace desired file inside it
            obj_field_file = getattr(obj, self.field.name)
            try:
                obj_field_file.storage.delete(obj_field_file.name)
                logger.debug("Deleted file:{} from {} model, {} field.".format(
                    obj_field_file.name,
                    self.instance.__class__.__name__,
                    self.field.name
                ))
            except:
                pass
        except ObjectDoesNotExist:
            # if the file did not exist before, that's totally fine, just proceed
            pass
        super(_MongoImageFieldFile, self).save(name, content, save)

    # method saving the file from mongo to media dir in local filesystem
    def save_to_media(self):
        self._require_file()

        # prepare location and make dirs if they don't exist
        location = settings.MEDIA_ROOT
        location = safe_join(location, self.instance._meta.app_label, self.storage.collection)
        os.makedirs(location, exist_ok=True)

        # get file from mongo
        mongo_file = self.storage.get_file(self.name)
        location = safe_join(location, mongo_file.filename)

        # stream content to the filesystem's file
        try:
            with open(location, 'xb') as file:
                for chunk in mongo_file:
                    file.write(chunk)
        except FileExistsError:
            # if file already exists do nothing
            pass

        return location


class MongoFileField(models.FileField):
    attr_class = _MongoFieldFile

    # when changing or clearing field in admin site
    def save_form_data(self, instance, data):
        if data is not None:
            file = getattr(instance, self.attname)
            if file != data:
                file.delete(save=False)

        super(MongoFileField, self).save_form_data(instance, data)


class MongoImageField(models.ImageField):
    attr_class = _MongoImageFieldFile

    # when changing or clearing field in admin site ex. checked the clear checkbox in image field
    def save_form_data(self, instance, data):
        if data is not None:
            file = getattr(instance, self.attname)
            if file != data:
                file.delete(save=False)

        super(MongoImageField, self).save_form_data(instance, data)
