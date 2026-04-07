from rest_framework import serializers

from .models import Balance, BillingConfig, UsageTransaction


class BalanceSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Balance
        fields = "__all__"


class BillingConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingConfig
        fields = [
            "id",
            "usage",
            "limit",
            "debit_amount",
            "fetch_amount",
            "edit_amount",
            "created_at",
            "updated_at",
        ]


class UsageTransactionSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    transaction_type_display = serializers.CharField(
        source="get_transaction_type_display", read_only=True
    )

    class Meta:
        model = UsageTransaction
        fields = [
            "id",
            "transaction_type",
            "transaction_type_display",
            "amount",
            "usage_before",
            "usage_after",
            "reg_number",
            "note",
            "created_at",
        ]
