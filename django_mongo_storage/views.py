from django.contrib.auth.decorators import login_required
from django.db.models.loading import get_model
from django.http import FileResponse, HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django_mongo_storage.utils.storage import MongoStorage


# get a file from GridFS (MongoDB) for specified model instance
def _get_mongo_file(app_label, model_name, pk, file_oid):
    Model = get_model(app_label, model_name)
    model = get_object_or_404(Model, pk=pk)

    for field in model._meta.get_fields():
        from gridfs import NoFile
        from django.db.models import FileField
        if isinstance(field, FileField):
            if isinstance(field.storage, MongoStorage):
                try:
                    file = field.storage.get_file(file_oid)
                    return file
                except NoFile:
                    # no need to do anything, try other fields
                    pass
    return None


@login_required
def view_file(request, app_label, model_name, pk, file_oid):

    # if user has proper perms then he can get a desired file
    mongo_file = _get_mongo_file(app_label, model_name, pk, file_oid)
    if not mongo_file:
        raise Http404('File not found')
    filename = mongo_file.filename
    content_type = mongo_file.content_type

    if content_type:
        if 'text' in content_type or 'image' in content_type:
            return HttpResponse(mongo_file.read(), content_type=content_type)
        else:
            response = FileResponse(mongo_file, content_type=content_type)
            response['Content-Disposition'] = 'attachment; filename=' + filename
            return response
    else:
        response = FileResponse(mongo_file)
        response['Content-Disposition'] = 'attachment; filename=' + filename
        return response


