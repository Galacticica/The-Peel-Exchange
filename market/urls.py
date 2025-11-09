"""
File: urls.py
Author: Reagan Zierke
Date: 2025-11-08
Description: description
"""

from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.market_home, name='market-home'),
    path('portfolio/', views.portfolio, name='market-portfolio'),
    path('leaderboard/', views.leaderboard, name='market-leaderboard'),
]