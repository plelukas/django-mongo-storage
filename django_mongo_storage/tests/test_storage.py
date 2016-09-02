import io
import time
from datetime import datetime, timedelta

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.test import TestCase, mock
from django_mongo_storage.utils.storage import MongoStorage


class MongoStorageTest(TestCase):

    mongo_storage = MongoStorage('Test', 'test')
    text_oid = None
    image_oid = None

    @classmethod
    def setUpTestData(cls):
        with open('django_mongo_storage/tests/files/test.txt') as text_file, \
                open('django_mongo_storage/tests/files/test.jpg') as image_file:

            dj_text_file = InMemoryUploadedFile(text_file.buffer, None, text_file.name, 'text/plain', None, None)
            cls.text_oid = cls.mongo_storage._save(text_file.name, dj_text_file)

            from PIL import Image
            bytes = io.BytesIO(image_file.buffer.read())
            image = Image.open(bytes)

            dj_image_file = InMemoryUploadedFile(bytes, None, image_file.name,
                                                 'image/jpg', bytes.getbuffer().nbytes, None)
            dj_image_file.width = image.width
            dj_image_file.height = image.height

            cls.image_oid = cls.mongo_storage._save(image_file.name, dj_image_file)

    @classmethod
    def tearDownClass(cls):
        cls.mongo_storage.delete(cls.text_oid)
        cls.mongo_storage.delete(cls.image_oid)
        super().tearDownClass()

    def test_save_and_delete(self):

        filename = 'test.txt'

        with open('django_mongo_storage/tests/files/{}'.format(filename)) as file:
            dj_file = InMemoryUploadedFile(file.buffer, None, file.name, 'text/plain', None, None)
            result = self.mongo_storage.save(file.name, dj_file)

            # sleep for replication lag
            time.sleep(0.5)

            self.assertEqual(self.mongo_storage.get_file_name(result), filename)

            self.mongo_storage.delete(result)
            self.assertFalse(self.mongo_storage.exists(result))

    def test_stream_and_delete(self):

        filename = 'test.txt'

        with open('django_mongo_storage/tests/files/{}'.format(filename)) as file:
            dj_file = InMemoryUploadedFile(file.buffer, None, file.name, 'text/plain', None, None)
            result = self.mongo_storage._stream(filename, dj_file)

            #sleep for replication lag
            time.sleep(0.5)

            self.assertEqual(self.mongo_storage.get_file_name(result), filename)

            self.mongo_storage.delete(result)
            self.assertFalse(self.mongo_storage.exists(result))

    def test_file_properties(self):

        mongo_image_file = self.mongo_storage.get_file(self.image_oid)

        self.assertEqual(mongo_image_file.filename, 'test.jpg')
        self.assertTrue(hasattr(mongo_image_file, 'width'))
        self.assertTrue(hasattr(mongo_image_file, 'height'))
        self.assertNotEqual(mongo_image_file, 0)
        self.assertEqual(mongo_image_file.content_type, 'image/jpg')
        self.assertLess(datetime.now() - mongo_image_file.upload_date, timedelta(days=1))

    def test_listdir(self):
        self.assertIn('test.jpg', self.mongo_storage.listdir())
        self.assertIn('test.txt', self.mongo_storage.listdir())

    def test_url(self):
        app_label, model_name, pk = 'test_app', 'testmodel', 1

        self.assertEqual(self.mongo_storage.url(self.text_oid, app_label, model_name, pk),
                         '{}{}/{}/{}/{}/'.format(self.mongo_storage.base_url, app_label, model_name, pk, self.text_oid))

    def test_partial_url(self):
        model_name = 'testmodel'

        self.assertEqual(self.mongo_storage.url(self.text_oid, model_name=model_name),
                         '{}{}'.format(self.mongo_storage.base_url, self.text_oid))
        self.assertEqual(self.mongo_storage.url(self.text_oid),
                         '{}{}'.format(self.mongo_storage.base_url, self.text_oid))




