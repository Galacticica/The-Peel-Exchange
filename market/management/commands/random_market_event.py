from django.core.management.base import BaseCommand
from market.models import Stock, MarketEvent, MarketEventApplication
from django.utils import timezone
import random

class Command(BaseCommand):
    help = "Randomly select and apply a market event"

    def handle(self, *args, **kwargs):
        events = MarketEvent.objects.all()
        
        event_type = random.randint(1, 100)
        if event_type <= 2:
            event = random.choice(events.filter(impact_level='severe'))
        elif event_type <= 10:
            event = random.choice(events.filter(impact_level='major'))
        elif event_type <= 30:
            event = random.choice(events.filter(impact_level='moderate'))
        else:
            event = random.choice(events.filter(impact_level='minor'))

        stock_to_affect = random.choice(Stock.objects.all())
        event.apply_event(stock=stock_to_affect)

        # record the application so the UI can show which stock was affected
        try:
            MarketEventApplication.objects.create(event=event, stock=stock_to_affect)
        except Exception:
            # don't fail the command if recording the application fails
            pass

        self.stdout.write(self.style.SUCCESS(f"Applied market event: {event}"))