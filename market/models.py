from django.db import models

class Stock(models.Model):
    """Model representing a stock in the market."""
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10, unique=True)
    price = models.FloatField(default=10.0)
    volatility = models.FloatField(default=1.0)
