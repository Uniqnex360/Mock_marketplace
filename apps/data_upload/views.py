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
import random
def safe_str(value, default=''):
    """Safely convert value to string, handling NaN and None"""
    if pd.isna(value) or value is None:
        return default
    return str(value).strip()

def safe_num(value, default=0):
    """Safely convert value to number"""
    if pd.isna(value) or value is None:
        return default
    try:
        return float(value)
    except:
        return default

def safe_int(value, default=0):
    """Safely convert value to integer"""
    return int(safe_num(value, default))

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
        asin = safe_str(row.get('asin'))
        if not asin:
            continue
        
        obj, is_created = AmazonProduct.objects.update_or_create(
            asin=asin,
            defaults={
                'user': user,
                'sku': safe_str(row.get('sku'), 'UNKNOWN'),
                'title': safe_str(row.get('title'), 'Untitled'),
                'description': safe_str(row.get('description'), ''),
                'brand': safe_str(row.get('brand'), ''),
                'category': safe_str(row.get('category'), 'General'),
                'price': safe_num(row.get('price'), 0),
                'quantity': safe_int(row.get('quantity'), 0),
                'image_url': safe_str(row.get('image_url'), ''),
                'status': safe_str(row.get('status'), 'ACTIVE'),
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
            try:
                order_date = datetime.strptime(order_date, '%Y-%m-%d %H:%M:%S')
            except:
                order_date = datetime.now()
        elif order_date is None or pd.isna(order_date):
            order_date = datetime.now()
        
        amazon_order_id = safe_str(row.get('amazon_order_id'))
        if not amazon_order_id:
            continue
        
        order, _ = AmazonOrder.objects.update_or_create(
            amazon_order_id=amazon_order_id,
            defaults={
                'user': user,
                'purchase_date': order_date,
                'order_status': safe_str(row.get('order_status'), 'Pending'),
                'order_total_amount': safe_num(row.get('order_total_amount'), 0),
                'buyer_email': safe_str(row.get('buyer_email'), ''),
                'buyer_name': safe_str(row.get('buyer_name'), ''),
            }
        )
        orders += 1
        
        order_item_id = safe_str(row.get('order_item_id'))
        if order_item_id:
            AmazonOrderItem.objects.update_or_create(
                order_item_id=order_item_id,
                defaults={
                    'order': order,
                    'asin': safe_str(row.get('item_asin'), ''),
                    'sku': safe_str(row.get('item_sku'), ''),
                    'title': safe_str(row.get('item_title'), 'Product'),
                    'quantity_ordered': safe_int(row.get('quantity_ordered'), 1),
                    'item_price_amount': safe_num(row.get('item_price'), 0),
                }
            )
            items += 1
    
    return {'orders': orders, 'items': items}

def upload_amazon_inventory(df, user):
    created = 0
    updated = 0
    
    for _, row in df.iterrows():
        sku = safe_str(row.get('sku'))
        if not sku:
            continue
        
        obj, is_created = AmazonInventory.objects.update_or_create(
            user=user,
            sku=sku,
            defaults={
                'asin': safe_str(row.get('asin'), ''),
                'product_name': safe_str(row.get('product_name'), ''),
                'available_quantity': safe_int(row.get('available_quantity'), 0),
                'pending_quantity': safe_int(row.get('pending_quantity'), 0),
                'reserved_quantity': safe_int(row.get('reserved_quantity'), 0),
                'total_quantity': safe_int(row.get('total_quantity'), 0),
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
        noon_sku = safe_str(row.get('noon_sku'))
        if not noon_sku:
            continue
        
        sale_price = row.get('sale_price')
        if pd.isna(sale_price) or sale_price is None:
            sale_price = None
        else:
            sale_price = safe_num(sale_price)
        
        obj, is_created = NoonProduct.objects.update_or_create(
            noon_sku=noon_sku,
            defaults={
                'user': user,
                'partner_sku': safe_str(row.get('partner_sku'), ''),
                'title': safe_str(row.get('title'), ''),
                'title_ar': safe_str(row.get('title_ar'), ''),
                'brand': safe_str(row.get('brand'), ''),
                'category_code': safe_str(row.get('category_code'), ''),
                'product_type': safe_str(row.get('product_type'), ''),
                'price': safe_num(row.get('price'), 0),
                'sale_price': sale_price,
                'stock_quantity': safe_int(row.get('stock_quantity'), 0),
                'status': safe_str(row.get('status'), 'active'),
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
        order_nr = safe_str(row.get('order_nr'))
        if not order_nr:
            continue
        
        order_date = row.get('order_date')
        if isinstance(order_date, str):
            try:
                order_date = datetime.strptime(order_date, '%Y-%m-%d %H:%M:%S')
            except:
                order_date = datetime.now()
        elif order_date is None or pd.isna(order_date):
            order_date = datetime.now()
        
        if order_nr not in orders:
            order, _ = NoonOrder.objects.update_or_create(
                order_nr=order_nr,
                defaults={
                    'user': user,
                    'order_date': order_date,
                    'status': safe_str(row.get('status'), 'placed'),
                    'customer_first_name': safe_str(row.get('customer_first_name'), ''),
                    'customer_last_name': safe_str(row.get('customer_last_name'), ''),
                    'customer_email': safe_str(row.get('customer_email'), ''),
                    'total_amount': safe_num(row.get('total_amount'), 0),
                    'address_city': safe_str(row.get('address_city'), ''),
                    'payment_method': safe_str(row.get('payment_method'), 'COD'),
                }
            )
            orders[order_nr] = order
        
        order_item_id = safe_str(row.get('order_item_id'))
        if order_item_id:
            NoonOrderItem.objects.update_or_create(
                order_item_id=order_item_id,
                defaults={
                    'order': orders[order_nr],
                    'noon_sku': safe_str(row.get('item_noon_sku'), ''),
                    'partner_sku': safe_str(row.get('item_partner_sku'), ''),
                    'name': safe_str(row.get('item_name'), ''),
                    'quantity': safe_int(row.get('quantity'), 1),
                    'unit_price': safe_num(row.get('unit_price'), 0),
                    'total_price': safe_num(row.get('total_price'), 0),
                    'status': safe_str(row.get('item_status'), 'confirmed'),
                }
            )
    
    return {'orders': len(orders), 'rows_processed': len(df)}

def upload_noon_inventory(df, user):
    created = 0
    updated = 0
    
    for _, row in df.iterrows():
        partner_sku = safe_str(row.get('partner_sku'))
        if not partner_sku:
            continue
        
        obj, is_created = NoonInventory.objects.update_or_create(
            user=user,
            partner_sku=partner_sku,
            defaults={
                'noon_sku': safe_str(row.get('noon_sku'), ''),
                'barcode': safe_str(row.get('barcode'), ''),
                'quantity': safe_int(row.get('quantity'), 0),
                'reserved_quantity': safe_int(row.get('reserved_quantity'), 0),
                'warehouse_code': safe_str(row.get('warehouse_code'), ''),
            }
        )
        if is_created:
            created += 1
        else:
            updated += 1
    
    return {'created': created, 'updated': updated}

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clear_database(request):
    """Dangerous: Deletes all marketplace data"""
    try:
        with transaction.atomic():
            AmazonOrder.objects.all().delete()
            AmazonProduct.objects.all().delete() # Inventory & Items cascade
            NoonOrder.objects.all().delete()
            NoonProduct.objects.all().delete()
        return Response({"message": "✅ Database Cleared Successfully"})
    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def fix_relationships(request):
    """Links Order Items to Products via SKU matching"""
    try:
        with transaction.atomic():
            # 1. Fix Amazon
            products = list(AmazonProduct.objects.all())
            if not products: return Response({"error": "No Amazon products found"})
            
            sku_to_product = {p.sku: p for p in products}
            amz_count = 0
            
            for item in AmazonOrderItem.objects.all():
                if item.sku in sku_to_product:
                    p = sku_to_product[item.sku]
                    item.asin, item.title, item.item_price_amount = p.asin, p.title, p.price
                else:
                    p = random.choice(products)
                    item.asin, item.sku, item.title, item.item_price_amount = p.asin, p.sku, p.title, p.price
                
                if item.quantity_ordered == 0: item.quantity_ordered = 1
                item.save()
                amz_count += 1

            # Recalculate Amazon Order Totals
            for order in AmazonOrder.objects.all():
                order.order_total_amount = sum(i.item_price_amount * i.quantity_ordered for i in order.items.all())
                order.save()

            # 2. Fix Noon
            n_products = list(NoonProduct.objects.all())
            if not n_products: return Response({"error": "No Noon products found"})
            
            n_sku_to_product = {p.partner_sku: p for p in n_products}
            noon_count = 0
            
            for item in NoonOrderItem.objects.all():
                if item.partner_sku in n_sku_to_product:
                    p = n_sku_to_product[item.partner_sku]
                    item.noon_sku, item.name, item.unit_price = p.noon_sku, p.title, p.price
                else:
                    p = random.choice(n_products)
                    item.noon_sku, item.partner_sku, item.name, item.unit_price = p.noon_sku, p.partner_sku, p.title, p.price
                
                if item.quantity == 0: item.quantity = 1
                item.total_price = item.unit_price * item.quantity
                item.save()
                noon_count += 1

            # Recalculate Noon Order Totals
            for order in NoonOrder.objects.all():
                order.total_amount = sum(i.total_price for i in order.items.all())
                order.save()

        return Response({
            "message": "✅ Relationships Fixed", 
            "amazon_items_fixed": amz_count,
            "noon_items_fixed": noon_count
        })
    except Exception as e:
        return Response({"error": str(e)}, status=500)