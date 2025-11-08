from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from market.models import Stock


@require_GET
def ticker_data(request):
	"""Return JSON array of stocks with symbol, price and direction.

	direction: 1 = up, -1 = down, 0 = unchanged / unknown
	"""
	data = []
	for stock in Stock.objects.all():
		direction = 0
		try:
			history = list(stock.history.order_by('-timestamp')[:2])
			if len(history) >= 2:
				latest = history[0].price
				prev = history[1].price
				if latest > prev:
					direction = 1
				elif latest < prev:
					direction = -1
		except Exception:
			pass

		data.append({
			'symbol': stock.symbol,
			'price': round(stock.price, 2),
			'direction': direction,
		})

	return JsonResponse(data, safe=False)
