from django.contrib import admin

from .models import Balance, BillingConfig, UsageTransaction


@admin.register(Balance)
class BalanceAdmin(admin.ModelAdmin):
    list_display = ("recharge_amt", "balance", "debit_amount", "date")
    ordering = ("-date",)


@admin.register(BillingConfig)
class BillingConfigAdmin(admin.ModelAdmin):
    list_display = ("usage", "limit", "debit_amount", "debit_amount_old", "fetch_amount", "edit_amount", "limit_deduction_per_rc", "updated_at")

    def has_add_permission(self, request):
        if BillingConfig.objects.exists():
            return False
        return super().has_add_permission(request)


@admin.register(UsageTransaction)
class UsageTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "app",
        "transaction_type",
        "amount",
        "usage_before",
        "usage_after",
        "reg_number",
        "created_at",
    )
    list_filter = ("app", "transaction_type")
    ordering = ("-created_at", "-id")

    def get_fields(self, request, obj=None):
        if obj:
            return (
                "app",
                "transaction_type",
                "amount",
                "usage_before",
                "usage_after",
                "reg_number",
                "note",
                "created_at",
            )
        return ("app", "transaction_type", "amount", "note")

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return (
                "app",
                "transaction_type",
                "amount",
                "usage_before",
                "usage_after",
                "reg_number",
                "note",
                "created_at",
            )
        return ("usage_before", "usage_after", "reg_number", "created_at")

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "transaction_type":
            kwargs["choices"] = [
                (
                    UsageTransaction.MANUAL_SETTLEMENT,
                    "Manual Settlement",
                )
            ]
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def has_delete_permission(self, request, obj=None):
        return False
