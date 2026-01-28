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
    """
    Mock Noon Seller API - Products
    Similar to: GET /seller/products
    """
    serializer_class = NoonProductSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = NoonProduct.objects.filter(user=self.request.user)
        
        # Filter by SKU
        sku = self.request.query_params.get('sku')
        if sku:
            queryset = queryset.filter(partner_sku=sku)
        
        # Filter by noon_sku
        noon_sku = self.request.query_params.get('noon_sku')
        if noon_sku:
            queryset = queryset.filter(noon_sku=noon_sku)
        
        # Filter by status
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        # Filter by brand
        brand = self.request.query_params.get('brand')
        if brand:
            queryset = queryset.filter(brand__icontains=brand)
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(title__icontains=search)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """Mock Noon GetProducts API response format"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Pagination
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 50))
        
        offset = (page - 1) * limit
        products = queryset[offset:offset + limit]
        serializer = self.get_serializer(products, many=True)
        
        # Noon API format
        formatted_products = []
        for product in serializer.data:
            formatted_products.append({
                'sku': product['partner_sku'],
                'noon_sku': product['noon_sku'],
                'name': product['title'],
                'name_ar': product.get('title_ar', ''),
                'brand': product['brand'],
                'category': product['category_code'],
                'price': {
                    'currency': 'AED',
                    'value': float(product['price'])
                },
                'sale_price': {
                    'currency': 'AED',
                    'value': float(product['sale_price']) if product.get('sale_price') else None
                } if product.get('sale_price') else None,
                'stock': {
                    'quantity': product['stock_quantity'],
                    'max_order_quantity': product.get('max_order_quantity', 10)
                },
                'status': product['status'],
                'images': [product.get('image_url')] if product.get('image_url') else [],
                'created_at': product.get('created_at'),
                'updated_at': product.get('updated_at')
            })
        
        total_pages = (queryset.count() + limit - 1) // limit
        
        return Response({
            'success': True,
            'data': {
                'products': formatted_products,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total_items': queryset.count(),
                    'total_pages': total_pages,
                    'has_next': page < total_pages,
                    'has_prev': page > 1
                }
            }
        })


class NoonOrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Mock Noon Seller API - Orders
    Similar to: GET /seller/orders
    """
    serializer_class = NoonOrderSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'order_nr'
    
    def get_queryset(self):
        queryset = NoonOrder.objects.filter(user=self.request.user).prefetch_related('items')
        
        # Filter by status
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        # Filter by date range
        from_date = self.request.query_params.get('from_date')
        if from_date:
            try:
                date = datetime.fromisoformat(from_date)
                queryset = queryset.filter(order_date__gte=date)
            except:
                pass
        
        to_date = self.request.query_params.get('to_date')
        if to_date:
            try:
                date = datetime.fromisoformat(to_date)
                queryset = queryset.filter(order_date__lte=date)
            except:
                pass
        
        # Filter by city
        city = self.request.query_params.get('city')
        if city:
            queryset = queryset.filter(address_city__icontains=city)
        
        return queryset.order_by('-order_date')
    
    def list(self, request, *args, **kwargs):
        """Mock Noon GetOrders API response format"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Pagination
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 50))
        
        offset = (page - 1) * limit
        orders = queryset[offset:offset + limit]
        
        formatted_orders = []
        for order in orders:
            items_serializer = NoonOrderItemSerializer(order.items.all(), many=True)
            
            formatted_items = []
            for item in items_serializer.data:
                formatted_items.append({
                    'item_id': item['order_item_id'],
                    'sku': item['partner_sku'],
                    'noon_sku': item['noon_sku'],
                    'name': item['name'],
                    'quantity': item['quantity'],
                    'price': {
                        'currency': 'AED',
                        'unit_price': float(item['unit_price']),
                        'total_price': float(item['total_price'])
                    },
                    'status': item['status']
                })
            
            formatted_orders.append({
                'order_nr': order.order_nr,
                'order_date': order.order_date.isoformat(),
                'status': order.status,
                'customer': {
                    'first_name': order.customer_first_name,
                    'last_name': order.customer_last_name,
                    'email': order.customer_email,
                    'phone': order.customer_phone
                },
                'payment': {
                    'method': order.payment_method,
                    'total': {
                        'currency': order.currency,
                        'value': float(order.total_amount)
                    }
                },
                'shipping': {
                    'provider': order.delivery_provider,
                    'tracking_number': order.tracking_number,
                    'address': {
                        'city': order.address_city,
                        'area': order.address_area,
                        'street': order.address_street
                    },
                    'is_express': order.is_express
                },
                'items': formatted_items,
                'items_count': len(formatted_items)
            })
        
        total_pages = (queryset.count() + limit - 1) // limit
        
        return Response({
            'success': True,
            'data': {
                'orders': formatted_orders,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total_items': queryset.count(),
                    'total_pages': total_pages
                }
            }
        })
    
    @action(detail=False, methods=['post'], url_path='status-update')
    def update_status(self, request):
        """Mock Noon Update Order Status API"""
        order_nr = request.data.get('order_nr')
        new_status = request.data.get('status')
        
        if not order_nr or not new_status:
            return Response({
                'success': False,
                'error': {
                    'code': 'MISSING_PARAMS',
                    'message': 'order_nr and status are required'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            order = NoonOrder.objects.get(order_nr=order_nr, user=request.user)
            order.status = new_status
            order.save()
            
            return Response({
                'success': True,
                'data': {
                    'order_nr': order.order_nr,
                    'status': order.status,
                    'updated_at': order.updated_at.isoformat()
                }
            })
        except NoonOrder.DoesNotExist:
            return Response({
                'success': False,
                'error': {
                    'code': 'ORDER_NOT_FOUND',
                    'message': f'Order {order_nr} not found'
                }
            }, status=status.HTTP_404_NOT_FOUND)


class NoonInventoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Mock Noon Seller API - Inventory
    Similar to: GET /seller/inventory
    """
    serializer_class = NoonInventorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = NoonInventory.objects.filter(user=self.request.user)
        
        # Filter by SKU
        sku = self.request.query_params.get('sku')
        if sku:
            queryset = queryset.filter(partner_sku=sku)
        
        # Filter by SKUs (comma-separated)
        skus = self.request.query_params.get('skus')
        if skus:
            sku_list = skus.split(',')
            queryset = queryset.filter(partner_sku__in=sku_list)
        
        # Filter by warehouse
        warehouse = self.request.query_params.get('warehouse')
        if warehouse:
            queryset = queryset.filter(warehouse_code=warehouse)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """Mock Noon GetInventory API response format"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Pagination
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 100))
        
        offset = (page - 1) * limit
        items = queryset[offset:offset + limit]
        serializer = self.get_serializer(items, many=True)
        
        formatted_inventory = []
        for item in serializer.data:
            formatted_inventory.append({
                'sku': item['partner_sku'],
                'noon_sku': item['noon_sku'],
                'barcode': item.get('barcode', ''),
                'stock': {
                    'available': item['quantity'],
                    'reserved': item['reserved_quantity'],
                    'total': item['quantity'] + item['reserved_quantity']
                },
                'warehouse': {
                    'code': item.get('warehouse_code', ''),
                    'name': item.get('warehouse_code', '')
                },
                'last_updated': item.get('last_updated')
            })
        
        return Response({
            'success': True,
            'data': {
                'inventory': formatted_inventory,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total_items': queryset.count()
                }
            }
        })
    
    @action(detail=False, methods=['post'], url_path='update')
    def update_stock(self, request):
        """Mock Noon Update Stock API"""
        updates = request.data.get('updates', [])
        
        if not updates:
            return Response({
                'success': False,
                'error': {
                    'code': 'MISSING_UPDATES',
                    'message': 'updates array is required'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        results = []
        for update in updates:
            sku = update.get('sku')
            quantity = update.get('quantity')
            
            try:
                inventory = NoonInventory.objects.get(
                    partner_sku=sku,
                    user=request.user
                )
                inventory.quantity = quantity
                inventory.save()
                results.append({
                    'sku': sku,
                    'status': 'success',
                    'new_quantity': inventory.quantity
                })
            except NoonInventory.DoesNotExist:
                results.append({
                    'sku': sku,
                    'status': 'error',
                    'message': 'SKU not found'
                })
        
        return Response({
            'success': True,
            'data': {
                'results': results,
                'updated_count': len([r for r in results if r['status'] == 'success'])
            }
        })