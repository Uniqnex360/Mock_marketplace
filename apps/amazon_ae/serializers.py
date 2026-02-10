from rest_framework import serializers
from .models import AmazonProduct, AmazonOrder, AmazonOrderItem, AmazonInventory

class AmazonProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = AmazonProduct
        fields = '__all__'

class AmazonOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = AmazonOrderItem
        fields = '__all__'

class AmazonOrderSerializer(serializers.ModelSerializer):
    items = AmazonOrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = AmazonOrder
        fields = '__all__'

class AmazonInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AmazonInventory
        fields = '__all__'