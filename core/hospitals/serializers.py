from rest_framework import serializers
from .models import Hospital


class HospitalSerializer(serializers.ModelSerializer):
    """Serializer for Hospital model."""
    
    class Meta:
        model = Hospital
        fields = ['id', 'name', 'city', 'address', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

