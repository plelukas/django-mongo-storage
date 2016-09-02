# Use case:
#
# from django.db import models
#
# from django_mongo_storage.utils.storage import MongoStorage
# from django_mongo_storage.fields import MongoFileField, MongoImageField
#
#
# class TestModel(models.Model):
#
#     file_id = models.AutoField(primary_key=True)
#     file = MongoFileField(storage=MongoStorage(db_alias='FileStorage', collection='fs'))
#
#     def __str__(self):
#         return str(self.file_id)
#
#
# class TestFinalModel(models.Model):
#
#     pikerino = models.AutoField(primary_key=True)
#     file1 = MongoFileField(storage=MongoStorage(db_alias='FileStorage', collection='final'))
#     file2 = MongoFileField(storage=MongoStorage(db_alias='FileStorage', collection='final'))
#
#     def __str__(self):
#         return str(self.pikerino)
#
#
# class TestImageModel(models.Model):
#
#     file_id = models.AutoField(primary_key=True)
#     photo = MongoImageField(storage=MongoStorage(db_alias='FileStorage', collection='pics'), name='diff_name')
#
#     def __str__(self):
#         return str(self.file_id)
