"""
File: urls.py
Author: Reagan Zierke <reaganzierke@gmail.com>
Date: 2025-11-08
Description: URL configuration for the project.
"""


from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from market import views as market_views

urlpatterns = [
    path('', include('accounts.urls')),
    path('api/ticker/', market_views.ticker_data, name='ticker-data'),
    path('api/stocks/', market_views.stocks_list, name='stocks-list'),
    path('api/stocks/<str:symbol>/', market_views.stock_detail, name='stock-detail'),
    path('api/stocks/<str:symbol>/history/', market_views.stock_history, name='stock-history'),
    path('api/latest-event/', market_views.latest_event, name='latest-event'),
    path('api/buy/', market_views.buy_stock, name='buy-stock'),
    path('api/sell/', market_views.sell_stock, name='sell-stock'),
    path('api/admin/force-event/', market_views.admin_force_event, name='admin-force-event'),
    path('api/admin/add-money/', market_views.admin_add_money, name='admin-add-money'),
    path('api/admin/users/', market_views.admin_list_users, name='admin-list-users'),
    path('', include('market.urls')),
    path('__reload__/', include('django_browser_reload.urls')),
    path('admin/', admin.site.urls),
]