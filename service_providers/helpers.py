from django.core.files.storage import FileSystemStorage
from django.conf import settings

from uuid import uuid4
import datetime

def upload_file(instance):
    # renaming
    extension = instance.name.split()[1]
    new_filename = uuid4().hex + extension
    
    # choose the location
    date_obj = datetime.datetime
    month, year, day = date_obj.now().month, date_obj.now().year, date_obj.now().day
    
    # storaging
    location = f"{settings.MEDIA_ROOT}/service_providers/documents/{year}/{month}/{day}/"
    fs = FileSystemStorage(location=location)
    result = fs.save(name=new_filename, content=instance)
    
    return location+result
