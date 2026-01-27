from django.urls import path
from . import views

urlpatterns = [
    path('token/', views.obtain_token, name='obtain_token'),
    path('register/', views.register_credentials, name='register_credentials'),
]