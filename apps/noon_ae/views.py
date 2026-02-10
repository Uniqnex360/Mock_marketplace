from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied # Required for security check
from rest_framework.filters import SearchFilter
from .models import NoonProduct, NoonOrder, NoonOrderItem, NoonInventory
from .serializers import (
    NoonProductSerializer, NoonOrderSerializer,
    NoonOrderItemSerializer, NoonInventorySerializer
)
from datetime import datetime

class NoonProductViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NoonProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['partner_sku', 'noon_sku', 'title']
    
    def get_queryset(self):
        # SECURITY CHECK: Token must be for Noon
        if self.request.auth.marketplace != 'NOON_AE':
            raise PermissionDenied("This token is restricted to Noon AE endpoints.")
            
        return NoonProduct.objects.filter(user=self.request.user)
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 50))
        offset = (page - 1) * limit
        products = queryset[offset:offset + limit]
        
        formatted_products = []
        for p in products:
            formatted_products.append({
                'sku': p.partner_sku, 'noon_sku': p.noon_sku, 'name': p.title,
                'brand': p.brand, 'price': {'currency': 'AED', 'value': float(p.price)},
                'stock': {'quantity': p.stock_quantity}, 'status': p.status
            })
        
        return Response({'success': True, 'data': {'products': formatted_products, 'pagination': {'page': page, 'total_items': queryset.count()}}})

class NoonOrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NoonOrderSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'order_nr'
    
    def get_queryset(self):
        # SECURITY CHECK: Token must be for Noon
        if self.request.auth.marketplace != 'NOON_AE':
            raise PermissionDenied("This token is restricted to Noon AE endpoints.")
            
        return NoonOrder.objects.filter(user=self.request.user).prefetch_related('items').order_by('-order_date')
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 50))
        offset = (page - 1) * limit
        orders = queryset[offset:offset + limit]
        
        formatted_orders = []
        for o in orders:
            items = []
            for i in o.items.all():
                items.append({'item_id': i.order_item_id, 'sku': i.partner_sku, 'name': i.name, 'quantity': i.quantity, 'price': {'total_price': float(i.total_price)}})
            
            formatted_orders.append({
                'order_nr': o.order_nr, 'order_date': o.order_date.isoformat(), 'status': o.status,
                'customer': {'first_name': o.customer_first_name, 'last_name': o.customer_last_name},
                'payment': {'total': {'value': float(o.total_amount)}}, 'items': items
            })
        
        return Response({'success': True, 'data': {'orders': formatted_orders, 'pagination': {'page': page, 'total_items': queryset.count()}}})

class NoonInventoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NoonInventorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # SECURITY CHECK: Token must be for Noon
        if self.request.auth.marketplace != 'NOON_AE':
            raise PermissionDenied("This token is restricted to Noon AE endpoints.")
            
        return NoonInventory.objects.filter(user=self.request.user)
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        items = queryset[:100]
        formatted = []
        for i in items:
            formatted.append({'sku': i.partner_sku, 'stock': {'available': i.quantity}})
        return Response({'success': True, 'data': {'inventory': formatted, 'pagination': {'total_items': queryset.count()}}})

    @action(detail=False, methods=['post'], url_path='update')
    def update_stock(self, request):
        # Security check also needed here
        if self.request.auth.marketplace != 'NOON_AE':
            raise PermissionDenied("This token is restricted to Noon AE endpoints.")
            
        updates = request.data.get('updates', [])
        results = []
        for update in updates:
            try:
                inv = NoonInventory.objects.get(partner_sku=update.get('sku'), user=request.user)
                inv.quantity = update.get('quantity')
                inv.save()
                results.append({'sku': inv.partner_sku, 'status': 'success'})
            except:
                results.append({'sku': update.get('sku'), 'status': 'error'})
        return Response({'success': True, 'data': {'results': results}})