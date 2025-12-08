from django.urls import path
from . import views
  

urlpatterns = [
    path('place_order/', views.place_order, name='place_order'),
    path('order_complete/<str:secure_token>/',views.order_complete, name='order_complete'),
    path('order_complete/',views.order_complete_old, name='order_complete_old'), # Keep old URL for backward compatibility temporarily
    path('track_order/<str:tracking_id>/', views.track_order, name='track_order'),
]
