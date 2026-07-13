from rest_framework import serializers

from .models import NewRc, OldRc


class NewRcSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewRc
        fields = "__all__"
        read_only_fields = ("now", "front_image", "back_image")


class OldRcSerializer(serializers.ModelSerializer):
    class Meta:
        model = OldRc
        fields = "__all__"
        read_only_fields = ("now", "front_image", "back_image")
