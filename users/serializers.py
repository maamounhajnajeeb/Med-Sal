from rest_framework import serializers, validators

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from djoser.serializers import UserCreateSerializer

from users.models import Admins, SuperAdmins
from category.models import Category
from service_providers.models import ServiceProvider
from service_providers.serializers import ServiceProviderSerializer

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
    
    # class Meta:
    #     # model = Users
    #     fields = (
    #             "id", "email", "phone", "image", "password"
    #             , "password2", "user_type", "category", "business_name"
    #             , "bank_name", "iban", "swift_code", "provider_file"
    #             , )
    #     extra_kwargs = {
    #         'phone': {'required': True},
    #         'image': {'required': True}
    #     , }
    
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
        
        self.create_service_provider(user, validated_data)
        
        return user
    
    def create_service_provider(self, user: Users, validated_data):
        category = Category.objects.get(id=validated_data.get("category"))
        ServiceProvider.objects.create(
            category=category, user=user
            , iban=validated_data.get("iban")
            , bank_name=validated_data.get("bank_name")
            , swift_code=validated_data.get("swift_code")
            , provider_file=validated_data.get("provider_file")
            , business_name=validated_data.get("business_name")
            )


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
            , "service_provider": Users
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

