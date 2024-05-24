from rest_framework import serializers
from .models import FrontRcNew,BackRcNew


class FrontRcNewSerializer(serializers.ModelSerializer):
    class Meta:
        model = FrontRcNew
        fields = "__all__"

class BackRcNewSerializer(serializers.ModelSerializer):
    class Meta:
        model = BackRcNew
        fields = "__all__"