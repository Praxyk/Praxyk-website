
import sys, os
import argparse
import datetime
import json

from flask import Flask, jsonify, request, Response, g, abort, make_response, render_template, url_for
from flask.ext.restful import Api, Resource, reqparse, fields, marshal, marshal_with
from flask import Flask, session, redirect, url_for, escape, request, render_template

from app import app
from app import *
from app.util.defines import *
from app.routes.common import *
from app.routes import *
from app.routes.dashboard_route import *

from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound


users_route = Blueprint('users_route', __name__,
                                template_folder='templates')

@users_route.route('/tokens', methods=['GET', 'POST'])
def authenticate():
    error = None
    email = request.form['email']
    pw = request.form['password']
    if request.method == 'POST':
        login_success = login(email, pw)
        if login_success :
            return redirect(url_for('dashboard_route.dashboard'))
        
    return redirect_login(failed=True)


@users_route.route('/login', methods=['GET', 'POST'])
def login_page():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        pw = request.form['password']
        login_success = login(email, pw)
        if login_success :
            return redirect(url_for('dashboard_route.dashboard'))
        
    if session.get('token', None) and session.get('user_id', None) :
        if get_user(session['token'], session['user_id']) :
            return redirect(url_for('dashboard_route.dashboard'))

    return redirect_login()


# route for handling the login page logic
@users_route.route('/logout', methods=['GET', 'POST'])
def logout():
    error = None
    session['user'] = None
    session['token'] = None
    session['email'] = None
    return redirect(url_for('index'))

# route for handling the login page logic
@users_route.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        pw = request.form['password']
        
        if register_new_user(name, email, pw) :
            print("We registered the user")
            return redirect_register(success=True)
        else :
            return redirect_register(failed=True)

    return redirect_register()


def get_user(token, user_id) :
    payload = {'token' : token, 'user_id' : user_id}
    headers = {'content-type': 'application/json'}
    r = requests.get(USERS_ROUTE+str(user_id), data=json.dumps(payload), headers=headers)
    print( r )
    
    if not check_return(r) :
        return None

    response = json.loads(r.text)
    print(response)
    
    if not response or not response['code'] == 200 or not response.get('user', None) :
        return None

    session['user'] = response['user']['name']
    session['email'] = response['user']['email']
    session['user_id'] = response['user']['user_id']

    return response 


def register_new_user(name, email, pw) :
    payload = {'name' : name, 'email' : email, 'password' : pw}
    headers = {'content-type': 'application/json'}

    r = requests.post(USERS_ROUTE, data=json.dumps(payload), headers=headers)
    print( r )
    
    if not check_return(r) :
        return None

    response = json.loads(r.text)
    
    if not response or not response.get('code') == 200 or not response.get('user') :
        return None

    session['user'] = response['user']['name']
    session['email'] = response['user']['email']

    return response 
