from rest_framework import generics, decorators
from rest_framework import permissions, status
from rest_framework.response import Response

from django.http import HttpRequest

from . import permissions as mypermissions
from . import models, serializers

from users.serializers import ServiceProviderSerializer


