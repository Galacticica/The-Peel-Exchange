from django.core.management.base import BaseCommand
from market.models import Stock
from django.utils import timezone

class Command(BaseCommand):
    help = "Randomly fluctuate stock prices"

    def handle(self, *args, **kwargs):
        for stock in Stock.objects.all():
            stock.random_fluctuate()
        self.stdout.write(self.style.SUCCESS("Stock prices updated!"))

        # Append a timestamp to a simple log file so cron runs can be verified.
        try:
            with open('/tmp/update_stocks.log', 'a') as f:
                f.write(f"{timezone.now().isoformat()} - update_stocks run\n")
        except Exception:
            # Do not raise from the cron job; it's only for basic verification.
            pass