from rest_framework import serializers
from .models import NoonProduct, NoonOrder, NoonOrderItem, NoonInventory

class NoonProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoonProduct
        exclude = ['user', 'created_at', 'updated_at']

class NoonOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoonOrderItem
        exclude = ['order']

class NoonOrderSerializer(serializers.ModelSerializer):
    items = NoonOrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = NoonOrder
        exclude = ['user', 'created_at', 'updated_at']

class NoonInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = NoonInventory
        exclude = ['user']