from django.db import models

class Stock(models.Model):
    """Model representing a stock in the market."""
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10, unique=True)
    price = models.FloatField(default=10.0)
    volatility = models.FloatField(default=1.0)

class Holding(models.Model):
    """Model representing a user's holding of a stock."""
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)

class MarketEvent(models.Model):
    text = models.CharField(max_length=200)
    impact = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

