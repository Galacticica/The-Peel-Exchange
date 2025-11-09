"""
File: update_stocks.py
Author: Reagan Zierke <reaganzierke@gmail.com>
Date: 2025-11-08
Description: Command to update stock prices.
"""


from django.core.management.base import BaseCommand
from market.models import Stock
from django.utils import timezone

class Command(BaseCommand):
    help = "Randomly fluctuate stock prices"

    def handle(self, *args, **kwargs):
        for stock in Stock.objects.all():
            stock.random_fluctuate()
        self.stdout.write(self.style.SUCCESS("Stock prices updated!"))