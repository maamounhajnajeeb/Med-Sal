from typing import Any, Dict
from rest_framework import serializers, validators

from django.db import connection
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.models import Admins, SuperAdmins



Users = get_user_model()


class ServiceProviderSerializer(serializers.Serializer):
    password = serializers.CharField(
        max_length=64, write_only=True, required=True
        , validators=[validate_password]
        , )
    password2 = serializers.CharField(max_length=64, write_only=True, required=True)
    email = serializers.EmailField(
        max_length=64
        , validators=[validators.UniqueValidator(queryset=Users.objects.all())]
        , required=True
        , )
    category = serializers.IntegerField()
    business_name = serializers.CharField(max_length=128)
    bank_name = serializers.CharField(max_length=128)
    iban = serializers.CharField(max_length=40)
    swift_code = serializers.CharField(max_length=16)
    provider_file = serializers.FileField()
    image = serializers.ImageField()
    phone = serializers.CharField(max_length=10)
    user_type = serializers.CharField(max_length=16)
    
    class Meta:
        model = Users
        fields = (
                "id", "email", "phone", "image", "password"
                , "password2", "user_type", "category", "business_name"
                , "bank_name", "iban", "swift_code", "provider_file"
                , )
        extra_kwargs = {
            'phone': {'required': True},
            'image': {'required': True}
        , }
    
    def validate(self, attrs):
        password, password2 = attrs.get("password"), attrs.pop("password2")
        if password != password2:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        return attrs
    
    def create(self, validated_data):
        user = Users.objects.create_user(
            password=validated_data['password']
            , email=validated_data['email']
            , phone=validated_data['phone']
            , image=validated_data['image']
            , user_type=validated_data["user_type"]
            , )
        
        prov_creation = self.create_service_provider(user, validated_data)
        
        if prov_creation != "Done":
            raise serializers.ValidationError("Something wrong with provider values")
        
        return user.email, user.id
    
    def create_service_provider(self, user: Users, validated_data):
        query = self.insert_query(user, validated_data)
        return query
    
    def insert_query(self, user, validated_data):
        with connection.cursor() as cursor:
            cursor.execute(
                f"insert into service_providers_serviceprovider ( \
                    business_name, bank_name, iban, swift_code, category_id, provider_file \
                    , user_id, users_ptr_id, account_status, created_at, updated_at) \
                    values ( \
                    '{validated_data.get('business_name')}', '{validated_data.get('bank_name')}' \
                    , '{validated_data.get('iban')}', '{validated_data.get('swift_code')}' \
                    , '{validated_data.get('category')}', '{validated_data.get('provider_file')}' \
                    , '{user.id}', '{user.id}', 'pending', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP ) "
                , )
            
        return "Done"


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=64, write_only=True, required=True
        , validators=[validate_password]
        , )
    password2 = serializers.CharField(max_length=64, write_only=True, required=True)
    email = serializers.EmailField(
        max_length=64
        , validators=[validators.UniqueValidator(queryset=Users.objects.all())]
        , required=True
        , )
    
    class Meta:
        model = Users
        fields = ("id", "email", "phone", "image", "password", "password2", "user_type")
        extra_kwargs = {
            'phone': {'required': True},
            'image': {'required': True}
        , }
    
    def validate(self, attrs):
        password, password2 = attrs.get("password"), attrs.pop("password2")
        if password != password2:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        return attrs
    
    def create(self, validated_data):
        model = self.model_hashing(validated_data.get("user_type"))
        admin_attrs = self.admins_attrs(validated_data.get("user_type"))
        user = model.objects.create_user(
            password=validated_data['password']
            , email=validated_data['email']
            , phone=validated_data['phone']
            , image=validated_data['image']
            , user_type=validated_data["user_type"]
            , **admin_attrs)
        
        user.save()
        return user
    
    def admins_attrs(self, user_type: str):
        attrs = dict()
        if user_type.lower() == "admin":
            attrs["is_staff"] = True
        elif user_type.lower() == "super_admin":
            attrs["is_staff"] = True
            attrs["is_superuser"] = True
        return attrs
    
    def model_hashing(self, user_type: str):
        user_type = user_type.lower()
        models = {
            "user": Users
            , "admin": Admins
            , "service_provider": Users
            , "super_admin": SuperAdmins
        }
        return models[user_type]


class LogInSerializer(TokenObtainPairSerializer):
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, str]:
        attrs = super().validate(attrs)
        
        attrs.update({"id": self.user.id})
        attrs.update({"user_type": self.user.user_type})
        
        return attrs