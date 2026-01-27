from django.urls import path
from . import views

urlpatterns = [
    path('amazon/', views.upload_amazon_data, name='upload_amazon_data'),
    path('noon/', views.upload_noon_data, name='upload_noon_data'),
]