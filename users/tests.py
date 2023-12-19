from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APIClient

from hypothesis import given, strategies as st
from hypothesis.extra.django import TestCase
import pytest

from service_providers.models import ServiceProvider
from category.models import Category

User = get_user_model()
pytestmark = pytest.mark.django_db


class TestUserModels(TestCase):
    @classmethod
    def setUp(self) -> None:
        self.user_data = {
            "email": "maamoun.haj.najeeb@gmail.com"
            , "password": "17AiGz48rhe"
            , "user_type": "USER"
            , "is_active": True
            , "phone": "+963932715313"
        }
        
        self.category_data = {
            "ar_name": "أطباء"
            , "en_name": "Doctors"
        }
        
        self.service_provider_data = {
            "bank_name": "Albaraka"
            , "business_name": "Django On the Backend"
            , "iban": "i1b2a3n4"
            , "swift_code": "s1w2i3f4t5"
        }
        
        self.user = User.objects.create_user(**self.user_data)
        self.category = Category.objects.create(**self.category_data)
        self.service_provider = ServiceProvider.objects.create(
            **self.service_provider_data, category=self.category, user=self.user)
    
    @given(some_value=st.text(max_size=15))
    def test_create_user(self, some_value):
        assert self.user.email != some_value
    
    def test_create_category(self):
        assert self.category.ar_name == "أطباء"
        assert self.category.en_name == "Doctors"
    
    def test_create_service_provider(self):
        assert self.service_provider.user == self.user




class TestUsersAPI(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        
        self.user_data = {
            "email": "maamoun.haj.najeeb@gmail.com"
            , "password": "17AiGz48rhe"
            , "password2": "17AiGz48rhe"
            , "user_type": "USER"
            , "is_active": True
            , "phone": "+963932715313"
        }
        
        self.group = Group.objects.create(name="USER")
    
    # @given()
    def test_user_api_create(self):
        self.client.credentials(Accept_Language="ar")
        response = self.client.post(
            path="/api/v1/users/signup/"
            , data=self.user_data
            , format="json"
            , headers={"Accept-Language": "ar"})
        
        assert response.json != None
        assert response.status_code == 201
