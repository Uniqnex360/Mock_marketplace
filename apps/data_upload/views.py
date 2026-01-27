import pandas as pd
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from django.http import HttpResponse
from django.conf import settings
from apps.amazon_ae.models import AmazonProduct, AmazonOrder, AmazonOrderItem, AmazonInventory
from apps.noon_ae.models import NoonProduct, NoonOrder, NoonOrderItem, NoonInventory
from datetime import datetime
import os

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_amazon_data(request):
    if 'file' not in request.FILES:
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

    file = request.FILES['file']
    data_type = request.data.get('data_type')

    if data_type not in ['products', 'orders', 'inventory']:
        return Response({'error': 'Invalid data type'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        df = pd.read_excel(file)
        df = df.where(pd.notnull(df), None)

        with transaction.atomic():
            if data_type == 'products':
                result = upload_amazon_products(df, request.user)
            elif data_type == 'orders':
                result = upload_amazon_orders(df, request.user)
            elif data_type == 'inventory':
                result = upload_amazon_inventory(df, request.user)

        return Response({
            'message': f'Successfully uploaded {data_type}',
            'details': result
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def upload_amazon_products(df, user):
    created = 0
    updated = 0
    for _, row in df.iterrows():
        obj, is_created = AmazonProduct.objects.update_or_create(
            asin=row.get('asin'),
            defaults={
                'user': user,
                'sku': row.get('sku', ''),
                'title': row.get('title', ''),
                'description': row.get('description', ''),
                'brand': row.get('brand', ''),
                'category': row.get('category', ''),
                'price': row.get('price', 0),
                'quantity': row.get('quantity', 0),
                'image_url': row.get('image_url', ''),
                'status': row.get('status', 'ACTIVE'),
            }
        )
        if is_created:
            created += 1
        else:
            updated += 1
    return {'created': created, 'updated': updated}

def upload_amazon_orders(df, user):
    orders = 0
    items = 0
    for _, row in df.iterrows():
        order_date = row.get('purchase_date')
        if isinstance(order_date, str):
            order_date = datetime.strptime(order_date, '%Y-%m-%d %H:%M:%S')

        order, _ = AmazonOrder.objects.update_or_create(
            amazon_order_id=row.get('amazon_order_id'),
            defaults={
                'user': user,
                'purchase_date': order_date,
                'order_status': row.get('order_status', 'Pending'),
                'order_total_amount': row.get('order_total_amount', 0),
                'buyer_email': row.get('buyer_email', ''),
                'buyer_name': row.get('buyer_name', ''),
            }
        )
        orders += 1

        if row.get('order_item_id'):
            AmazonOrderItem.objects.update_or_create(
                order_item_id=row.get('order_item_id'),
                defaults={
                    'order': order,
                    'asin': row.get('item_asin', ''),
                    'sku': row.get('item_sku', ''),
                    'title': row.get('item_title', ''),
                    'quantity_ordered': row.get('quantity_ordered', 1),
                    'item_price_amount': row.get('item_price', 0),
                }
            )
            items += 1
    return {'orders': orders, 'items': items}

def upload_amazon_inventory(df, user):
    created = 0
    updated = 0
    for _, row in df.iterrows():
        obj, is_created = AmazonInventory.objects.update_or_create(
            user=user,
            sku=row.get('sku'),
            defaults={
                'asin': row.get('asin', ''),
                'product_name': row.get('product_name', ''),
                'available_quantity': row.get('available_quantity', 0),
                'pending_quantity': row.get('pending_quantity', 0),
                'reserved_quantity': row.get('reserved_quantity', 0),
                'total_quantity': row.get('total_quantity', 0),
            }
        )
        if is_created:
            created += 1
        else:
            updated += 1
    return {'created': created, 'updated': updated}

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_noon_data(request):
    if 'file' not in request.FILES:
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

    file = request.FILES['file']
    data_type = request.data.get('data_type')

    if data_type not in ['products', 'orders', 'inventory']:
        return Response({'error': 'Invalid data type'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        df = pd.read_excel(file)
        df = df.where(pd.notnull(df), None)

        with transaction.atomic():
            if data_type == 'products':
                result = upload_noon_products(df, request.user)
            elif data_type == 'orders':
                result = upload_noon_orders(df, request.user)
            elif data_type == 'inventory':
                result = upload_noon_inventory(df, request.user)

        return Response({
            'message': f'Successfully uploaded {data_type}',
            'details': result
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def upload_noon_products(df, user):
    created = 0
    updated = 0
    for _, row in df.iterrows():
        obj, is_created = NoonProduct.objects.update_or_create(
            noon_sku=row.get('noon_sku'),
            defaults={
                'user': user,
                'partner_sku': row.get('partner_sku', ''),
                'title': row.get('title', ''),
                'title_ar': row.get('title_ar', ''),
                'brand': row.get('brand', ''),
                'category_code': row.get('category_code', ''),
                'product_type': row.get('product_type', ''),
                'price': row.get('price', 0),
                'sale_price': row.get('sale_price') if pd.notna(row.get('sale_price')) else None,
                'stock_quantity': row.get('stock_quantity', 0),
                'status': row.get('status', 'active'),
            }
        )
        if is_created:
            created += 1
        else:
            updated += 1
    return {'created': created, 'updated': updated}

def upload_noon_orders(df, user):
    orders = {}
    for _, row in df.iterrows():
        order_nr = row.get('order_nr')
        order_date = row.get('order_date')
        if isinstance(order_date, str):
            order_date = datetime.strptime(order_date, '%Y-%m-%d %H:%M:%S')

        if order_nr not in orders:
            order, _ = NoonOrder.objects.update_or_create(
                order_nr=order_nr,
                defaults={
                    'user': user,
                    'order_date': order_date,
                    'status': row.get('status', 'placed'),
                    'customer_first_name': row.get('customer_first_name', ''),
                    'customer_last_name': row.get('customer_last_name', ''),
                    'customer_email': row.get('customer_email', ''),
                    'total_amount': row.get('total_amount', 0),
                    'address_city': row.get('address_city', ''),
                }
            )
            orders[order_nr] = order

        if pd.notna(row.get('order_item_id')):
            NoonOrderItem.objects.update_or_create(
                order_item_id=row.get('order_item_id'),
                defaults={
                    'order': orders[order_nr],
                    'noon_sku': row.get('item_noon_sku', ''),
                    'partner_sku': row.get('item_partner_sku', ''),
                    'name': row.get('item_name', ''),
                    'quantity': row.get('quantity', 1),
                    'unit_price': row.get('unit_price', 0),
                    'total_price': row.get('total_price', 0),
                }
            )
    return {'orders': len(orders), 'rows_processed': len(df)}

def upload_noon_inventory(df, user):
    created = 0
    updated = 0
    for _, row in df.iterrows():
        obj, is_created = NoonInventory.objects.update_or_create(
            user=user,
            partner_sku=row.get('partner_sku'),
            defaults={
                'noon_sku': row.get('noon_sku', ''),
                'barcode': row.get('barcode', ''),
                'quantity': row.get('quantity', 0),
                'reserved_quantity': row.get('reserved_quantity', 0),
                'warehouse_code': row.get('warehouse_code', ''),
            }
        )
        if is_created:
            created += 1
        else:
            updated += 1
    return {'created': created, 'updated': updated}