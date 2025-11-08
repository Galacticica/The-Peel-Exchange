"""
URL configuration for conf project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from market import views as market_views

urlpatterns = [
    path('', include('accounts.urls')),
    # API endpoint for ticker data
    path('api/ticker/', market_views.ticker_data, name='ticker-data'),
    path('api/stocks/', market_views.stocks_list, name='stocks-list'),
    path('api/stocks/<str:symbol>/', market_views.stock_detail, name='stock-detail'),
    path('api/stocks/<str:symbol>/history/', market_views.stock_history, name='stock-history'),
    path('api/buy/', market_views.buy_stock, name='buy-stock'),
    path('api/sell/', market_views.sell_stock, name='sell-stock'),
    path('', include('market.urls')),
    path('__reload__/', include('django_browser_reload.urls')),
    path('admin/', admin.site.urls),
]