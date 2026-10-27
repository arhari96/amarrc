from django.contrib import admin
from .models import HostDetail, CanCall


@admin.register(HostDetail)
class HostDetailAdmin(admin.ModelAdmin):
    list_display = ("name", "mobile_number", "last_active")
    search_fields = ("name", "mobile_number")
    ordering = ("-last_active",)


@admin.register(CanCall)
class CanCallAdmin(admin.ModelAdmin):
    list_display = ("can_call",)
