"""
File: models.py
Author: Reagan Zierke <reaganzierke@gmail.com>
Date: 2025-11-08
Description: Models for the market app.
"""


from django.db import models
import random
from django.utils import timezone

class Stock(models.Model):
    """Model representing a stock in the market."""
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10, unique=True)
    price = models.FloatField(default=10.0)
    volatility_min = models.FloatField(null=True, blank=True)
    volatility_max = models.FloatField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        """Override save to set random volatility if not already set."""
        if self.volatility_min is None or self.volatility_max is None:
            self.volatility_min = -1 * random.uniform(0.05, 0.15)
            self.volatility_max = random.uniform(0.05, 0.15)
        super().save(*args, **kwargs)
    
    def random_fluctuate(self):
        """Randomly fluctuate the stock price and maintain price history.
        
        Uses an asymmetric mean-reverting model: strong recovery for crashed stocks,
        minimal resistance for successful stocks.
        """
        if self.volatility_min is None or self.volatility_max is None or self.volatility_min != -1 * self.volatility_max:
            base_volatility = random.uniform(0.05, 0.15)
            self.volatility_min = -1 * base_volatility
            self.volatility_max = base_volatility
        
        random_change = random.uniform(self.volatility_min, self.volatility_max)

        target_price = 10.0
        
        if self.price < target_price:
            upward_strength = 0.10
            reversion = upward_strength * ((target_price - self.price) / target_price)
        else:
            downward_strength = 0.03
            reversion = -downward_strength * ((self.price - target_price) / target_price)
        
        total_change = random_change + reversion
        
        self.price = max(0.1, self.price * (1 + total_change))
        super().save()  

        StockPriceHistory.objects.create(stock=self, price=self.price)

        history = self.history.order_by('-timestamp')
        if history.count() > 2000:
            for old in history[2000:]:
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
    text = models.CharField(max_length=200)
    impact_level = models.CharField(
        max_length=50,
        choices=[
            ("minor", "Slightly"),
            ("moderate", "Moderately"),
            ("major", "Significantly"),
            ("severe", "Severely"),
        ],
        default="minor",
    )
    impact_low = models.FloatField()
    impact_high = models.FloatField()
    
    def apply_event(self, stock):
        """Apply the market event to a given stock."""
        impact = random.uniform(self.impact_low, self.impact_high)
        stock.price = max(0.1, stock.price * (1 + (1.2*impact)))
        stock.save()

    def __str__(self):
        return f"{self.text} (Impact: {self.impact_low} - {self.impact_high})"


class MarketEventApplication(models.Model):
    """Record that a MarketEvent was applied to a specific Stock at a given time.

    This makes it easy to show the latest applied event and the affected stock.
    """
    event = models.ForeignKey(MarketEvent, on_delete=models.CASCADE, related_name='applications')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.event.text} -> {self.stock.symbol} @ {self.created_at.isoformat()}"

