from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied # Required for security check
from rest_framework.filters import SearchFilter
from django.db.models import Q
from .models import AmazonProduct, AmazonOrder, AmazonOrderItem, AmazonInventory
from .serializers import (
    AmazonProductSerializer, AmazonOrderSerializer, 
    AmazonOrderItemSerializer, AmazonInventorySerializer
)
from datetime import datetime, timedelta
import base64

class AmazonProductViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AmazonProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['sku', 'asin', 'title']
    
    def get_queryset(self):
        # SECURITY CHECK: Token must be for Amazon
        if self.request.auth.marketplace != 'AMAZON_AE':
            raise PermissionDenied("This token is restricted to Amazon AE endpoints.")
            
        queryset = AmazonProduct.objects.filter(user=self.request.user)
        
        # Support specific SKU/ASIN search parameters
        sku = self.request.query_params.get('sku')
        if sku:
            queryset = queryset.filter(sku__icontains=sku)
        
        asin = self.request.query_params.get('asin')
        if asin:
            queryset = queryset.filter(asin__icontains=asin)
        
        identifiers = self.request.query_params.get('identifiers')
        if identifiers:
            queryset = queryset.filter(asin__in=identifiers.split(','))
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page_size = int(request.query_params.get('pageSize', 20))
        items = queryset[:page_size]
        serializer = self.get_serializer(items, many=True)
        return Response({
            'payload': {'items': serializer.data, 'numberOfResults': queryset.count()},
            'pagination': {'nextToken': None}
        })

class AmazonOrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AmazonOrderSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'amazon_order_id'
    
    def get_queryset(self):
        # SECURITY CHECK: Token must be for Amazon
        if self.request.auth.marketplace != 'AMAZON_AE':
            raise PermissionDenied("This token is restricted to Amazon AE endpoints.")
            
        return AmazonOrder.objects.filter(user=self.request.user).prefetch_related('items').order_by('-purchase_date')
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        max_results = int(request.query_params.get('MaxResultsPerPage', 100))
        orders = queryset[:max_results]
        serializer = self.get_serializer(orders, many=True)
        
        formatted_orders = []
        for order_data in serializer.data:
            formatted_orders.append({
                'AmazonOrderId': order_data['amazon_order_id'],
                'PurchaseDate': order_data['purchase_date'],
                'OrderStatus': order_data['order_status'],
                'OrderTotal': {'CurrencyCode': 'AED', 'Amount': str(order_data['order_total_amount'])},
                'BuyerInfo': {'BuyerEmail': order_data.get('buyer_email', ''), 'BuyerName': order_data.get('buyer_name', '')}
            })
        
        return Response({
            'payload': {
                'Orders': formatted_orders, 
                'NextToken': None,
                'LastUpdatedBefore': datetime.now().isoformat() + 'Z'
            }
        })

    @action(detail=True, methods=['get'], url_path='orderItems')
    def order_items(self, request, amazon_order_id=None):
        order = self.get_object()
        items = AmazonOrderItem.objects.filter(order=order)
        formatted_items = []
        for item in items:
            formatted_items.append({
                'ASIN': item.asin, 'SellerSKU': item.sku, 'OrderItemId': item.order_item_id,
                'Title': item.title, 'QuantityOrdered': item.quantity_ordered,
                'ItemPrice': {'CurrencyCode': 'AED', 'Amount': str(item.item_price_amount)}
            })
        return Response({'payload': {'AmazonOrderId': order.amazon_order_id, 'OrderItems': formatted_items}})

class AmazonInventoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AmazonInventorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # SECURITY CHECK: Token must be for Amazon
        if self.request.auth.marketplace != 'AMAZON_AE':
            raise PermissionDenied("This token is restricted to Amazon AE endpoints.")
        return AmazonInventory.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        items = queryset[:50]
        formatted = []
        for item in items:
            formatted.append({
                'asin': item.asin, 'sellerSku': item.sku, 'productName': item.product_name,
                'inventoryDetails': {'fulfillableQuantity': item.available_quantity}
            })
        return Response({'payload': {'inventorySummaries': formatted}, 'pagination': {'nextToken': None}})