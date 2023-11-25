from django.core.files.storage import FileSystemStorage
from django.http import HttpRequest

from datetime import datetime
from typing import Any
import os


class HandleFiles:
    def __init__(self, request: HttpRequest) -> None:
        self.request = request
        
        fs = FileSystemStorage()
        fs.location = os.path.join(fs.location, "products")
        self.fs = fs
    
    def upload_images(self, images_objs: list[Any]):
        images_names = ""
        for i in range(len(images_objs)):
            image_obj = images_objs[i]
            image_path, image_name = self.generate_unique_name(image_obj.name)
            self.fs.save(image_name, image_obj)
            images_names += image_path
            if i < len(images_objs) -1:
                images_names += ","
        
        return images_names
    
    def generate_unique_name(self, image_name: str):
        extension = image_name.split(".")[1]
        microsecond = datetime.now().microsecond
        image_name = f"{microsecond}.{extension}"
        protocol = "https" if self.request.is_secure() else "http"
        image_path = f"{protocol}://{self.request.get_host()}/media/products/{image_name}"
        return image_path, image_name
    
    def delete_images(self, paths: list[str]):
        for path in paths:
            try:
                os.remove(path)
                print("Image Removed")
            except:
                print("No Image")