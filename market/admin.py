from django.contrib import admin
from .models import Stock, Holding, MarketEvent, StockPriceHistory

admin.site.register(Stock)
admin.site.register(Holding)
admin.site.register(MarketEvent)
admin.site.register(StockPriceHistory)
