from django.db import models
import random

class Stock(models.Model):
    """Model representing a stock in the market."""
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10, unique=True)
    price = models.FloatField(default=10.0)
    
    def random_fluctuate(self):
        change = random.uniform(-0.05, 0.05)
        self.price = max(0.1, self.price * (1 + change))
        self.save()

    def __str__(self):
        return f"{self.name} ({self.symbol}): ${self.price:.2f}"

class Holding(models.Model):
    """Model representing a user's holding of a stock."""
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    shares = models.IntegerField(default=0)

class MarketEvent(models.Model):
    """Model representing a market event that can impact stock prices."""
    text = models.CharField(max_length=200)
    impact = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

