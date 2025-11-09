"""
File: views.py
Author: Reagan Zierke <reaganzierke@gmail.com>
Date: 2025-11-08
Description: Views for the market app
"""


from django.shortcuts import render
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from market.models import Stock, Holding, MarketEvent, MarketEventApplication, StockPriceHistory
from django.utils.html import escape
from django.db import transaction
from django.db.models import Sum, F, FloatField, Value
from django.db.models.functions import Coalesce
from accounts.models import User
import json
import random


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

	holdings_qs = Holding.objects.filter(user=user).select_related('stock')
	holdings = []
	stocks_total = 0.0
	for h in holdings_qs:
		price = float(h.stock.price)
		shares = int(h.shares)
		total = round(price * shares, 2)
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
		user.refresh_from_db()
		if user.balance < cost:
			return JsonResponse({'error': 'Insufficient funds', 'balance': user.balance}, status=400)

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


@login_required
@require_POST
def sell_stock(request):
	"""Handle selling a stock for the logged-in user.

	Expects JSON body: {"symbol": "ABC", "amount": 1}
	Validations:
	- amount must be integer >= 1
	- user must own at least that many shares
	- if user sells all shares, the Holding is deleted
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

	user = request.user

	with transaction.atomic():
		user.refresh_from_db()
		try:
			holding = Holding.objects.select_for_update().get(user=user, stock=stock)
		except Holding.DoesNotExist:
			return JsonResponse({'error': 'You do not own this stock'}, status=400)

		if amount > holding.shares:
			return JsonResponse({'error': 'Cannot sell more shares than owned', 'shares': holding.shares}, status=400)

		proceeds = stock.price * amount

		user.balance = user.balance + proceeds
		user.save()

		remaining = holding.shares - amount
		if remaining <= 0:
			holding.delete()
			remaining = 0
		else:
			holding.shares = remaining
			holding.save()

	return JsonResponse({
		'success': True,
		'balance': round(user.balance, 2),
		'holding': {
			'symbol': stock.symbol,
			'shares': remaining,
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
def latest_event(request):
	"""Return the most recent MarketEventApplication as JSON.

	If an application exists, return both event and stock fields plus a
	server-rendered `rendered_text` where {company} is replaced with the
	affected stock's name. If none exist, return {'event': None}.
	"""
	try:
		app = MarketEventApplication.objects.select_related('event', 'stock').order_by('-created_at').first()
	except Exception:
		app = None

	if not app:
		return JsonResponse({'event': None})

	ev = app.event
	stock = app.stock

	try:
		rendered = ev.text.replace('{company}', escape(stock.name))
	except Exception:
		rendered = ev.text

	data = {
		'application_id': app.id,
		'id': ev.id,
		'text': ev.text,
		'rendered_text': rendered,
		'impact_level': ev.impact_level,
		'created_at': app.created_at.isoformat(),
		'stock': {
			'id': stock.id,
			'symbol': stock.symbol,
			'name': stock.name,
			'price': round(stock.price, 2),
		}
	}

	return JsonResponse({'event': data})


@login_required
def leaderboard(request):
	"""Display the top 25 users by total portfolio worth."""
	users_data = []
	
	for user in User.objects.all():
		balance = float(user.balance or 0.0)
		
		holdings = Holding.objects.filter(user=user).select_related('stock')
		stocks_total = sum(float(h.stock.price) * int(h.shares) for h in holdings)
		
		portfolio_worth = balance + stocks_total
		
		users_data.append({
			'user': user,
			'balance': balance,
			'stocks_total': stocks_total,
			'portfolio_worth': portfolio_worth,
		})
	
	users_data.sort(key=lambda x: x['portfolio_worth'], reverse=True)
	top_users = users_data[:25]
	
	for i, user_data in enumerate(top_users, 1):
		user_data['rank'] = i
	
	context = {
		'top_users': top_users,
	}
	
	return render(request, 'market/leaderboard.html', context)


@staff_member_required
@require_POST
def admin_force_event(request):
	"""Admin endpoint to force a market event of a specific impact level.
	
	Expects JSON body: {"impact_level": "minor|moderate|major|severe", "stock_symbol": "CORN"}
	"""
	try:
		payload = json.loads(request.body.decode('utf-8'))
		impact_level = payload.get('impact_level', 'minor')
		stock_symbol = payload.get('stock_symbol')
		
		valid_levels = ['minor', 'moderate', 'major', 'severe']
		if impact_level not in valid_levels:
			return JsonResponse({'error': 'Invalid impact level'}, status=400)
		
		events = MarketEvent.objects.filter(impact_level=impact_level)
		if not events.exists():
			return JsonResponse({'error': f'No events found for impact level: {impact_level}'}, status=404)
		
		event = random.choice(events)
		
		if stock_symbol:
			try:
				stock = Stock.objects.get(symbol=stock_symbol)
			except Stock.DoesNotExist:
				return JsonResponse({'error': f'Stock {stock_symbol} not found'}, status=404)
		else:
			stocks = Stock.objects.all()
			if not stocks.exists():
				return JsonResponse({'error': 'No stocks available'}, status=404)
			stock = random.choice(stocks)
		
		event.apply_event(stock=stock)
		
		MarketEventApplication.objects.create(event=event, stock=stock)
		
		return JsonResponse({
			'success': True,
			'event': event.text,
			'stock': stock.symbol,
			'impact_level': impact_level,
			'new_price': round(stock.price, 2)
		})
		
	except json.JSONDecodeError:
		return JsonResponse({'error': 'Invalid JSON'}, status=400)
	except Exception as e:
		return JsonResponse({'error': str(e)}, status=500)


@staff_member_required
@require_POST
def admin_add_money(request):
	"""Admin endpoint to add money to a specified user's account.
	
	Expects JSON body: {"user_id": 1, "amount": 1000.0}
	"""
	try:
		payload = json.loads(request.body.decode('utf-8'))
		user_id = payload.get('user_id')
		amount = float(payload.get('amount', 0))
		
		if not user_id:
			return JsonResponse({'error': 'User ID is required'}, status=400)
		
		if amount <= 0:
			return JsonResponse({'error': 'Amount must be positive'}, status=400)
		
		try:
			target_user = User.objects.get(id=user_id)
		except User.DoesNotExist:
			return JsonResponse({'error': 'User not found'}, status=404)
		
		target_user.balance = float(target_user.balance or 0.0) + amount
		target_user.save()
		
		return JsonResponse({
			'success': True,
			'user_name': target_user.get_full_name() or target_user.email,
			'added': round(amount, 2),
			'new_balance': round(target_user.balance, 2)
		})
		
	except (json.JSONDecodeError, ValueError):
		return JsonResponse({'error': 'Invalid data'}, status=400)
	except Exception as e:
		return JsonResponse({'error': str(e)}, status=500)


@staff_member_required
@require_GET
def admin_list_users(request):
	"""Admin endpoint to get a list of all users with their balances.
	
	Returns JSON array of users with id, name, email, and balance.
	"""
	try:
		users_data = []
		for user in User.objects.all().order_by('email'):
			users_data.append({
				'id': user.id,
				'name': user.get_full_name() or 'No Name',
				'email': user.email,
				'balance': round(float(user.balance or 0.0), 2)
			})
		
		return JsonResponse({'users': users_data})
		
	except Exception as e:
		return JsonResponse({'error': str(e)}, status=500)


@staff_member_required
@require_POST
def admin_set_stock_price(request):
	"""Admin endpoint to set a stock's price directly.
	
	Expects JSON body: {"stock_symbol": "CORN", "price": 15.50}
	"""
	try:
		payload = json.loads(request.body.decode('utf-8'))
		stock_symbol = payload.get('stock_symbol')
		price = float(payload.get('price', 0))
		
		if not stock_symbol:
			return JsonResponse({'error': 'Stock symbol is required'}, status=400)
		
		if price <= 0:
			return JsonResponse({'error': 'Price must be positive'}, status=400)
		
		try:
			stock = Stock.objects.get(symbol=stock_symbol)
		except Stock.DoesNotExist:
			return JsonResponse({'error': f'Stock {stock_symbol} not found'}, status=404)
		
		stock.price = price
		stock.save()
		
		from market.models import StockPriceHistory
		StockPriceHistory.objects.create(stock=stock, price=price)
		
		return JsonResponse({
			'success': True,
			'stock': stock.symbol,
			'new_price': round(stock.price, 2)
		})
		
	except (json.JSONDecodeError, ValueError):
		return JsonResponse({'error': 'Invalid data'}, status=400)
	except Exception as e:
		return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST
def take_loan(request):
	"""Allow users to take a $20 emergency loan if portfolio is below $3."""
	try:
		user = request.user
		
		if user.has_loan:
			return JsonResponse({'error': 'You already have an active loan'}, status=400)
		
		holdings = Holding.objects.filter(user=user).select_related('stock')
		stocks_total = sum(float(h.stock.price) * int(h.shares) for h in holdings)
		portfolio_worth = float(user.balance or 0.0) + stocks_total
		
		if portfolio_worth >= 3.0:
			return JsonResponse({'error': 'You must have less than $3 total to qualify for a loan'}, status=400)
		
		LOAN_AMOUNT = 20.0
		user.has_loan = True
		user.loan_amount = LOAN_AMOUNT * 1.25  
		user.balance = float(user.balance or 0.0) + LOAN_AMOUNT
		user.save()
		
		return JsonResponse({
			'success': True,
			'loan_given': LOAN_AMOUNT,
			'to_repay': user.loan_amount,
			'new_balance': round(user.balance, 2)
		})
		
	except Exception as e:
		return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_GET
def check_loan_status(request):
	"""Check if user has a loan and if they can repay it."""
	try:
		user = request.user
		
		holdings = Holding.objects.filter(user=user).select_related('stock')
		stocks_total = sum(float(h.stock.price) * int(h.shares) for h in holdings)
		portfolio_worth = float(user.balance or 0.0) + stocks_total
		
		if user.has_loan and user.balance >= 50.0:
			user.balance = float(user.balance) - user.loan_amount
			user.has_loan = False
			repaid_amount = user.loan_amount
			user.loan_amount = 0.0
			user.save()
			
			return JsonResponse({
				'has_loan': False,
				'auto_repaid': True,
				'repaid_amount': round(repaid_amount, 2),
				'new_balance': round(user.balance, 2),
				'portfolio_worth': round(portfolio_worth, 2),
				'eligible_for_loan': portfolio_worth < 3.0
			})
		
		return JsonResponse({
			'has_loan': user.has_loan,
			'loan_amount': round(user.loan_amount, 2) if user.has_loan else 0,
			'balance': round(user.balance, 2),
			'portfolio_worth': round(portfolio_worth, 2),
			'eligible_for_loan': portfolio_worth < 3.0 and not user.has_loan
		})
		
	except Exception as e:
		return JsonResponse({'error': str(e)}, status=500)


@staff_member_required
@require_POST
def admin_market_event(request):
	"""Admin endpoint to trigger market-wide events.
	
	Expects JSON body: {"event_type": "boom" | "crisis"}
	boom: increases all stocks by 25-50%
	crisis: decreases all stocks by 25-50%
	"""
	try:
		payload = json.loads(request.body.decode('utf-8'))
		event_type = payload.get('event_type')
		
		if event_type not in ['boom', 'crisis']:
			return JsonResponse({'error': 'Invalid event type. Use "boom" or "crisis"'}, status=400)
		
		stocks = Stock.objects.all()
		if not stocks.exists():
			return JsonResponse({'error': 'No stocks available'}, status=404)
		
		stocks_affected = 0
		
		for stock in stocks:
			impact = random.uniform(0.25, 0.50)
			
			if event_type == 'boom':
				stock.price = max(0.1, stock.price * (1 + impact))
			else:  
				stock.price = max(0.1, stock.price * (1 - impact))
			
			stock.save()
			
			StockPriceHistory.objects.create(stock=stock, price=stock.price)
			stocks_affected += 1
		
		event_names = {
			'boom': 'Golden Peel Boom',
			'crisis': 'Bruised Peel Crisis'
		}
		
		return JsonResponse({
			'success': True,
			'event_type': event_type,
			'event_name': event_names[event_type],
			'stocks_affected': stocks_affected
		})
		
	except json.JSONDecodeError:
		return JsonResponse({'error': 'Invalid JSON'}, status=400)
	except Exception as e:
		return JsonResponse({'error': str(e)}, status=500)
