from django.shortcuts import render
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.decorators import login_required
from market.models import Stock, Holding
from django.db import transaction
import json


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


@login_required
def portfolio(request):
	"""Render the user's portfolio page with holdings and totals."""
	user = request.user

	# Fetch holdings and compute per-holding totals
	holdings_qs = Holding.objects.filter(user=user).select_related('stock')
	holdings = []
	stocks_total = 0.0
	for h in holdings_qs:
		price = float(h.stock.price)
		shares = int(h.shares)
		total = round(price * shares, 2)
		# determine direction based on the two most recent history points
		direction = 0
		try:
			history = list(h.stock.history.order_by('-timestamp')[:2])
			if len(history) >= 2:
				latest = history[0].price
				prev = history[1].price
				if latest > prev:
					direction = 1
				elif latest < prev:
					direction = -1
		except Exception:
			# if anything goes wrong, leave direction as 0 (unknown/unchanged)
			pass

		holdings.append({
			'name': h.stock.name,
			'symbol': h.stock.symbol,
			'price': round(price, 2),
			'shares': shares,
			'total': total,
			'direction': direction,
		})
		stocks_total += total

	# Portfolio worth = cash balance + value of stocks
	balance = float(user.balance or 0.0)
	portfolio_worth = round(balance + stocks_total, 2)

	context = {
		'user_obj': user,
		'balance': round(balance, 2),
		'holdings': holdings,
		'stocks_total': round(stocks_total, 2),
		'portfolio_worth': portfolio_worth,
	}

	return render(request, 'market/portfolio.html', context)


@login_required
@require_POST
def buy_stock(request):
	"""Handle buying a stock for the logged-in user.

	Expects JSON body: {"symbol": "ABC", "amount": 1}
	"""
	try:
		payload = json.loads(request.body.decode('utf-8'))
	except Exception:
		return JsonResponse({'error': 'Invalid JSON'}, status=400)

	symbol = payload.get('symbol')
	amount = payload.get('amount')

	try:
		amount = int(amount)
	except Exception:
		return JsonResponse({'error': 'Invalid amount'}, status=400)

	if amount < 1:
		return JsonResponse({'error': 'Amount must be at least 1'}, status=400)

	try:
		stock = Stock.objects.get(symbol=symbol)
	except Stock.DoesNotExist:
		return JsonResponse({'error': 'Stock not found'}, status=404)

	cost = stock.price * amount

	user = request.user

	with transaction.atomic():
		# reload fresh balance
		user.refresh_from_db()
		if user.balance < cost:
			return JsonResponse({'error': 'Insufficient funds', 'balance': user.balance}, status=400)

		# subtract balance
		user.balance = user.balance - cost
		user.save()

		holding, created = Holding.objects.get_or_create(user=user, stock=stock, defaults={'shares': amount})
		if not created:
			holding.shares = holding.shares + amount
			holding.save()

	return JsonResponse({
		'success': True,
		'balance': round(user.balance, 2),
		'holding': {
			'symbol': stock.symbol,
			'shares': holding.shares,
		}
	})


@require_GET
def stock_history(request, symbol):
	"""Return historical prices for a stock as a list of {timestamp, price}.

	Returns up to 500 most recent entries ordered from oldest->newest.
	"""
	try:
		stock = Stock.objects.get(symbol=symbol)
	except Stock.DoesNotExist:
		raise Http404("Stock not found")

	history_qs = stock.history.order_by('-timestamp')[:500]
	history = list(history_qs)
	history.reverse()

	data = []
	for h in history:
		data.append({
			'timestamp': h.timestamp.isoformat(),
			'price': round(h.price, 2),
		})

	return JsonResponse(data, safe=False)
	@require_GET
	def stock_history(request, symbol):
		"""Return historical prices for a stock as a list of {timestamp, price}.

		Returns up to 500 most recent entries ordered from oldest->newest.
		"""
		try:
			stock = Stock.objects.get(symbol=symbol)
		except Stock.DoesNotExist:
			raise Http404("Stock not found")

		history_qs = stock.history.order_by('-timestamp')[:500]
		history = list(history_qs)
		history.reverse()

		data = []
		for h in history:
			data.append({
				'timestamp': h.timestamp.isoformat(),
				'price': round(h.price, 2),
			})

		return JsonResponse(data, safe=False)


