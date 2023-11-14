from rest_framework import serializers, validators

from django.db import connection
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from typing import Any, Dict

from users.models import Admins, SuperAdmins
from service_providers.models import ServiceProvider



Users = get_user_model()


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
        user = model.objects.create_user(**validated_data, **admin_attrs)
        
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

class ServiceProviderSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    
    class Meta:
        model = ServiceProvider
        fields = ("user", "provider_file", "category", "business_name"
                , "bank_name", "iban", "swift_code")
    
    def create(self, validated_data):
        user = Users.objects.create(**validated_data.pop('user'))
        category = validated_data.pop("category")
        
        keys = [f"{key}" for key in validated_data.keys()]
        keys = ", ".join(keys)
        
        values = [f"'{val}'" for val in validated_data.values()]
        values = ", ".join(values)
        
        keys = keys + ", users_ptr_id, user_id, category_id, account_status, created_at, updated_at"
        values = values + f", '{user.id}', '{user.id}', '{category.id}', 'pending', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP"
        
        query = f"insert into service_providers_serviceprovider ({keys}) values ({values})"
        with connection.cursor() as cur:
            cur.execute(query)
        
        serv_prov_obj = ServiceProvider.objects.select_related("user").last()
        return serv_prov_obj


class LogInSerializer(TokenObtainPairSerializer):
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, str]:
        attrs = super().validate(attrs)
        
        attrs.update({"id": self.user.id})
        attrs.update({"user_type": self.user.user_type})
        return attrs


class SpecificUserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Users
        fields = ("id", "phone", "email", "image", "user_type", "date_joined")
