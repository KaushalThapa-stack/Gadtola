from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.sitemaps.views import sitemap

from sathyshop import views
from sathyshop.sitemaps import StaticViewSitemap

sitemaps = {
    'static': StaticViewSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.home, name='home'),
    path('store/', include('store.urls')),
    path('cart/', include('carts.urls')),
    # Authentication removed - system is now anonymous/session-based only
    # path('accounts/', include('accounts.urls')),  # REMOVED
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('searchbar/', views.search_page, name='search_page'),

    # Orders URLs removed - no order database storage, only WhatsApp
    # path('orders/', include('orders.urls')),  # REMOVED

    # sitemap
    path(
        'sitemap.xml',
        sitemap,
        {'sitemaps': sitemaps},
        name='django-sitemap'
    ),
]

# static & media (development only)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / 'static')

handler404 = 'sathyshop.views.custom_404'

