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

class AmazonProductViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AmazonProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = AmazonProduct.objects.filter(user=self.request.user)

        asin = self.request.query_params.get('asin')
        if asin:
            queryset = queryset.filter(asin=asin)

        sku = self.request.query_params.get('sku')
        if sku:
            queryset = queryset.filter(sku=sku)

        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)

        return queryset

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            'payload': {
                'Items': response.data['results'] if 'results' in response.data else response.data,
                'NumberOfResults': response.data.get('count', len(response.data)),
            }
        })

class AmazonOrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AmazonOrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = AmazonOrder.objects.filter(user=self.request.user).prefetch_related('items')

        order_status = self.request.query_params.get('OrderStatus')
        if order_status:
            queryset = queryset.filter(order_status=order_status)

        created_after = self.request.query_params.get('CreatedAfter')
        if created_after:
            date = datetime.fromisoformat(created_after.replace('Z', '+00:00'))
            queryset = queryset.filter(purchase_date__gte=date)

        return queryset.order_by('-purchase_date')

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            'payload': {
                'Orders': response.data['results'] if 'results' in response.data else response.data,
                'NextToken': response.data.get('next'),
                'LastUpdatedBefore': datetime.now().isoformat()
            }
        })

    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        order = self.get_object()
        items = AmazonOrderItem.objects.filter(order=order)
        serializer = AmazonOrderItemSerializer(items, many=True)

        return Response({
            'payload': {
                'AmazonOrderId': order.amazon_order_id,
                'OrderItems': serializer.data,
                'NextToken': None
            }
        })

class AmazonInventoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AmazonInventorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = AmazonInventory.objects.filter(user=self.request.user)

        skus = self.request.query_params.getlist('skus')
        if skus:
            queryset = queryset.filter(sku__in=skus)

        return queryset

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            'payload': {
                'inventorySummaries': response.data['results'] if 'results' in response.data else response.data,
                'nextToken': response.data.get('next'),
            }
        })