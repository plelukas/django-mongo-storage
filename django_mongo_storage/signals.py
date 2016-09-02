import logging

from django.db.models import FileField
from django.db.models.signals import post_delete
from django.dispatch import receiver

from django_mongo_storage.utils.storage import MongoStorage

logger = logging.getLogger(__name__)


# delete associated files from mongo after model deletion
# dispatch uid is set for no duplication

@receiver(post_delete, dispatch_uid="post_delete_file_removal")
def post_delete_receiver(sender, instance, **kwargs):
    for field in sender._meta.get_fields():
        if isinstance(field, FileField):
            if isinstance(field.storage, MongoStorage):
                field_file = getattr(instance, field.name)
                try:
                    field_file.storage.delete(field_file.name)
                    logger.debug("Deleted file:{} from {} model, {} field.".format(
                        field_file.name,
                        sender.__class__.__name__,
                        field.name
                    ))
                except:
                    pass
