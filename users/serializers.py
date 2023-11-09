from rest_framework import serializers, validators

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from djoser.serializers import UserCreateSerializer

from users.models import Admins, SuperAdmins
from service_providers.models import ServiceProvider
from service_providers.serializers import ServiceProviderSerializer

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
        user = model.objects.create_user(
            password=validated_data['password']
            , email=validated_data['email']
            , phone=validated_data['phone']
            , image=validated_data['image']
            , user_type=validated_data["user_type"]
            , )
        
        user.save()
        return user
    
    def model_hashing(self, user_type: str):
        user_type = user_type.lower()
        models = {
            "user": Users
            , "admin": Admins
            , "super_admin": SuperAdmins
        }
        return models[user_type]


class UserRegistrationSerializer(UserCreateSerializer):
    
    class Meta(UserCreateSerializer.Meta):
        model = Users
        fields = UserCreateSerializer.Meta.fields
    #     fields = (
    #         "email", "password", "re_password", "phone"
    #         , "user_type", "service_provider")
    
    # def validate(self, attrs):
    #     print(attrs)
    #     return super().validate(attrs)
    
    # def create(self, validated_data: dict):
    #     service_provider = validated_data.pop("service_provider")
    #     User = Users.objects.create(**validated_data)
    #     Provider = ServiceProvider.objects.create(user=User, **service_provider)
        
    #     return User

# class SignUpSerializer(serializers.ModelSerializer):
    
#     class Meta:
#         model = Users
#         fields = ("email", "password", "")


class ResetPasswordSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()


class ServiceProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceProvider
        fields = ("business_name", "contact_number")





"""
{
    "user_type": "SERVICE_PROVIDER",
    "email": "provider@example.com",
    "password": "your_password",
    "re_password": "your_password",
    "business_name": "Your Business Name",
    "contact_number": "123-456-7890",
    "bank_name": "Your Bank Name",
    "category": "DOCTOR",
    "iban": "Your IBAN",
    "swift_code": "Your Swift Code"
    "provider_file": "service provider documents"
}


"""


"""

{
    "user_type": "USER",
    "email": "user@example.com",
    "password": "your_password",
    "re_password": "your_password"
}


"""


"""
{"code": "344639"}
"""


"""

{"email": "admin@admin.com"}


"""
