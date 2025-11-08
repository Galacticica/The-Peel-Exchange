from django.shortcuts import render
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
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


@require_GET
def stocks_list(request):
	"""Return a list of all stocks with name, symbol and current price."""
	data = []
	for stock in Stock.objects.all().order_by('symbol'):
		data.append({
			'name': stock.name,
			'symbol': stock.symbol,
			'price': round(stock.price, 2),
		})
	return JsonResponse(data, safe=False)


@require_GET
def stock_detail(request, symbol):
	"""Return details for a single stock by symbol."""
	try:
		stock = Stock.objects.get(symbol=symbol)
	except Stock.DoesNotExist:
		raise Http404("Stock not found")

	latest_timestamp = None
	try:
		latest = stock.history.order_by('-timestamp').first()
		if latest:
			latest_timestamp = latest.timestamp.isoformat()
	except Exception:
		latest_timestamp = None

	data = {
		'name': stock.name,
		'symbol': stock.symbol,
		'price': round(stock.price, 2),
		'latest_timestamp': latest_timestamp,
	}

	return JsonResponse(data)


@login_required
def market_home(request):
	"""Render the market homepage. The template uses the API endpoints to populate data."""
	return render(request, 'market/home.html')


