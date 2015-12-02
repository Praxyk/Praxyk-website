from flask import Flask, session, redirect, url_for, escape, request, render_template
import requests
import json
from app import app
from app import *
from app.util.defines import *
from app.routes import *


def get_home_navbar() :
    return render_template('navbar.html', user=session.get('user', None))

def get_dashboard_navbar() :
    return render_template('dashboard/dashboard_navbar.html', user=session.get('user', None))

def get_sidebar(active=None) :
    return render_template('sidebar.html', user=session.get('user', None), active=active)

def redirect_register(success=None, failed=None) :
    return render_template('register.html', tab='register', navbar=get_home_navbar(), success=success, failed=failed)

def redirect_login(success=None, failed=None) :
    return render_template('register.html', tab='login', navbar=get_home_navbar(), success=success, failed=failed)

def login(email, pw) :

    payload = {'email' : email, 'password' : pw}
    headers = {'content-type': 'application/json'}
    r = requests.post(LOGIN_ROUTE, data=json.dumps(payload), headers=headers)
    print( r )
    
    if not check_return(r) :
        return None

    response = json.loads(r.text)
    
    if not response or not response['code'] == 200 or not response.get('token', None) :
        return None

    session['token'] = response['token']
    session['user'] = response['user']['name']
    session['email'] = response['user']['email']
    session['user_id'] = response['user']['user_id']

    return response 



# @info - looks at the raw response and prints relevant error messages if necessary
def check_return(r) :
    if not r or not r.text :
        if "404" in r.text :
            sys.stderr.write("Content Not Found. Double check all content-IDs are correct (username, instance id, etc).\n")
        elif "401" in r.text :
            sys.stderr.write("Request Could not be Authorized. If you haven't logged in today, do so. If error persists, contact John.\n")
        elif "500" in r.text :
            sys.stderr.write("The Server had a Hiccup, do you mind forwarding this stack trace to John?\n")
            sys.stderr.write(str(80*'-'+'\n'+r.text+80*'-'+'\n'))
        else :
            sys.stderr.write("Request Could not be Fufilled.\nDetails : %s\n"%r.text)
        return False
    else :
        return True
