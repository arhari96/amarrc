from rest_framework import serializers
from .models import Balance


class BalanceSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Balance
        fields = "__all__"
