from rest_framework import serializers
from .models import FrontRcNew


class FrontRcNewSerializer(serializers.ModelSerializer):
    class Meta:
        model = FrontRcNew
        fields = "__all__"
