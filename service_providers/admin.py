from django.contrib import admin
from .models import *

# class ServiceProviderAdmin(admin.ModelAdmin):
    
#     list_display = ('business_name')
#     list_filter = ('category','business_name', 'account_status')


# admin.site.register(ServiceProvider,ServiceProviderAdmin)
admin.site.register(ServiceProvider)
