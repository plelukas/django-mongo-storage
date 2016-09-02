import os

from django.core.files import File
from django.core.files.base import ContentFile
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, mock

from django_mongo_storage.utils.storage import MongoStorage
from .models import Document

def _get_storage_mock():
    oid = '012345678901234567890123'

    mongo_storage = mock.Mock(spec=MongoStorage)
    mongo_storage.save.return_value = oid
    mongo_storage.url.return_value = '/storage/django_mongo_storage/document/0/{}/'.format(oid)
    mongo_storage.collection = 'test'
    mongo_storage.get_file_name.return_value = 'test.txt'
    mongo_storage.delete = mock.Mock()

    return mongo_storage


class MongoFileFieldTest(TestCase):

    def test_clearable(self):
        """
            MongoFileField.save_form_data() will clear its instance attribute value if
            passed False.
        """
        d = Document(myfile='something.txt')
        self.assertEqual(d.myfile, 'something.txt')
        field = d._meta.get_field('myfile')
        field.save_form_data(d, False)

        self.assertEqual(d.myfile, '')

    def test_url(self):
        """
            Check if proper url is returned from field.
        """
        mongo_storage = _get_storage_mock()
        d = Document(myfile='something.txt')
        d.myfile.storage = mongo_storage

        self.assertEqual(d.myfile.url, mongo_storage.url())

    def test_html(self):
        """
            MongoFieldFile.__html__() should return filename to be posted in admin page.
        """
        mongo_storage = _get_storage_mock()
        d = Document(myfile='something.txt')
        d.myfile.storage = mongo_storage

        self.assertEqual(d.myfile.__html__(), mongo_storage.get_file_name())

    def test_save_with_no_file_before(self):
        """
            Check if first save (no file before) actually saves file.
        """
        mongo_storage = _get_storage_mock()

        Document.objects.get = mock.Mock()
        Document.objects.get.side_effect = ObjectDoesNotExist

        d = Document(myfile='something.txt')
        d.myfile.storage = mongo_storage

        d.myfile.save(mongo_storage.get_file_name(), ContentFile('content'), save=False)
        self.assertEqual(d.myfile.name, mongo_storage.save())

    def test_save_with_file_exist(self):
        """
            If file exists before in that field it should be removed.
        """
        mongo_storage = _get_storage_mock()

        # make mock that imitates initial file stored in storage
        initial = Document(myfile='initial.txt')
        initial.myfile.storage = mongo_storage

        Document.objects.get = mock.Mock()
        Document.objects.get.return_value = initial

        d = Document(myfile='something.txt')
        d.myfile.storage = mongo_storage

        d.myfile.save(mongo_storage.get_file_name(), ContentFile('content'), save=False)

        mongo_storage.delete.assert_called_once_with(initial.myfile.name)

    def test_save1_to_media_with_no_file_before(self):
        """
            Check if save_to_media method actually saves file to proper location.
        """
        mongo_storage = _get_storage_mock()

        d = Document(myfile='something.txt')
        d.myfile.storage = mongo_storage

        with open('django_mongo_storage/tests/files/test.txt', mode='rb') as file:
            passed_file = File(file)
            passed_file.filename = 'test.txt'
            d.myfile.storage.get_file.return_value = passed_file
            location = d.myfile.save_to_media()

            with open(location) as saved_file:
                self.assertEquals(saved_file.name, location)

    def test_save2_to_media_with_file_exist(self):
        """
            After saving file in test_save1_to_media_with_no_file_before,
             check if saving again does not remove the previous file.
             It should just return the location of file.
             After all test removes the test file.
        """
        mongo_storage = _get_storage_mock()

        d = Document(myfile='something.txt')
        d.myfile.storage = mongo_storage

        passed_file = mock.Mock()
        passed_file.__iter__ = mock.Mock()
        passed_file.filename = 'test.txt'
        d.myfile.storage.get_file.return_value = passed_file
        location = d.myfile.save_to_media()

        passed_file.__iter__.assert_not_called()

        #remove testing file
        os.remove(location)



