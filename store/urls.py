
from django.urls import path

from . import views

urlpatterns = [
    path('', views.store, name='store'),
    # Parent category view (outfit, shoes, combos)
    path('<slug:parent_slug>/', views.store, name='products_by_parent_category'),
    # Parent category with child category filter
    path('<slug:parent_slug>/<slug:child_slug>/', views.store, name='products_by_child_category'),
    # Product detail view
    path('product/<slug:parent_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),
    path('search/', views.search, name='search'),
    path('submit_review/<int:product_id>/', views.submit_review, name='submit_review'),
]
