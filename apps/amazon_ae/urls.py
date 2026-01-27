from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'products', views.AmazonProductViewSet, basename='amazon-products')
router.register(r'orders', views.AmazonOrderViewSet, basename='amazon-orders')
router.register(r'inventory', views.AmazonInventoryViewSet, basename='amazon-inventory')

urlpatterns = [
    path('', include(router.urls)),
]