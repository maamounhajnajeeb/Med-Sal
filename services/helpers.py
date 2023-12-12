from django.core.files.storage import FileSystemStorage
from django.http import HttpRequest
from django.conf import settings
from django.db.models import Q

from category.models import Category
from . import models

from functools import reduce
import uuid, os

MEDIA_FOLDER = settings.MEDIA_ROOT


class FileMixin():
    
    def upload(self, file_objs, folder_name: str, request: HttpRequest):
        host = request.get_host()
        protocol = "https" if request.is_secure() else "http"
        fs = FileSystemStorage(location=self.foldering_cliche(folder_name))
        
        file_names = []
        for file_obj in file_objs:
            extension = file_obj.name.split(".")[1]
            
            change_filename = lambda extension: f"{uuid.uuid4().hex}.{extension}"
            file_name = change_filename(extension)
            
            file_names.append(f"{protocol}://{host}/media/{folder_name}/{file_name}")
            fs.save(file_name, file_obj)
            
        return ",".join(file_names)
    
    def foldering_cliche(self, folder_name: str) -> str:
        path = os.path.join(MEDIA_FOLDER, folder_name)
        return path
    
    def delete_images(self, images_paths: str):
        images_paths = images_paths.split(",")
        
        actual_paths = []
        for image_path in images_paths:
            folder_name, file_name = image_path.split("/")[-2:]
            actual_paths.append(os.path.join(MEDIA_FOLDER, folder_name, file_name))
        
        for f in actual_paths:
            try:
                os.remove(f)
                print("Removed")
            except:
                print("No such file")



def searching_func(category_name):
    text_seq = category_name.split("_")
    
    q_exp = (Q(category__en_name__icontains=x) | Q(category__ar_name__icontains=x) for x in text_seq)
    
    query_func = reduce(lambda x, y: x & y, q_exp)
    queryset = models.Service.objects.filter(query_func)
    
    return queryset
