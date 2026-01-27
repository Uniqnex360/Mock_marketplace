from rest_framework import serializers
from .models import AmazonProduct, AmazonOrder, AmazonOrderItem, AmazonInventory

class AmazonProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = AmazonProduct
        exclude = ['user', 'created_at', 'updated_at']

class AmazonOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = AmazonOrderItem
        exclude = ['order']

class AmazonOrderSerializer(serializers.ModelSerializer):
    items = AmazonOrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = AmazonOrder
        exclude = ['user', 'created_at', 'updated_at']

class AmazonInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AmazonInventory
        exclude = ['user']