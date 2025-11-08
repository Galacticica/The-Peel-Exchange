from django.db import models
import random
from django.utils import timezone

class Stock(models.Model):
    """Model representing a stock in the market."""
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10, unique=True)
    price = models.FloatField(default=10.0)
    
    def random_fluctuate(self):
        change = random.uniform(-0.05, 0.05)
        self.price = max(0.1, self.price * (1 + change))
        self.save()

        StockPriceHistory.objects.create(stock=self, price=self.price)

        history = self.history.order_by('-timestamp')
        if history.count() > 500:
            for old in history[500:]:
                old.delete()

    def __str__(self):
        return f"{self.name} ({self.symbol}): ${self.price:.2f}"
    
class StockPriceHistory(models.Model):
    """Model to keep track of stock price history."""
    stock = models.ForeignKey('Stock', on_delete=models.CASCADE, related_name='history')
    price = models.FloatField()
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['timestamp']  

    def __str__(self):
        return f"{self.stock.symbol} @ {self.price:.2f} ({self.timestamp})"

class Holding(models.Model):
    """Model representing a user's holding of a stock."""
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    shares = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} holds {self.shares} shares of {self.stock.symbol}"

class MarketEvent(models.Model):
    """Model representing a market event that can impact stock prices."""
    name = models.CharField(max_length=100)
    text = models.CharField(max_length=200)
    impact_level = models.CharField(max_length=50)
    impact_low = models.FloatField()
    impact_high = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def apply_event(self):
        affected_stocks = Stock.objects.all()
        for stock in affected_stocks:
            impact = random.uniform(self.impact_low, self.impact_high)
            stock.price = max(0.1, stock.price * (1 + impact))
            stock.save()

    def __str__(self):
        return f"{self.name} (Impact: {self.impact_low} - {self.impact_high})"

