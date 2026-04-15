from rest_framework import serializers
from .models import HostDetail

class HostDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostDetail
        fields = ['name', 'mobile_number', 'last_active']