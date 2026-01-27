from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'products', views.NoonProductViewSet, basename='noon-products')
router.register(r'orders', views.NoonOrderViewSet, basename='noon-orders')
router.register(r'inventory', views.NoonInventoryViewSet, basename='noon-inventory')

urlpatterns = [
    path('', include(router.urls)),
]