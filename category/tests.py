from rest_framework.test import APIClient

from django.contrib.auth.hashers import make_password
from django.test import TestCase

from .models import Category
from users.models import Admins, Users

class TestCategory(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.category_api = "/api/v1/category/"
        cls.sing_up_api = "/api/v1/users/sign_up/"
        
        cls.normal_user_data = {
            "email": "maamoun3haj9najee1b@mail.com"
            , "password": make_password("sv_gtab101enter")
            , "user_type": "USER"
        }
        cls.admin_user_data = {
            "email": "maamoun3haj9najee1b@mail.com"
            , "password": make_password("sv_gtab101enter")
            , "user_type": "USER"
        }
        
        cls.client = APIClient()

    def test_create_user(self):
        response = self.client.post(
            path=self.sing_up_api
            , data=self.normal_user_data
            , format="json"
        )
        
        self.assertTrue(Users.objects.all(), 1)
        