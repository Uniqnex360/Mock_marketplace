from rest_framework import serializers
from .models import NoonProduct, NoonOrder, NoonOrderItem, NoonInventory

class NoonProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoonProduct
        fields = '__all__'
class NoonOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoonOrderItem
        fields = '__all__'

class NoonOrderSerializer(serializers.ModelSerializer):
    items = NoonOrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = NoonOrder
        fields = '__all__'

class NoonInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = NoonInventory
        fields = '__all__'