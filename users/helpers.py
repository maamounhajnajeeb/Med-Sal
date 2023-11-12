from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.http import HttpRequest

import random


Users = get_user_model()


class SendMail:
    
    def __init__(self, request: HttpRequest, to: str, view: str, out: bool = False) -> None:
        self.to, self.request = to, request
        self.subject = "Med Sal Email Confirmation"
        self.view = view
        self.out = out
    
    def generate_token(self):
        token = ""
        for _ in range(16):
            token += str(random.randint(0, 9))
        
        return token
    
    def get_content(self):
        protocol = "https" if self.request.is_secure() else "http"
        host = self.request.get_host()
        self.token = self.generate_token()
        
        if self.out:
            full_path = f"{protocol}://{host}{self.view}"
        else:
            full_path = f"{protocol}://{host}{self.view}{self.token}"
        
        return f"please use this link to verify your account: \n {full_path}"
        
    def send_mail(self):
        content = self.get_content()
        send_mail(
            subject=self.subject
            , message=content
            , from_email="med-sal-adminstration@gmail.com"
            , recipient_list=[self.to, ])



def activate_user(id: int):
    user_instance: Users = Users.objects.get(id=id)
    user_instance.is_active = True
    user_instance.save()
    


def change_user_email(id: int, new_email: str):
    user_instance: Users = Users.objects.get(id=id)
    user_instance.email = new_email
    user_instance.save()


def set_password(user: Users, new_pwd: str):
    user.set_password(new_pwd)
    user.save()