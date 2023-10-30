from rest_framework.test import APIClient

from django.contrib.auth.hashers import make_password
from django.test import TestCase

from .models import Category
from users.models import Admins, Users

class TestCategory(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.category_api = "/api/v1/category/"
        cls.sign_up_api = "/api/v1/users/sign_up/"
        
        cls.normal_user_data = {
            "email": "maamoun3haj9najee1b@mail.com"
            , "password": "sv_gtab101enter"
            , "confirm_password": "sv_gtab101enter"
            , "user_type": "USER"
        }
        cls.admin_user_data = {
            "email": "maamoun3haj9najee1b@mail.com"
            , "password": "sv_gtab101enter"
            , "confirm_password": "sv_gtab101enter"
            , "user_type": "ADMIN"
        }
        
        cls.client = APIClient()
    
    def create_user(self):
        resp = self.client.post(
            self.sign_up_api
            , self.normal_user_data
            , format="json"
        )
        
        return resp.data["tokens"]["access"]
    
    def create_admin(self):
        resp = self.client.post(
            self.sign_up_api
            , self.admin_user_data
            , format="json"
        )
        
        return resp.data["tokens"]["access"]
        
    def test_create_user(self):
        response = self.client.post(
            self.sign_up_api
            , self.normal_user_data
            , format="json"
        )
        
        self.assertEqual(Users.objects.count(), 1)
        self.assertEqual(response.status_code, 201)
    
    def test_create_admin(self):
        response = self.client.post(
            self.sign_up_api
            , self.admin_user_data
            , format="json"
        )
        
        self.assertEqual(Admins.admins.count(), 1)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Admins.admins.first().is_staff, True)
        self.assertEqual(Admins.admins.first().is_superuser, False)
    
    def test_create_category_by_anonymousu_user(self):
        resp = self.client.post(
            self.category_api
            , {"name": "Clinic"}
            , format="json"
        )
        
        self.assertEqual(resp.status_code, 401)
    
    def test_create_category_by_user(self):
        user_token = self.create_user()
        client = APIClient()
        
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + user_token)
        
        resp = client.post(
            self.category_api
            , {"name": "HOSPITAL"}
            , format="json"
        )
        
        self.assertEqual(resp.status_code, 401)
    
    def test_create_category_by_admin(self):
        admin_token = self.create_admin()
        client = APIClient()
        
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + admin_token)
        
        resp = client.post(
            self.category_api
            , {"name": "DOCTOR"}
            , format="json"
        )
        
        self.assertEqual(resp.status_code, 201)