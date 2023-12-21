from rest_framework.test import APIClient

from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model

from hypothesis.extra.django import TestCase


Users = get_user_model()


class TestCreateAPI(TestCase):
    def setUp(self) -> None:
        self.admin_data = {
            "email": "maamoun.haj.najeeb@gmail.com"
            , "phone": "+963932715313"
            , "user_type": "ADMIN"
            , "password": "sv_gtab101enter"
            , "is_active": True
            , "is_staff": True
        }
        
        self.category_data = {
            "en_name": "Doctors"
            , "ar_name": "أطباء"
        }
        
        self.group_name = "ADMIN"
        
        self.client = APIClient()
    
    def test_create(self):
        self.create_group()
        self.create_admin()
        access_token = self.login()
        
        response = self.client.post(
            path="/api/v1/category/create/"
            , data=self.category_data
            , format="json"
            , headers={"Authorization": f"JWT {access_token}"})
        
        response_data = response.json()
        
        assert response_data["en_name"] == "Doctors"
        assert response_data["ar_name"] == "أطباء"
        assert response_data["ar_name"] != "Doctors"
        assert response_data["en_name"] != "أطباء"
        
        assert response.status_code == 201
    
    def login(self):
        response = self.client.post(
            path="/api/v1/users/login/"
            , data={"email": "maamoun.haj.najeeb@gmail.com", "password": "sv_gtab101enter"}
            , format="json")
        response_data = response.json()
        return response_data["access"]
    
    def create_admin(self):
        user = Users.objects.create_user(**self.admin_data)
        return user
    
    def create_group(self):
        Group.objects.create(name=self.group_name)


class TestListAndRetrieveAPI(TestCase):
    def setUp(self) -> None:
        self.admin_data = {
            "email": "maamoun.haj.najeeb@gmail.com"
            , "phone": "+963932715313"
            , "user_type": "ADMIN"
            , "password": "sv_gtab101enter"
            , "is_active": True
            , "is_staff": True
        }
        
        self.category_data = {
            "en_name": "Doctors"
            , "ar_name": "أطباء"
        }
        
        self.group_name = "ADMIN"
        
        self.client = APIClient()
    
    def test_valid_retrieve(self):
        self.create_category()
        
        response = self.client.get(path="/api/v1/category/1/", headers={"Accept-Language": "ar"})
        instance_data = response.json()[0]
        
        assert instance_data["name"] == "أطباء"
    
    def test_invalid_retrieve(self):
        self.create_category()
        
        response = self.client.get(path="/api/v1/category/2/")
        assert response.status_code == 404
    
    def test_valid_list(self):
        self.create_category()
        
        response = self.client.get(path="/api/v1/category/", headers={"Accept-Language": "ar"})
        queryset_data = response.json()
        
        assert len(queryset_data) == 1
    
    def test_invalid_list(self):
        response = self.client.get(path="/api/v1/category/", headers={"Accept-Language": "ar"})
        queryset_data = response.json()
        
        assert len(queryset_data) == 0
    
    def create_category(self):
        self.create_group()
        self.create_admin()
        access_token = self.login()
        
        self.client.post(
            path="/api/v1/category/create/", data=self.category_data
            , format="json", headers={"Authorization": f"JWT {access_token}"})
    
    def login(self):
        response = self.client.post(
            path="/api/v1/users/login/"
            , data={"email": "maamoun.haj.najeeb@gmail.com", "password": "sv_gtab101enter"}
            , format="json")
        response_data = response.json()
        return response_data["access"]
    
    def create_admin(self):
        user = Users.objects.create_user(**self.admin_data)
        return user
    
    def create_group(self):
        Group.objects.create(name=self.group_name)


class TestUpdateAndDestroyAPI(TestCase):
    def setUp(self) -> None:
        self.admin_data = {
            "email": "maamoun.haj.najeeb@gmail.com"
            , "phone": "+963932715313"
            , "user_type": "ADMIN"
            , "password": "sv_gtab101enter"
            , "is_active": True
            , "is_staff": True
        }
        
        self.category_data = {
            "en_name": "Doctors"
            , "ar_name": "أطباء"
        }
        
        self.group_name = "ADMIN"
        
        self.client = APIClient()
    
    def test_update_category(self):
        self.create_category()
        
    def test_destroy_category(self):
        self.create_category()
        
    def test_invalid_destroy_category(self):
        response = self.client.delete(
            path="/api/v1/category/destroy/6/"
            , headers={"Authorization": f"JWT {self.login()}"})
        assert response.status_code == 404
    
    def create_category(self):
        access_token = self.login()
        
        self.client.post(path="/api/v1/category/create/", data=self.category_data
            , format="json", headers={"Authorization": f"JWT {access_token}"})
        
        return access_token
    
    def login(self):
        self.create_group()
        self.create_admin()
        
        response = self.client.post(
            path="/api/v1/users/login/"
            , data={"email": "maamoun.haj.najeeb@gmail.com", "password": "sv_gtab101enter"}
            , format="json")
        
        return response.json()["access"]
    
    def create_admin(self):
        user = Users.objects.create_user(**self.admin_data)
        return user
    
    def create_group(self):
        Group.objects.create(name=self.group_name)