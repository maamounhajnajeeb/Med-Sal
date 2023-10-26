from django.contrib.auth import authenticate, get_user_model
from django.test import TestCase, Client

from . import models
User = get_user_model()

class MyTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {
            "username" : "maamounnajeeb"
            , "email" : "maamounnajeeb@gmail.com"
            , "password":"sv_gtab101enter"
            , "is_active": True
        }
        
        cls.superuser_data = {
            "username" : "maamounnajeebsuper"
            , "email" : "maamounnajeebsuper@gmail.com"
            , "password":"sv_gtab101enter"
            , "is_active": True
            # , "is_superuser": True
            # , "is_staff" : True
            , "user_type": models.Users.Types.SUPER_ADMIN
        }
        
        cls.client = Client()
    
    def create_superuser(self) -> User:
        superuser = models.SuperAdmins.objects.create(
            **self.superuser_data
        )
        
        superuser.set_password(superuser.password)
        superuser.save()
        
        return superuser
    
    def create_user(self) -> User:
        user = models.Users.objects.create(
            **self.user_data
        )
        
        user.set_password(user.password)
        user.save()
        
        return user
    
    def test_create_user(self):
        user = self.create_user()
        
        self.assertEqual(user.username, self.user_data["username"])
        self.assertEqual(user.email, self.user_data["email"])
        self.assertEqual(user.is_active, True)
    
    def test_create_superuser(self):
        superuser = self.create_superuser()
        
        self.assertEqual(superuser.username, self.superuser_data["username"])
        self.assertEqual(superuser.email, self.superuser_data["email"])
        
        self.assertEqual(models.Users.Types.SUPER_ADMIN, superuser.user_type)
        self.assertTrue(models.SuperAdmins.admins.all().count() == 1)
        
        self.assertEqual(superuser.is_superuser, True)
        self.assertEqual(superuser.is_staff, True)
        self.assertEqual(superuser.is_active, True)
    
    def test_authentication(self):
        user = self.create_user()
        result = authenticate(email=self.user_data["email"], password=self.user_data["password"])
        self.assertTrue(result == user)
    
    def test_client_login(self):
        superuser = self.create_superuser()
        client_auth = self.client.login(
            email=self.superuser_data["email"], password=self.superuser_data["password"])
        self.assertEqual(True, client_auth)
        # self.assertEqual(True, superuser.is_superuser)
        