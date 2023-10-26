from rest_framework import generics, decorators, response

from django.shortcuts import render

# Create your views here.


@decorators.api_view(["GET"])
def hello(request):
    print("Hi")
    return response.Response({"message": "hello"})