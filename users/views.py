from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.hashers import make_password
from django.db.models.functions import TruncMonth
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.db.models import Q, Count

from rest_framework import permissions, decorators
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status, generics

from rest_framework_simplejwt.views import TokenObtainPairView

from functools import reduce
from random import randint
from typing import Any

from . import models, permissions as local_permissions
from . import throttles as local_throttles
from . import serializers, helpers

from utils.permission import authorization_with_method, HasPermission
from service_providers.models import ServiceProvider
from appointments.models import Appointments
from notification.models import Notification
from category.models import Category
from orders.models import OrderItem
from products.models import Product
from services.models import Service

Users = get_user_model()

# 
@decorators.api_view(["GET", ])
@authorization_with_method("list", "users")
def list_all_users(request: Request):
    """
    get all users and show them to admins
    """
    queryset = Users.objects.filter()
    serializer = serializers.UserSerializer(queryset, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


#
class UsersView(generics.RetrieveUpdateDestroyAPIView):
    """
    general retrieve, update, destroy api for profile owners and admins
    not for updating email or password
    """
    serializer_class = serializers.SpecificUserSerializer
    permission_classes = (HasPermission, )
    queryset = Users.objects
    
    def get_permissions(self):
        return [permission("users") for permission in self.permission_classes]
    
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        if request.data.get("image"):
            image_path = request.user.image.path
            helpers.delete_image(image_path)
        return super().update(request, *args, **kwargs)
    
    def perform_update(self, serializer):
        instance = serializer.save()
        
        Notification.objects.create(
            sender="System", sender_type="System"
            , receiver=instance.email, receiver_type="User"
            , en_content="Your profile information updated successfully"
            , ar_content="تم تحديث معلومات حسابك")
    
    def perform_destroy(self, instance: Users):
        image_path = instance.image.path
        helpers.delete_image(image_path)
        instance.delete()

#
class ServiceProviderList(generics.ListAPIView):
    """
    showing service providers list for everybody
    """
    serializer_class = serializers.ServiceProviderSerializer
    queryset = ServiceProvider.objects
    permission_classes = ( )
    
    def get_queryset(self):
        return self.queryset.filter(user__is_active=True)

#
class ServiceProviderCreate(generics.CreateAPIView):
    """
    signing up as service providers for UnAuthenticated users
    """
    serializer_class = serializers.ServiceProviderSerializer
    queryset = ServiceProvider.objects
    permission_classes = (local_permissions.UnAuthenticated, )
    
    def create(self, request: Request, *args, **kwargs):
        query = models.EmailConfirmation.objects.filter(ip_address=self.request.META.get("REMOTE_ADDR"))
        if query.exists():
            return Response(
                {"message": "You registered in this site, but you didn't confirm your email, "
                        "you can send a new email confirmation if you didn't receive one at the first time"}
                , status=status.HTTP_406_NOT_ACCEPTABLE)
            
        resp = super().create(request, *args, **kwargs)
        pk, email = resp.data["id"], resp.data["user"]["email"]
        
        models.EmailConfirmation.objects.get_or_create(
            user_id=pk, email=email, ip_address=self.request.META.get("REMOTE_ADDR"))
        
        confirm = helpers.SendMail(
            to=email, request=request, out=True, view="/api/v1/users/email_confirmation/")
        confirm.send_mail()
        
        return Response({"message": f"Confirmation email sent to: {email}"}, status=status.HTTP_201_CREATED)


@decorators.api_view(["POST", ])
@decorators.permission_classes([permissions.IsAdminUser, ])
def accept_provider_account(request: Request, provider_id: int, respond: str):
    respond = respond.capitalize()
    provider = ServiceProvider.objects.filter(id=provider_id)
    if not provider.exists():
        return Response({"error": "No account available with this id"}, status=status.HTTP_404_NOT_FOUND)
    
    provider = provider.first()
    provider.account_status = respond
    provider.save()
    
    if respond == "Accepted":
        helpers.activate_user(provider_id)
        send_mail(
            subject="Activate Service Provider Account"
            , message="Your account has been revised and activated, you can log in now"
            , from_email="med-sal-adminstration@gmail.com"
            , recipient_list=[provider.user.email, ])
        
        Notification.objects.create(
            sender="System", sender_type="System", receiver_type="Service_Provider", receiver=provider.user.email
            , en_content="Your account has been revised and activated, wellcome"
            , ar_content="تمت مراجعة حسابك و تفعيله, أهلاً وسهلاً")
    
    return Response({"message": f"Successfully {respond}"}, status=status.HTTP_202_ACCEPTED)


class ServiceProviderRUD(generics.RetrieveUpdateDestroyAPIView):
    """
    Read, Delete, Update specific service provider
    """
    serializer_class = serializers.ServiceProviderSerializer
    queryset = ServiceProvider.objects
    permission_classes = (permissions.IsAuthenticated, local_permissions.HavePermission, )
    
    def update(self, request, *args, **kwargs):
        data = request.data.copy()
        user_data = data.pop("user", None)
        if user_data:
            self.update_user_instance(user_data)
            
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        Notification.objects.create(
            sender="System", sender_type="System"
            , receiver=instance.user.email, receiver_type="Service_Provider"
            , ar_content="تم تحديث معلومات حسابك بنجاح"
            , en_content="Your profile information updated successfully")
        
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
    
    def update_user_instance(self, user_data: dict[str, Any]):
        """
        updating the user_instance in the service_provider record
        """
        pk = self.kwargs.get("pk")
        user_instance = Users.objects.filter(pk=pk)
        
        if user_data.get("image"):
            img_path = user_instance.first().image.path
            helpers.delete_image(img_path)
            
        user_instance.update(**user_data)
        
    def perform_destroy(self, instance):
        """
        remove files from the media folder before destroying record
        """
        helpers.delete_image(instance.user.image.path)
        helpers.delete_image(instance.provider_file.path)
        
        return super().perform_destroy(instance)

# 
class SignUp(generics.CreateAPIView):
    """
    sign up as user, admin, and super_admin
    """
    serializer_class = serializers.UserSerializer
    permission_classes = (local_permissions.UnAuthenticated, )
    queryset = Users.objects
    
    def create(self, request: Request, *args, **kwargs):
        query = models.EmailConfirmation.objects.filter(ip_address=self.request.META.get("REMOTE_ADDR"))
        if query.exists():
            return Response(
                {"message": "You registered in this site, but you didn't confirm your email, "
                        "you can send a new email confirmation if you didn't receive one at the first time"}
                , status=status.HTTP_406_NOT_ACCEPTABLE)
            
        resp = super().create(request, *args, **kwargs)
        pk, email = resp.data["id"], resp.data["email"]
        
        models.EmailConfirmation.objects.get_or_create(
        user_id=pk, email=email, ip_address=self.request.META.get("REMOTE_ADDR"))
        
        confirm = helpers.SendMail(
            to=resp.data.get("email"), request=request, out=True, view="/api/v1/users/email_confirmation/")
        confirm.send_mail()
        
        return Response({"message": "Confirmation email sent"}, status=resp.status_code
        , headers=self.get_success_headers(resp.data))

# 
@decorators.api_view(["GET"])
@decorators.permission_classes([local_permissions.UnAuthenticated, ])
def email_confirmation(request: Request):
    """
    this function is to use after sign up for email confirmation puprose
    """
    ip_address = request.META.get("REMOTE_ADDR")
    query = models.EmailConfirmation.objects.filter(ip_address=ip_address)
    
    if not query.exists():
        return Response(
            {"message": "Invalid email confirmation token"}
            , status=status.HTTP_404_NOT_FOUND)
    
    confirm_record = query.first()
    query.first().delete()
    
    def create_notification(user_id: int):
        user = Users.objects.get(id=user_id)
        user_type = "_".join(u_type.capitalize() for u_type in user.user_type.split("_"))
        
        ar_content, en_content = "تم تفعيل حسابك", "your account has been activated"
        if user_type == "Service_Provider":
            ar_content, en_content = "حسابك بانتظار المراجعة من قبل المشرفين", "Your account is under revision"
        
        Notification.objects.create(
            sender="System", sender_type="System", receiver=user.email
            , receiver_type=user_type, ar_content=ar_content, en_content=en_content)
    
    if Users.objects.get(id=confirm_record.user_id).user_type == "SERVICE_PROVIDER":
        create_notification(confirm_record.user_id)
        return Response(
            {"message":"Valid email, but you are Service Provider so your account is under revision"}
            , status=status.HTTP_200_OK)
        
    helpers.activate_user(confirm_record.user_id)
    create_notification(confirm_record.user_id)
    return Response({"message": "Valid email you can log in now"}, status=status.HTTP_202_ACCEPTED)

# 
@decorators.api_view(["POST", ])
@decorators.permission_classes([local_permissions.UnAuthenticated, ])
@decorators.throttle_classes([local_throttles.UnAuthenticatedRateThrottle, ])
def resend_email_validation(request: Request):
    """
    this function is used when email_confirmation failed to send email
    """
    ip_address = request.META.get("REMOTE_ADDR")
    query = models.EmailConfirmation.objects.filter(ip_address=ip_address)
    
    if not query.exists():
        return Response(
            {"message": "Invalid Ip Address, there is no associated account with this IP"}
            , status=status.HTTP_404_NOT_FOUND)
    
    confirm_record = query.first()
    confirm = helpers.SendMail(
        to=confirm_record.email, request=request, out=True
        , view="/api/v1/users/email_confirmation/")
    confirm.send_mail()
    
    return Response({"message": "Confirmation email resent"}, status=status.HTTP_202_ACCEPTED)

#
@decorators.api_view(["POST", ])
def change_email(request: Request):
    """
    give authenticated user ability to change his/her email
    and send a confirmation message to the new email.
    """
    user_id = request.user.id
    new_email = request.data.get("new_email")
    
    confirm = helpers.SendMail(
        to=new_email, request=request
        , view="/api/v1/users/accept_new_email/")
    confirm.send_mail()
    
    # we can make more than one email confirmation request if it doesn't work form the first time
    try:
        user_record = models.EmailChange.objects.get(user_id=user_id)
        user_record.new_email, user_record.token = new_email, confirm.token
        user_record.save()
        
    except models.EmailChange.DoesNotExist:
        models.EmailChange.objects.create(
            user_id=user_id, new_email=new_email, token=confirm.token)
    
    return Response({
        "message": f"confirmation message sent to {new_email}"
    }, status=status.HTTP_200_OK)

#
@decorators.api_view(["GET", ])
def accept_email_change(request: Request, token: str):
    """
    check if the link sent to email is real
    and make the new email official email for user
    """
    query = models.EmailChange.objects.filter(token=token)
    if not query.exists():
        return Response({
            "message": "Invalid confirmation link or expired"
        }, status=status.HTTP_404_NOT_FOUND)
    
    confirm_record = query.first()
    helpers.change_user_email(
        id=confirm_record.user_id
        , new_email=confirm_record.new_email)
    
    query.first().delete()
    
    return Response({
        "message": "user email changed successfully"
    }, status=status.HTTP_202_ACCEPTED)

#
@decorators.api_view(["POST", ])
def check_password(request: Request):
    """
    first step to change password to authenticated users
    """
    pwd, re_pwd = request.data.get("password"), request.data.get("re_password")
    if pwd != re_pwd:
        return Response({
            "message": "Password fields are not the same"
        }, status=status.HTTP_409_CONFLICT)
    
    user_email = request.user.email
    match = authenticate(email=user_email, password=pwd)
    if not match:
        return Response({
            "message": "The passowrd inputed isn't same authenticated user password"
        }, status=status.HTTP_409_CONFLICT)
    
    return Response({
        "message": "Valid passwords you can go to change password"
    }, status=status.HTTP_202_ACCEPTED)

#
@decorators.api_view(["POST", ])
def change_password(request: Request):
    """
    second step to change password to authenticated users
    """
    new_pwd = request.data.get("new_password")
    if not new_pwd:
        return Response({"Error": "new_password needed for changing current user password"}
            , status=status.HTTP_400_BAD_REQUEST)
    
    helpers.set_password(request.user, new_pwd)
    
    return Response({
        "message": "Password changed successfully"
    }, status=status.HTTP_202_ACCEPTED)

#
@decorators.api_view(["POST", ])
@decorators.permission_classes([local_permissions.UnAuthenticated, ])
def reset_password(request: Request):
    """
    first step to unauthenticated users to reset there password
    it send an email with a 6 digits code
    """
    email = request.data.get("email")
    user_instance = Users.objects.filter(email=email)
    if not user_instance.exists():
        return Response({
            "message": "There is no account associated with this email"
        }, status=status.HTTP_404_NOT_FOUND)
    
    code = helpers.generate_code()
    ip_address = request.META.get("REMOTE_ADDR")
    models.PasswordReset.objects.create(
        code=code, user=user_instance.first(), ip_address=ip_address)
    
    send_mail(subject="Password Reset"
        , message=f"put this code: {code} in the input field"
        , from_email="med-sal-adminstration@gmail.com"
        , recipient_list=[email, ])
    
    return Response({
        "message": "A 6 numbers code sent to your mail, check it"
    }, status=status.HTTP_200_OK)

#
@decorators.api_view(["GET", ])
@decorators.permission_classes([local_permissions.UnAuthenticated, ])
@decorators.throttle_classes([local_throttles.UnAuthenticatedRateThrottle, ])
def resend_code(request: Request):
    ip_address = request.META.get("REMOTE_ADDR")
    record = models.PasswordReset.objects.filter(ip_address=ip_address)
    
    if not record.exists():
        return Response({
            "message": "We've not send code for this email"
        }, status=status.HTTP_404_NOT_FOUND)
    
    record = record.select_related("user").first()
    send_mail(subject="Password Reset"
        , message=f"put this code: {record.code} in the input field"
        , from_email="med-sal-adminstration@gmail.com"
        , recipient_list=[record.user.email, ])
    
    return Response({
        "message": "A 6 numbers code sent to your mail, check it"
    }, status=status.HTTP_200_OK)

#
@decorators.api_view(["POST", ])
@decorators.permission_classes([local_permissions.UnAuthenticated, ])
def enter_code(request):
    """
    second step
    check if the inputed code the same
    and depending on that it give user ability to write new password
    """
    code = request.data.get("code")
    if not code:
        return Response({"Error": "you should put the code from email"}, status=status.HTTP_400_BAD_REQUEST)
    
    record = models.PasswordReset.objects.filter(code=code)
    if not record.exists():
        return Response({
            "message": "sorry, but there is no code like this in the database, try to reset password again"
        }, status=status.HTTP_404_NOT_FOUND)
    
    return Response({
        "message":"Right code, you can put new password now"
    }, status=status.HTTP_202_ACCEPTED)

#
@decorators.api_view(["POST", ])
@decorators.permission_classes([local_permissions.UnAuthenticated, ])
def new_password(request: Request):
    """
    third step
    saving the new password to user record if every scenario goes will
    """
    pwd, re_pwd = request.data.get("password"), request.data.get("re_password")
    if pwd != re_pwd:
        return Response({
            "message": "Password fields are not the same"
        }, status=status.HTTP_409_CONFLICT)
    
    ip_address = request.META.get("REMOTE_ADDR")
    record = models.PasswordReset.objects.select_related("user").get(ip_address=ip_address)
    user = record.user
    user.password = make_password(pwd)
    user.save()
    
    record.delete()
    
    return Response({
        "message": "Password changed successfully, now you can log in with the new password"
    }, status=status.HTTP_202_ACCEPTED)


@decorators.api_view(["POST", ])
def send_2FA_code(request: Request):
    """
    send 2FA code
    """
    query = models.PasswordReset.objects.filter(user=request.user)
    if query.exists():
        return Response({"error": "You've already receive an 2FA code, check you inbox or resent it"}
                , status=status.HTTP_403_FORBIDDEN)
    
    instance = models.PasswordReset.objects.create(ip_address=request.META.get("REMOTE_ADDR"),
        code="".join(str(randint(0, 9)) for _ in range(6)), user=request.user)
    
    send_mail(subject="2 Factor Authentication"
        , message=f"put this code: {instance.code} in the input field"
        , from_email="med-sal-adminstration@gmail.com"
        , recipient_list=[instance.user.email, ])
    
    return Response({"message": "A 6 number code sent to your email"}, status=status.HTTP_201_CREATED)


@decorators.api_view(["POST", ])
# @decorators.throttle_classes([local_throttles.AuthenticatedRateThrottle, ])
def resend_2fa_code(request: Request):
    """
    resend the 2FA code
    """
    query = models.PasswordReset.objects.filter(user=request.user)
    if not query.exists():
        return Response(
            {"error": "You haven't send a code in the first place"}
            , status=status.HTTP_404_NOT_FOUND)
    
    new_code = "".join(str(randint(0, 9)) for _ in range(6))
    instance = query.first()
    instance.code = new_code
    instance.save()
    
    send_mail(subject="2 Factor Authentication"
        , message=f"put this code: {instance.code} in the input field"
        , from_email="med-sal-adminstration@gmail.com"
        , recipient_list=[instance.user.email, ])
    
    return Response({"message": "A 6 number code resent to your email"}, status=status.HTTP_201_CREATED)


@decorators.api_view(["POST", ])
def validate_2FA(request: Request, code: str):
    """
    check if the 2FA code is valid
    """
    query = models.PasswordReset.objects.filter(user=request.user)
    if not query.exists():
        return Response(
            {"error": "You haven't send a code in the first place"}
            , status=status.HTTP_404_NOT_FOUND)
    
    instance = query.first()
    if instance.code != code:
        return Response({"error": "Not valid, try again"}, status=status.HTTP_406_NOT_ACCEPTABLE)
    
    instance.delete()
    return Response({"message": "Right code, wellcome"}, status=status.HTTP_202_ACCEPTED)

#
class LogIn(TokenObtainPairView):
    """
    login view
    the main login response edited with user(id, user_type) in the serializer
    """
    serializer_class = serializers.LogInSerializer
    permission_classes = (local_permissions.UnAuthenticated, )

from rest_framework_simplejwt.tokens import RefreshToken

@decorators.api_view(["POST", ])
def logout(req: Request):
    refresh_token = req.data.get("refresh")
    if not refresh_token:
        return Response({"Error": "Refresh Token needed"}, status=status.HTTP_400_BAD_REQUEST)
    
    token = RefreshToken(refresh_token)
    token.blacklist()
    
    return Response({"message": "Logged out successfully"}, status=status.HTTP_202_ACCEPTED)


def main_counter(language: str):
    """
    helper function
    """
    # stats
    stats = {}
    services_stats = Appointments.objects.filter(status="accepted", result__isnull=False).values(
        f"service__{language}_title").annotate(count=Count("service"))
    services_stats = [
        {"title": stat[f"service__{language}_title"],"count": stat["count"]} for stat in services_stats ]
    
    products_stats = OrderItem.objects.filter(status="ACCEPTED").values(
        f"product__{language}_title").annotate(count=Count("product"))
    products_stats = [
        {"title": stat[f"product__{language}_title"], "count": stat["count"]} for stat in products_stats ]
    
    user_stats = Group.objects.values("name").annotate(Count("user"))
    user_stats = {key["name"]: key["user__count"] for key in user_stats}
    
    stats["products_stats"], stats["services_stats"] = products_stats, services_stats
    stats["user_stats"] = user_stats
    
    # counts
    counts = {
        "products": Product.objects.count(),
        "services_count": Service.objects.count(),
        "users": Users.objects.count(),
    }
    
    return counts, stats


@decorators.api_view(["GET", ])
@decorators.permission_classes([permissions.IsAdminUser, ])
def admin_reports(req: Request):
    language = req.META.get("Accept-Language")
    counts, stats = main_counter(language)
    
    products_diagram = Product.objects.annotate(
            month=TruncMonth("updated_at")).values("month").annotate(products=Count("id"))
    products_diagram = [
        {"year": result["month"].year, "month": result["month"].month, "products_count": result["products"]}
        for result in products_diagram ]
    
    services_diagram = Service.objects.annotate(
            month=TruncMonth("updated_at")).values("month").annotate(
                services=Count("id"))
    services_diagram = [
        {"year": result["month"].year, "month": result["month"].month, "services_count": result["services"]}
        for result in services_diagram ]
    
    # each appointment is a customer (even if the customer comes more than one time)
    # this contains orders and appointments 
    # we get active and non-active users here
    users_count = Users.objects.annotate(month=TruncMonth('date_joined')).values("month").annotate(
            total=Count("id"))
    users_diagram = [
        {"year": user["month"].year, "month": user["month"].month, "total_users": user["total"]} 
            for user in users_count ]
    
    response = {
        "stats": stats,
        "counts": counts,
        "services_diagram": services_diagram,
        "products_diagram": products_diagram,
        "users_diagram": users_diagram
    }
    
    return Response(response, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@decorators.permission_classes([permissions.IsAdminUser, ])
def admin_dashboard_details_table(req: Request):
    language = req.META.get("Accept-Language")
    users_table = Group.objects.values("name").annotate(
        active=Count("user", filter=Q(user__is_active=True)),
        not_active=Count("user", filter=Q(user__is_active=False)))
    users_table = {
        key["name"]: {"active": key["active"], "not_active": key["not_active"]} for key in users_table }
    
    services_table = Category.objects.values(f"{language}_name").annotate(
        active=Count("services", filter=Q(services__is_active=True)),
        not_active=Count("services", filter=Q(services__is_active=False)))
    services_table = {
        key[f"{language}_name"]: {"active": key["active"], "not_active": key["not_active"]} 
        for key in services_table
    }
    
    products_table = Category.objects.values(f"{language}_name").annotate(
        active=Count("services_providers__locations__product",
            filter=Q(services_providers__locations__product__is_active=True)),
        not_active=Count("services_providers__locations__product",
            filter=Q(services_providers__locations__product__is_active=False)))
    products_table = {
        key[f"{language}_name"]: {"active": key["active"], "not_active": key["not_active"]} 
        for key in products_table
    }
    
    return Response({
        "users_table": users_table, "products_table": products_table,
        "services_table": services_table
        }, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@decorators.permission_classes([permissions.IsAdminUser, ])
def search_users(request: Request, search_term: str):
    search_terms = search_term.split("_")
    search_exprs = (Q(email__icontains=word) for word in search_terms)
    search_func = reduce(lambda x, y: x | y, search_exprs)
    queryset = Users.objects.filter(search_func)
    
    serializer = serializers.SpecificUserSerializer(queryset, many=True)
    return Response(data=serializer.data, status=status.HTTP_200_OK)
