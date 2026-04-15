from django.contrib import admin
from .models import HostDetail,CanCall

# Register your models here.
admin.site.register([HostDetail,CanCall])
