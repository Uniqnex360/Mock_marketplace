from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import AmazonProduct, AmazonOrder, AmazonOrderItem, AmazonInventory
from .serializers import (
    AmazonProductSerializer, AmazonOrderSerializer, 
    AmazonOrderItemSerializer, AmazonInventorySerializer
)
from datetime import datetime, timedelta
import base64

class AmazonProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Mock Amazon SP-API Catalog Items API
    Similar to: GET /catalog/2022-04-01/items
    """
    serializer_class = AmazonProductSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = AmazonProduct.objects.filter(user=self.request.user)
        
        # Filter by ASIN (identifiers)
        identifiers = self.request.query_params.get('identifiers')
        if identifiers:
            asin_list = identifiers.split(',')
            queryset = queryset.filter(asin__in=asin_list)
        
        # Filter by SKU (sellerSku)
        seller_sku = self.request.query_params.get('sellerSku')
        if seller_sku:
            queryset = queryset.filter(sku=seller_sku)
        
        # Filter by keywords
        keywords = self.request.query_params.get('keywords')
        if keywords:
            queryset = queryset.filter(
                Q(title__icontains=keywords) | 
                Q(description__icontains=keywords)
            )
        
        # Filter by brand
        brand_names = self.request.query_params.get('brandNames')
        if brand_names:
            queryset = queryset.filter(brand__in=brand_names.split(','))
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """Mock Amazon GetCatalogItems API response format"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Pagination
        page_size = int(request.query_params.get('pageSize', 20))
        page_token = request.query_params.get('pageToken')
        
        # Decode page token to get offset
        offset = 0
        if page_token:
            try:
                offset = int(base64.b64decode(page_token).decode())
            except:
                offset = 0
        
        # Get page of results
        items = queryset[offset:offset + page_size]
        serializer = self.get_serializer(items, many=True)
        
        # Create next token if more results
        next_token = None
        if queryset.count() > offset + page_size:
            next_token = base64.b64encode(str(offset + page_size).encode()).decode()
        
        # Amazon SP-API format response
        return Response({
            'payload': {
                'items': serializer.data,
                'numberOfResults': queryset.count(),
            },
            'pagination': {
                'nextToken': next_token
            }
        })
    
    def retrieve(self, request, *args, **kwargs):
        """Mock Amazon GetCatalogItem API"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        return Response({
            'payload': serializer.data
        })


class AmazonOrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Mock Amazon SP-API Orders API
    Similar to: GET /orders/v0/orders
    """
    serializer_class = AmazonOrderSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'amazon_order_id'
    
    def get_queryset(self):
        queryset = AmazonOrder.objects.filter(user=self.request.user).prefetch_related('items')
        
        # Filter by MarketplaceIds (required in real API)
        marketplace_ids = self.request.query_params.getlist('MarketplaceIds')
        if marketplace_ids:
            queryset = queryset.filter(marketplace_id__in=marketplace_ids)
        
        # Filter by OrderStatuses
        order_statuses = self.request.query_params.getlist('OrderStatuses')
        if order_statuses:
            queryset = queryset.filter(order_status__in=order_statuses)
        
        # Filter by CreatedAfter
        created_after = self.request.query_params.get('CreatedAfter')
        if created_after:
            try:
                date = datetime.fromisoformat(created_after.replace('Z', '+00:00'))
                queryset = queryset.filter(purchase_date__gte=date)
            except:
                pass
        
        # Filter by CreatedBefore
        created_before = self.request.query_params.get('CreatedBefore')
        if created_before:
            try:
                date = datetime.fromisoformat(created_before.replace('Z', '+00:00'))
                queryset = queryset.filter(purchase_date__lte=date)
            except:
                pass
        
        # Filter by LastUpdatedAfter
        last_updated_after = self.request.query_params.get('LastUpdatedAfter')
        if last_updated_after:
            try:
                date = datetime.fromisoformat(last_updated_after.replace('Z', '+00:00'))
                queryset = queryset.filter(updated_at__gte=date)
            except:
                pass
        
        # Filter by FulfillmentChannels
        fulfillment_channels = self.request.query_params.getlist('FulfillmentChannels')
        if fulfillment_channels:
            queryset = queryset.filter(fulfillment_channel__in=fulfillment_channels)
        
        return queryset.order_by('-purchase_date')
    
    def list(self, request, *args, **kwargs):
        """Mock Amazon GetOrders API response format"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Pagination
        max_results = int(request.query_params.get('MaxResultsPerPage', 100))
        next_token = request.query_params.get('NextToken')
        
        offset = 0
        if next_token:
            try:
                offset = int(base64.b64decode(next_token).decode())
            except:
                offset = 0
        
        orders = queryset[offset:offset + max_results]
        serializer = self.get_serializer(orders, many=True)
        
        # Format orders like Amazon
        formatted_orders = []
        for order_data in serializer.data:
            formatted_orders.append({
                'AmazonOrderId': order_data['amazon_order_id'],
                'PurchaseDate': order_data['purchase_date'],
                'LastUpdateDate': order_data.get('updated_at', order_data['purchase_date']),
                'OrderStatus': order_data['order_status'],
                'FulfillmentChannel': order_data.get('fulfillment_channel', 'MFN'),
                'SalesChannel': order_data.get('sales_channel', 'Amazon.ae'),
                'OrderTotal': {
                    'CurrencyCode': order_data.get('order_total_currency', 'AED'),
                    'Amount': str(order_data['order_total_amount'])
                },
                'NumberOfItemsShipped': order_data.get('number_of_items_shipped', 0),
                'NumberOfItemsUnshipped': order_data.get('number_of_items_unshipped', 0),
                'PaymentMethod': order_data.get('payment_method', 'Other'),
                'MarketplaceId': order_data.get('marketplace_id', 'A2VIGQ35RCS4UG'),
                'BuyerInfo': {
                    'BuyerEmail': order_data.get('buyer_email', ''),
                    'BuyerName': order_data.get('buyer_name', '')
                },
                'ShipServiceLevel': order_data.get('ship_service_level', 'Standard')
            })
        
        # Create next token
        new_next_token = None
        if queryset.count() > offset + max_results:
            new_next_token = base64.b64encode(str(offset + max_results).encode()).decode()
        
        return Response({
            'payload': {
                'Orders': formatted_orders,
                'NextToken': new_next_token,
                'LastUpdatedBefore': datetime.now().isoformat() + 'Z',
                'CreatedBefore': datetime.now().isoformat() + 'Z'
            }
        })
    
    def retrieve(self, request, *args, **kwargs):
        """Mock Amazon GetOrder API"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        order_data = serializer.data
        
        return Response({
            'payload': {
                'AmazonOrderId': order_data['amazon_order_id'],
                'PurchaseDate': order_data['purchase_date'],
                'OrderStatus': order_data['order_status'],
                'OrderTotal': {
                    'CurrencyCode': 'AED',
                    'Amount': str(order_data['order_total_amount'])
                }
            }
        })
    
    @action(detail=True, methods=['get'], url_path='orderItems')
    def order_items(self, request, amazon_order_id=None):
        """Mock Amazon GetOrderItems API"""
        order = self.get_object()
        items = AmazonOrderItem.objects.filter(order=order)
        
        formatted_items = []
        for item in items:
            formatted_items.append({
                'ASIN': item.asin,
                'SellerSKU': item.sku,
                'OrderItemId': item.order_item_id,
                'Title': item.title,
                'QuantityOrdered': item.quantity_ordered,
                'QuantityShipped': item.quantity_shipped,
                'ItemPrice': {
                    'CurrencyCode': item.item_price_currency,
                    'Amount': str(item.item_price_amount)
                },
                'ShippingPrice': {
                    'CurrencyCode': 'AED',
                    'Amount': str(item.shipping_price_amount)
                },
                'ItemTax': {
                    'CurrencyCode': 'AED',
                    'Amount': str(item.item_tax_amount)
                },
                'PromotionDiscount': {
                    'CurrencyCode': 'AED',
                    'Amount': str(item.promotion_discount_amount)
                },
                'ConditionId': item.condition_id,
                'IsGift': item.is_gift
            })
        
        return Response({
            'payload': {
                'AmazonOrderId': order.amazon_order_id,
                'OrderItems': formatted_items,
                'NextToken': None
            }
        })


class AmazonInventoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Mock Amazon SP-API FBA Inventory API
    Similar to: GET /fba/inventory/v1/summaries
    """
    serializer_class = AmazonInventorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = AmazonInventory.objects.filter(user=self.request.user)
        
        # Filter by SKUs (sellerSkus)
        seller_skus = self.request.query_params.getlist('sellerSkus')
        if seller_skus:
            queryset = queryset.filter(sku__in=seller_skus)
        
        # Filter by granularityType
        granularity_type = self.request.query_params.get('granularityType', 'Marketplace')
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """Mock Amazon GetInventorySummaries API response format"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Pagination
        next_token = request.query_params.get('nextToken')
        offset = 0
        if next_token:
            try:
                offset = int(base64.b64decode(next_token).decode())
            except:
                offset = 0
        
        page_size = 50
        items = queryset[offset:offset + page_size]
        
        formatted_summaries = []
        for item in items:
            formatted_summaries.append({
                'asin': item.asin,
                'fnSku': item.fn_sku or item.sku,
                'sellerSku': item.sku,
                'condition': item.condition,
                'inventoryDetails': {
                    'fulfillableQuantity': item.available_quantity,
                    'inboundWorkingQuantity': item.pending_quantity,
                    'inboundShippedQuantity': 0,
                    'inboundReceivingQuantity': 0,
                    'reservedQuantity': {
                        'totalReservedQuantity': item.reserved_quantity,
                        'pendingCustomerOrderQuantity': item.reserved_quantity,
                        'pendingTransshipmentQuantity': 0,
                        'fcProcessingQuantity': 0
                    }
                },
                'lastUpdatedTime': item.last_updated_time.isoformat() + 'Z',
                'productName': item.product_name,
                'totalQuantity': item.total_quantity
            })
        
        new_next_token = None
        if queryset.count() > offset + page_size:
            new_next_token = base64.b64encode(str(offset + page_size).encode()).decode()
        
        return Response({
            'payload': {
                'granularity': {
                    'granularityType': 'Marketplace',
                    'granularityId': 'A2VIGQ35RCS4UG'
                },
                'inventorySummaries': formatted_summaries
            },
            'pagination': {
                'nextToken': new_next_token
            }
        })