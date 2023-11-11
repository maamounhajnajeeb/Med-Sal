from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.http import HttpRequest

import random


Users = get_user_model()


class SendMail:
    
    def __init__(self, to: str, request: HttpRequest) -> None:
        self.to, self.request = to, request
        self.subject = "Med Sal Email Confirmation"
    
    def generate_token(self):
        token = ""
        for _ in range(16):
            token += str(random.randint(0, 9))
        
        return token
    
    def get_content(self):
        protocol = "https" if self.request.is_secure() else "http"
        host = self.request.get_host()
        view = "/api/v1/users/email_confirmation/"
        self.token = self.generate_token()
        full_path = f"{protocol}://{host}{view}{self.token}"
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
    
