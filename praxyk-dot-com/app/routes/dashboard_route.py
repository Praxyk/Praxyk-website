from flask import Flask, session, redirect, url_for, escape, request, render_template
import requests
import json
try:
	from urllib.parse import urlparse, parse_qs
except ImportError:
	from urlparse import urlparse, parse_qs
from app import app
from app import *
from app.util.defines import *
from app.routes import *
from app.routes.common import *

import datetime as dt
from datetime import timedelta
import dateutil.parser

from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound

cost_per_KB = 0.0001

dashboard_route = Blueprint('dashboard_route', __name__, template_folder='templates/dashboard')


@dashboard_route.route('/dashboard', methods=['GET'])
def dashboard():
	error = None
	ingress_str = "0.00 KB"
	dates4 = []
	date_counts = []
	newest_trans = {}
	if not session.get('token') or not session.get('user') :
		return redirect(url_for('users_route.login_page', _external=True))
	navbar = get_dashboard_navbar()
	sidebar = get_sidebar()
	transactions = get_transactions(paginated=False)
	for t in transactions :
		t['finished_at'] = "" if not t['finished_at'] else t['finished_at']
	num_transactions = len([] if not transactions else transactions)
	commands = set([trans['command_url'] for trans in transactions])
	command_counts = {url : 0 for url in commands}
	for trans in transactions :
		command_counts[trans['command_url']] += 1
	total_ingress = 0
	for trans in transactions :
		total_ingress += trans['size_total_KB']
	if total_ingress > 2000 : # > 2MB
		ingress_str = "{0:.2f}".format(total_ingress/1000.0)+" MB"
	else: 
		ingress_str = "{0:.2f}".format(total_ingress)+" KB"

	cost = "{0:.2f}".format(total_ingress*cost_per_KB)
	state_names = ['active', 'canceled', 'finished', 'failed']
	state_counts = [len([x for x in transactions if x['status'] == state]) for state in state_names]
	trans_card = ""


	if num_transactions > 0:

		newest_trans = transactions[0]

		trans_card = render_trans_card(transactions[0])
		dates = list(set([x['created_at'].split("T")[0] for x in transactions]))
		dates.sort()
		date_map = { dates[x]:x for x in range(0, len(dates)) }

		dates2 = list(set([dateutil.parser.parse(x['created_at'].split("T")[0]) for x in transactions]))
		dates2.sort()

		dates3 = []
		if ((dt.datetime.now()-dates2[0]).days) < 7 :
			for x in range(1, 8):
				dates3.append((dt.datetime.now()-timedelta(days=(7-x))).isoformat().split("T")[0])
				# dates3.reverse()
		else :
			for x in range(0, (dt.datetime.now()-dates2[0]).days) :
				dates3.append(dates2[0]+timedelta(days=x).isoformat().split("T")[0]) 

		date_map = { dates3[x]:x for x in range(0, len(dates3)) }


		for x in dates3 :
			date_counts.append(0)
		for x in transactions :
			try :
				date_counts[date_map[x['created_at'].split("T")[0]]] += 1
			except :
				continue

		dates4 = [str(x) for x in dates3]

	newest_trans['finished_at'] = "" if not newest_trans['finished_at'] else newest_trans['finished_at']

	return render_template('/dashboard/dashboard_home.html',
						   token=session['token'],
						   user=session['user'],
						   email=session['email'],
						   navbar=navbar,
						   transactions=transactions[-10:],
						   all_transactions=transactions,
						   num_transactions=num_transactions,
						   newest_trans=newest_trans,
						   command_counts=command_counts,
						   total_ingress=total_ingress,
						   ingress_str=ingress_str,
						   trans_card = trans_card,
						   cost_total=cost,
						   state_counts=state_counts,
						   state_names=state_names,
						   dates = dates4,
						   date_counts = date_counts,
						   sidebar=sidebar)

@dashboard_route.route('/dashboard/home/', methods=['GET'])
def dashboard_home():
	return redirect(url_for('dashboard_route.dashboard'))

@dashboard_route.route('/dashboard/transactions', methods=['GET'])
def transactions_tab():
	error = None
	if not session.get('token') or not session.get('user') :
		return redirect(url_for('users_route.login_page', _external=True))
	if request.values.get('last', None) :
		return transaction_tab(-1)
	page = request.values.get('page', None)
	page_size = request.values.get('page_size', 15)

	navbar = get_dashboard_navbar()
	sidebar = get_sidebar()
	tdict = get_transactions(page=page, page_size=page_size)
	transactions = tdict.get('transactions', []) if tdict else []
	transactions = transactions[::-1]
	for t in transactions :
		t['finished_at'] = "" if not t['finished_at'] else t['finished_at']
	trans_cards = [render_trans_card(t) for t in transactions]
	num_transactions = len(transactions)

	if not tdict or isinstance(tdict, list) :
		tdict = {}
	page = tdict.get('page', None)
	next_page = tdict.get('next_page', None)
	prev_page = tdict.get('prev_page', None)
	first_page = tdict.get('first_page', None)
	last_page = tdict.get('last_page', None)
	
	return render_template('/dashboard/dashboard_transactions.html',
						   token=session['token'],
						   user=session['user'],
						   email=session['email'],
						   navbar=navbar,
						   all_transactions=transactions,
						   num_transactions=num_transactions,
						   trans_cards = trans_cards,
						   page=page, next_page=next_page, prev_page=prev_page,
						   last_page=last_page, first_page=first_page,
						   sidebar=sidebar)


@dashboard_route.route('/dashboard/transaction/<int:id>', methods=['GET'])
def transaction_tab(id):
	error = None
	if not session.get('token') or not session.get('user') :
		return redirect(url_for('users_route.login_page', _external=True))
	navbar = get_dashboard_navbar()
	sidebar = get_sidebar()

	transaction =  {}

	if id == -1 :
		trs = get_transactions(reverse_sort=True, page=1, page_size=1)
		if trs and trs.get('transactions') :
			t = trs.get('transactions', [None])[0]
			transaction = t
	else :
		transaction = get_transaction(id)
	if not transaction :
		transaction = get_closest_transaction(id)
	if not transaction :
		return redirect(url_for('dashboard_route.transactions_tab'))
	transactions = get_transactions(paginated=False)
	index = 0
	for x in range(0, len(transactions)) :
		if transactions[x]['trans_id'] == str(id) :
			index = x
			break
	nxt = None if index <= 0 else index-1
	prev = None if index >= len(transactions)-1 else index+1

	nxt = transactions[nxt]['trans_id'] if nxt else None
	prev = transactions[prev]['trans_id'] if prev else None

	trans_card = render_trans_card(transaction)
	if transaction['size_total_KB'] > 2000 : # > 2MB
		ingress_str = "{0:.2f}".format(transaction['size_total_KB']/1000.0)+" MB"
	else: 
		ingress_str = "{0:.2f}".format(transaction['size_total_KB'])+" KB"

	results = get_results(transaction['trans_id'], page=1, page_size=25)
	page = results.get('page') if results else {}
	res_list = page.get('results', []) if page else []
	result_cards = [render_result_card(r, transaction.get('trans_id', 0)) for r in res_list]

	transaction['finished_at'] = "" if not transaction['finished_at'] else transaction['finished_at']

	return render_template('/dashboard/dashboard_transaction.html',
						   token=session['token'],
						   user=session['user'],
						   email=session['email'],
						   navbar=navbar,
						   transaction=transaction,
						   trans_id = id,
						   results = results,
						   trans_card = trans_card,
						   result_cards = result_cards,
						   ingress_str=ingress_str,
						   prev=prev, nxt=nxt,
						   sidebar=sidebar)


@dashboard_route.route('/dashboard/results/<int:id>', methods=['GET'])
def results_tab(id):
	error = None
	if not session.get('token') or not session.get('user') :
		return redirect(url_for('users_route.login_page', _external=True))
	navbar = get_dashboard_navbar()
	sidebar = get_sidebar()
	transaction = get_transaction(id)
	if not transaction :
		abort(404)
	results = get_results(id, page=1, page_size=25)
	return render_template('/dashboard/dashboard_result.html',
						   token=session['token'],
						   user=session['user'],
						   email=session['email'],
						   navbar=navbar,
						   results=results,
						   trans_id=id,
						   transaction=transaction,
						   sidebar=sidebar)


@dashboard_route.route('/dashboard/services', methods=['GET'])
def services_tab():
	error = None
	if not session.get('token') or not session.get('user') :
		return redirect(url_for('users_route.login_page', _external=True))
	navbar = get_dashboard_navbar()
	sidebar = get_sidebar()
	return render_template('/dashboard/services.html',
						   token=session['token'],
						   user=session['user'],
						   email=session['email'],
						   navbar=navbar,
						   sidebar=sidebar)


def get_closest_transaction(trans_id) :
	transactions = get_transactions(paginated=False)
	
	return get_closest_helper(transactions)

def get_closest_helper(transactions) :
	if not transactions : return {}
	size = len(transactions)
	if size == 1 : return transactions[0]
	mid = size/2
	tid = transactions[mid]['trans_id']
	if int(tid) == trans_id :
		return get_transaction(trans_id)
	elif int(tid) > trans_id :
		return get_closest_helper(transactions[mid:])
	else :
		return get_closest_helper(transactions[:mid])


def get_transaction(trans_id) :
	token = session.get('token', None)
	user_id = session.get('user_id', None)
	if not token or not user_id :
		return []

	payload = {'token' : token}
	headers = {'content-type': 'application/json'}

	r = requests.get(TRANSACTIONS_ROUTE+str(trans_id), data=json.dumps(payload), headers=headers)

	response = json.loads(r.text)

	if not response or not response.get('code') == 200 or not response.get('transaction',None) :
		return []

	transaction = response.get('transaction')

	return transaction

	

def get_transactions(paginated=True, page=1, page_size=15, model=None, service=None, reverse_sort=True) :
	token = session.get('token', None)
	user_id = session.get('user_id', None)
	if not token or not user_id :
		return []

	payload = {'token' : token, 'reverse_sort' : reverse_sort, 'pagination' : paginated, 'user_id' : user_id,
			   'page' : page, 'page_size' : page_size}
	if model :
		payload['model'] = model
	if service :
		payload['service'] = service
	headers = {'content-type': 'application/json'}

	r = requests.get(TRANSACTIONS_ROUTE, data=json.dumps(payload), headers=headers)

	response = json.loads(r.text)

	if not response or not response.get('code') == 200 or not (response.get('transactions',None) or response.get('page', None)) :
		return []

	if paginated :
		transactions = response.get('page')['transactions']
	else :
		transactions = response.get('transactions')

	# return reversed(transactions)

	if paginated :
		next_page = get_params_from_url(url=response.get('next_page')).get('page', [None])[0]
		prev_page = get_params_from_url(url=response.get('prev_page')).get('page', [None])[0]
		first_page = get_params_from_url(url=response.get('first_page')).get('page', [None])[0]
		last_page = get_params_from_url(url=response.get('last_page')).get('page', [None])[0]
		return { 'transactions' : transactions, 'page' : page, 'next_page' : next_page, 'prev_page' : prev_page,
				 'first_page' : first_page, 'last_page' : last_page }
	else :
		return transactions
	

def get_results(trans_id, paginated=True, page=1, page_size=15, model=None, service=None) :
	token = session.get('token', None)
	user_id = session.get('user_id', None)
	if not token or not user_id :
		return []

	payload = {'token' : token, 'pagination' : paginated, 'user_id' : user_id,
			   'page' : page, 'page_size' : page_size}
	if model :
		payload['model'] = model
	if service :
		payload['service'] = service
	headers = {'content-type': 'application/json'}

	r = requests.get(RESULTS_ROUTE+str(trans_id), data=json.dumps(payload), headers=headers)

	response = json.loads(r.text)

	print("Results Response ID %s"%str(trans_id)+"\n\n")
	print(json.dumps(response))
	print("\n\n\n")

	if not response or not response.get('code') == 200 :
		return []

	if paginated :
		page = response.get('page', None)
		if page :
			results  = page.get('results', [])
			results = reversed(results)
			response['results'] = results
	else :
		results = response.get('results', [])
		results = reversed(results)
		response['results'] = results

	return response


def render_trans_card(trans) :
	try :
		return render_template('dashboard/trans_card.html', user=session.get('user', None), transaction=trans)
	except :
		return ""


def render_result_card(result, tid) :
	try :
		return render_template('dashboard/result_card.html', user=session.get('user', None), result=result, trans_id=tid)
	except :
		return ""

# @info - takes a url like api.praxyk.com/transactions?page=3&page_size=12 and returns
#		 {'page' : 3, 'page_size' : 12}
def get_params_from_url(url) :
	query_raw = urlparse(url).query
	query_dict = parse_qs(query_raw)
	return query_dict

