from django.contrib.auth import get_user_model
from django.test import TestCase

from service_providers.models import ServiceProvider
from category.models import Category

User = get_user_model()



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
    
    def test_create_user(self):
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(user.email, "maamoun.haj.najeeb@gmail.com")
    
    def test_create_category(self):
        category = Category.objects.create(**self.category_data)
        
        self.assertEqual(category.ar_name, "أطباء")
        self.assertEqual(category.en_name, "Doctors")
    
    def test_create_service_provider(self):
        user = User.objects.create(**self.user_data)
        category = Category.objects.create(**self.category_data)
        sp = ServiceProvider.objects.create(
            **self.service_provider_data, category=category, user=user)

        self.assertEqual(sp.user, user)
