"""
File: admin.py
Author: Reagan Zierke <reaganzierke@gmail.com>
Date: 2025-11-08
Description: Admin interface for market-related models.
"""


from django.contrib import admin
from .models import Stock, Holding, MarketEvent, StockPriceHistory

admin.site.register(Stock)
admin.site.register(Holding)
admin.site.register(MarketEvent)
admin.site.register(StockPriceHistory)
