from django.contrib import admin
from .models import Stock, Holding, MarketEvent
# Register your models here.
admin.site.register(Stock)
admin.site.register(Holding)
admin.site.register(MarketEvent)
