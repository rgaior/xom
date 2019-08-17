from flask import make_response, send_file, Response, Markup, jsonify, render_template, flash, redirect, Response, request, session, abort, url_for
from app import app
from app.forms import LoginForm
from pymongo import MongoClient
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from bson.json_util import dumps, loads
from io import StringIO, BytesIO
from datetime import date, timedelta, datetime
from dateutil.parser import parse
import numpy as np
from flask import Flask, render_template, request
import pandas as pd

client = MongoClient()
login_manager = LoginManager()

class User(UserMixin):
    def __init__(self, id):
        self.id = id
        self.name = "user" + str(id)
        self.password = self.name + "_secret"

    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.password)


users = [User(id) for id in range(1, 21)]

db = client.test1
collection = db.inventory

person = {'username' : ''}

login_manager.init_app(app)
login_manager.login_view = "login"

obs_start = parse("2012-01-19 17:21:00")
obs_end = parse("2019-01-19 17:21:00")
view_data = 'all'
data_type = 'light_yield'
source = 'Kr'
################################
## my test #####################
from bokeh.embed import server_document
from bokeh.server.server import Server
from bokeh.themes import Theme
from tornado.ioloop import IOLoop

from bokeh.sampledata.sea_surface_temperature import sea_surface_temperature
import sys
import os
cwd = os.getcwd()
sys.path.append(cwd)
from app.implot import plot

# Index page
@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    if (request.method == 'GET'):
        obs_date_submit = request.args.get('obs_date_submit')
        if (obs_date_submit == 'Submit'):
            obs_start_read = request.args.get('obs_start')
            global obs_start
            obs_start = parse(obs_start_read)
            global obs_end
            obs_end_read = request.args.get('obs_end')
            obs_end = parse(obs_end_read)
            print(obs_start, obs_end)



    username = "{}".format(person["username"])
    entry = collection.find({"processes" : f"{username}"}, {"_id" : False})
    return render_template('index.html', title='Home', entry = entry, user = person)



from bokeh.embed import server_document
from bokeh.server.server import Server
#from bokeh.themes import Theme


# bokeh test page with fake data
from threading import Thread, Lock

# @app.route('/bokeh', methods=['GET'])
# def bkapp_page():
#     script = server_document('http://localhost:5006/bkapp')
#     return render_template("embed.html", script=script, template="Flask")

# @app.route('/bokeh2', methods=['GET'])
# def bkapp_page2():
#     script = server_document('http://localhost:5006/bkapp2')
#     return render_template("embed.html", script=script, template="Flask")

@app.route('/implot', methods=['GET'])
@login_required
def bkapp_implot():
    script = server_document('http://localhost:5006/implot')
    return render_template("embed.html", script=script, template="Flask")


def bk_worker():
    # Can't pass num_procs > 1 in this configuration. If you need to run multiple
    # processes, see e.g. flask_gunicorn_embed.py
#    server = Server({'/bkapp': modify_doc,'/bkapp2': modify_doc2,'/implot': plot}, io_loop=IOLoop(), allow_websocket_origin=["localhost:5000","127.0.0.1:5000"])
    server = Server({'/implot': plot}, io_loop=IOLoop(), allow_websocket_origin=["localhost:5000","127.0.0.1:5000"])
    server.start()
    server.io_loop.start()

Thread(target=bk_worker).start()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if password == username + "_secret":
            id = username.split('user')[1]
            user = User(id)
            login_user(user)
            person['username'] = User(id).name
            return redirect(url_for('index', user=person))
        else:
            return abort(401)
    else:
        form = LoginForm()
        return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    person['username'] = ''
    return render_template('index.html', user=person)


@app.errorhandler(401)
def page_not_found(e):
    form = LoginForm()
    return render_template('login.html', title='Sign In', form=form)


# callback to reload the user object
@login_manager.user_loader
def load_user(userid):
    return User(userid)


@app.route('/download')
def download():

    electron = dumps(collection.find({"names" : "light_yield"}, {"_id" : False}))
    electron = loads(electron)
    electron_lifetime_data = []
    electron_csv = []
    for entry in electron:
        electron_lifetime_data.append(entry)
        electron_csv.append("%s, %s\n" %(entry["values"][0], entry["time"]))


    csvElString = ''.join(electron_csv)

    output = BytesIO()
    output.write(csvElString.encode('utf-8'))
    output.seek(0)

    return send_file(output, mimetype='text/csv', attachment_filename='testEL', as_attachment=True)

#app.run(port=5000, debug=True)
#app.run(host="0.0.0.0", port=5000, threaded=True)
