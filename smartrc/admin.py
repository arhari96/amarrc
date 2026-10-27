from django.contrib import admin
from .models import NewRc, OldRc, Rc


@admin.register(NewRc)
class NewRcAdmin(admin.ModelAdmin):
    list_display = (
        "reg_number",
        "name",
        "maker_name",
        "model_name",
        "vehicle_class",
        "fuel",
        "template",
        "reg_date",
        "rto_name",
        "now",
    )
    search_fields = (
        "reg_number",
        "chassis_number",
        "engine_number",
        "name",
        "maker_name",
        "model_name",
        "rto_name",
    )
    list_filter = ("template", "fuel", "vehicle_class", "now")
    ordering = ("-now",)
    readonly_fields = ("now",)


@admin.register(OldRc)
class OldRcAdmin(admin.ModelAdmin):
    list_display = (
        "reg_number",
        "name",
        "maker_name",
        "model_name",
        "owner_type",
        "fuel",
        "reg_date",
        "rto_name",
        "now",
    )
    search_fields = (
        "reg_number",
        "chassis_number",
        "engine_number",
        "name",
        "maker_name",
        "model_name",
        "rto_name",
    )
    list_filter = ("fuel", "owner_type", "now")
    ordering = ("-now",)
    readonly_fields = ("now",)


@admin.register(Rc)
class RcAdmin(admin.ModelAdmin):
    list_display = ("reg_number", "now")
    search_fields = ("reg_number",)
    ordering = ("-now",)
    readonly_fields = ("now",)
