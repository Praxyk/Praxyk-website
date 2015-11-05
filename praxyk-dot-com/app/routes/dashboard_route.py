from flask import Flask, session, redirect, url_for, escape, request, render_template
import requests
import json
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

cost_per_KB = 0.005

dashboard_route = Blueprint('dashboard_route', __name__,
                                template_folder='templates/dashboard')


@dashboard_route.route('/dashboard', methods=['GET'])
def dashboard():
    error = None
    if not session.get('token') or not session.get('user') :
        return redirect(url_for('users_route.login_page', _external=True))
    navbar = get_dashboard_navbar()
    sidebar = get_sidebar()
    transactions = get_transactions(paginated=False)
    num_transactions = len(transactions)
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
    state_names = ['active', 'finished', 'failed']
    state_counts = [len([x for x in transactions if x['status'] == state]) for state in state_names]

    print(transactions[0]['created_at'])
    dates = list(set([x['created_at'].split("T")[0] for x in transactions]))
    dates.sort()
    date_map = { dates[x]:x for x in range(0, len(dates)) }
    date_counts = []
    for x in dates :
        date_counts.append(0)
    for x in transactions :
        date_counts[date_map[x['created_at'].split("T")[0]]] += 1
    
    print(date_counts)
    print(dates)

    dates2 = list(set([dateutil.parser.parse(x['created_at'].split("T")[0]) for x in transactions]))
    dates2.sort()
    print(dates2)

    dates3 = []
    for x in range((dt.datetime.now()-dates2[0]).days):
        dates3.append(dates2[0]+timedelta(days=x)) 
    print(dates3)

    return render_template('/dashboard/dashboard_home.html',
                           token=session['token'],
                           user=session['user'],
                           email=session['email'],
                           navbar=navbar,
                           transactions=transactions[-10:],
                           all_transactions=transactions,
                           num_transactions=num_transactions,
                           command_counts=command_counts,
                           total_ingress=total_ingress,
                           ingress_str=ingress_str,
                           cost_total=cost,
                           state_counts=state_counts,
                           state_names=state_names,
                           dates = dates,
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
    navbar = get_dashboard_navbar()
    sidebar = get_sidebar()
    transactions = get_transactions(paginated=False)
    num_transactions = len(transactions)
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
    state_names = ['active', 'finished', 'failed']
    state_counts = [len([x for x in transactions if x['status'] == state]) for state in state_names]

    dates = list(set([x['created_at'].split("T")[0] for x in transactions]))
    dates.sort()
    date_map = { dates[x]:x for x in range(0, len(dates)) }
    date_counts = []
    for x in dates :
        date_counts.append(0)
    for x in transactions :
        date_counts[date_map[x['created_at'].split("T")[0]]] += 1
    
    return render_template('/dashboard/dashboard_transactions.html',
                           token=session['token'],
                           user=session['user'],
                           email=session['email'],
                           navbar=navbar,
                           transactions=transactions[-10:],
                           all_transactions=transactions,
                           num_transactions=num_transactions,
                           command_counts=command_counts,
                           total_ingress=total_ingress,
                           ingress_str=ingress_str,
                           cost_total=cost,
                           state_counts=state_counts,
                           state_names=state_names,
                           dates = dates,
                           date_counts = date_counts,
                           sidebar=sidebar)




    error = None
    if not session.get('token') or not session.get('user') :
        return redirect(url_for('users_route.login_page', _external=True))
    navbar = get_dashboard_navbar()
    sidebar = get_sidebar()
    transactions = get_transactions(page=1, page_size=25)
    return render_template('/dashboard/dashboard_transactions.html',
                           token=session['token'],
                           user=session['user'],
                           email=session['email'],
                           navbar=navbar,
                           transactions=transactions,
                           sidebar=sidebar)


@dashboard_route.route('/dashboard/transaction/<int:id>', methods=['GET'])
def transaction_tab(id):
    error = None
    if not session.get('token') or not session.get('user') :
        return redirect(url_for('users_route.login_page', _external=True))
    navbar = get_dashboard_navbar()
    sidebar = get_sidebar()
    transaction = get_transaction(id)
    if transaction['size_total_KB'] > 2000 : # > 2MB
        ingress_str = "{0:.2f}".format(transaction['size_total_KB']/1000.0)+" MB"
    else: 
        ingress_str = "{0:.2f}".format(transaction['size_total_KB'])+" KB"
    return render_template('/dashboard/dashboard_transaction.html',
                           token=session['token'],
                           user=session['user'],
                           email=session['email'],
                           navbar=navbar,
                           transaction=transaction,
                           ingress_str=ingress_str,
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

    

def get_transactions(paginated=True, page=1, page_size=15, model=None, service=None) :
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

    r = requests.get(TRANSACTIONS_ROUTE, data=json.dumps(payload), headers=headers)

    response = json.loads(r.text)

    if not response or not response.get('code') == 200 or not (response.get('transactions',None) or response.get('page', None)) :
        return []

    if paginated :
        transactions = response.get('page')['transactions']
    else :
        transactions = response.get('transactions')

    # return reversed(transactions)
    return transactions[::-1]

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

    if not response or not response.get('code') == 200 or not (response.get('transactions',None) or response.get('page', None)) :
        return []

    if paginated :
        results  = response.get('page')['results']
        results = reversed(results)
        response['results'] = results
    else :
        results = response.get('results')
        results = reversed(results)
        response['results'] = results

    return response
