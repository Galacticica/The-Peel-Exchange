"""
File: rebase_stock_prices.py
Author: Reagan Zierke <reaganzierke@gmail.com>
Date: 2025-11-10
Description: Command to reset all stock prices to a reasonable range ($2-55)
"""


from django.core.management.base import BaseCommand
from market.models import Stock, StockPriceHistory
import random


class Command(BaseCommand):
    help = "Reset all stock prices to be between $2 and $55"

    def handle(self, *args, **kwargs):
        stocks = Stock.objects.all()
        
        if not stocks.exists():
            self.stdout.write(self.style.WARNING("No stocks found"))
            return
        
        self.stdout.write(self.style.SUCCESS(f"Rebasing {stocks.count()} stocks..."))
        
        for stock in stocks:
            old_price = stock.price
            new_price = round(random.uniform(2.0, 55.0), 2)
            
            stock.price = new_price
            stock.save()
            
            # Add to price history
            StockPriceHistory.objects.create(stock=stock, price=new_price)
            
            self.stdout.write(
                f"  {stock.symbol}: ${old_price:.2f} → ${new_price:.2f}"
            )
        
        self.stdout.write(self.style.SUCCESS(f"\n✓ Successfully rebased all stock prices to $2-$55 range"))
