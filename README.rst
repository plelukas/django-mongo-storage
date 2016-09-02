App for storing files in Mongo GridFS.
Supports streaming content, if it has chunks.
Deletes files on models deletion using signals (signals.py).
Deletes files on change (replace if file in that field already exists).

First, include STORAGE_URL in your django settings.

To use app, instead of django FileField or ImageField use custom MongoFileField or MongoImageField.
Ex.

 * this:
class DjangoModel(Model):

    ...
    file = FileField()
    ...

 * replace with this:
class DjangoModel(Model):

    ...
    file = MongoFileField(storage=MongoStorage(db_alias="DB_ALIAS", collection="COLLECTION"))
    ...


These mongo fields generate urls based on app, model and primary key:
/{settings.STORAGE_URL}/{app_label}/{model_name}/{model.pk}/{ObjectID (in mongo)}
ex.
/storage/django_mongo_storage/djangomodel/1/5799ee3ca68ce8463a392bc1/


In views.py there is a view that displays the file if it's text/image, or downloads it
based on the app_label, model_name, pk, and ObjectID.


To save the file manually:

    * first create or get model instance:
    model = DjangoModel(...)
    * then get the file-like django object File (ex. InMemoryUploadedFile)
    file = UploadedFile(...)
    * assign it to the model field and save model (it will replace the old file in MongoDB if there was one)
    model.file = file
    model.save()


To get file attributes from MongoDB:

    model = DjangoModel(...)
    file = model.file

    # get mongo file from storage
    mongo_file = file.storage.get_file(file.name)

    # now we have all the attributes from mongo in mongo_file, ex.:
    mongo_file.filename
    mongo_file.length
    mongo_file.content_type



Enjoy!