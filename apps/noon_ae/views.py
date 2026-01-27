from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import NoonProduct, NoonOrder, NoonOrderItem, NoonInventory
from .serializers import (
    NoonProductSerializer, NoonOrderSerializer,
    NoonOrderItemSerializer, NoonInventorySerializer
)
from datetime import datetime

class NoonProductViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NoonProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = NoonProduct.objects.filter(user=self.request.user)

        partner_sku = self.request.query_params.get('partner_sku')
        if partner_sku:
            queryset = queryset.filter(partner_sku=partner_sku)

        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)

        return queryset

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            'success': True,
            'data': {
                'products': response.data['results'] if 'results' in response.data else response.data,
                'total_count': response.data.get('count', len(response.data)),
                'page': request.query_params.get('page', 1)
            }
        })

class NoonOrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NoonOrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = NoonOrder.objects.filter(user=self.request.user).prefetch_related('items')

        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)

        from_date = self.request.query_params.get('from_date')
        if from_date:
            date = datetime.fromisoformat(from_date)
            queryset = queryset.filter(order_date__gte=date)

        return queryset.order_by('-order_date')

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            'success': True,
            'data': {
                'orders': response.data['results'] if 'results' in response.data else response.data,
                'total': response.data.get('count', len(response.data)),
                'page': request.query_params.get('page', 1),
                'limit': request.query_params.get('limit', 50)
            }
        })

class NoonInventoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NoonInventorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = NoonInventory.objects.filter(user=self.request.user)

        partner_skus = self.request.query_params.getlist('partner_skus')
        if partner_skus:
            queryset = queryset.filter(partner_sku__in=partner_skus)

        return queryset

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            'success': True,
            'data': {
                'inventory': response.data['results'] if 'results' in response.data else response.data,
                'total_count': response.data.get('count', len(response.data))
            }
        })