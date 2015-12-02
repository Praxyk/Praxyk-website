from flask import Flask, session, redirect, url_for, escape, request, render_template
from app import app
import requests
import json
from app import *
from app.util.defines import *
from app.routes import *
from app.routes.common import *
from app.routes.user_route import *
from app.routes.dashboard_route import *

app.register_blueprint(users_route)
app.register_blueprint(dashboard_route)


@app.route('/')
@app.route('/index')
def index():
    navbar = get_home_navbar()
    user = {}
    if session.get('token', None) and session.get('user', None) :
        user = {'name' : session['user'], 'email' : session['email'], 'token' : True}
    return render_template('index.html', navbar=navbar, user=user)


@app.route('/documentation')
def documentation():
    navbar = get_home_navbar()
    user = {}
    if session.get('token', None) and session.get('user', None) :
        user = {'name' : session['user'], 'email' : session['email']}
    with open('app/templates/praxyk-wiki-html/Praxyk-API.html', 'r') as fh:
        page= fh.read()
    return render_template('documentation.html', navbar=navbar, user=user, page=page)


@app.route('/documentation/<string:name>')
def documentation_api(name):
    navbar = get_home_navbar()
    user = {}
    if session.get('token', None) and session.get('user', None) :
        user = {'name' : session['user'], 'email' : session['email']}
    with open('app/templates/praxyk-wiki-html/Praxyk-API.html', 'r') as fh:
        page= fh.read()
    return render_template('documentation/documentation_api.html', navbar=navbar, user=user, page=page)


@app.route('/services')
def services():
    navbar = get_home_navbar()
    user = {}
    if session.get('token', None) and session.get('user', None) :
        user = {'name' : session['user'], 'email' : session['email']}
    return render_template('services.html', navbar=navbar, user=user)
