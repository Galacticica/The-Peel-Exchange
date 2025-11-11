"""
File: cleanup_stock_history.py
Author: Reagan Zierke <reaganzierke@gmail.com>
Date: 2025-11-10
Description: Command to clean up stock price history, keeping only the 5 most recent entries per stock
"""


from django.core.management.base import BaseCommand
from market.models import Stock, StockPriceHistory


class Command(BaseCommand):
    help = "Remove all stock price history entries except the 5 most recent for each stock"

    def handle(self, *args, **kwargs):
        stocks = Stock.objects.all()
        
        if not stocks.exists():
            self.stdout.write(self.style.WARNING("No stocks found"))
            return
        
        total_deleted = 0
        
        self.stdout.write(self.style.SUCCESS(f"Cleaning up history for {stocks.count()} stocks..."))
        
        for stock in stocks:
            # Get all history entries for this stock, ordered by timestamp descending
            all_history = stock.history.order_by('-timestamp')
            
            # Get the IDs of entries to keep (the 5 most recent)
            keep_ids = list(all_history.values_list('id', flat=True)[:5])
            
            # Delete all entries that are NOT in the keep list
            deleted_count = stock.history.exclude(id__in=keep_ids).delete()[0]
            
            if deleted_count > 0:
                total_deleted += deleted_count
                self.stdout.write(
                    f"  {stock.symbol}: Deleted {deleted_count} old entries, kept {len(keep_ids)}"
                )
            else:
                self.stdout.write(
                    f"  {stock.symbol}: Already has {all_history.count()} entries (no cleanup needed)"
                )
        
        self.stdout.write(
            self.style.SUCCESS(f"\n✓ Successfully deleted {total_deleted} old history entries")
        )
