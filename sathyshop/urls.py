"""sathyshop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls import handler404
from django.shortcuts import render

from sathyshop import views

urlpatterns = [
    # path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    path('admin/', admin.site.urls),
    path('',views.home,name='home'),
    path('store/',include('store.urls')),
    path('cart/',include('carts.urls')),
    path('accounts/',include('accounts.urls')),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('searchbar/', views.search_page, name='search_page'),

    #order
    path('orders/', include('orders.urls')),
]+  static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.BASE_DIR / 'static')

handler404 = 'sathyshop.views.custom_404'


