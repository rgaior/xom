from flask import make_response, send_file, Response, Markup, jsonify, render_template, flash, redirect, Response, request, session, abort, url_for
from app import app
from app.forms import LoginForm
from pymongo import MongoClient
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from bson.json_util import dumps, loads
from io import StringIO, BytesIO
from datetime import date, timedelta, datetime
from dateutil.parser import parse

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


@app.route('/calib', methods=['GET', 'POST'])
@login_required
def calib():
    global view_data
    global obs_start
    global obs_end
    bad_runs = []
    bad_index_list = request.args.get('bad')
    print(bad_index_list)
    data_type = str(request.args.get('data'))
    source = str(request.args.get('source'))

    new_view_data = str(request.args.get('view'))
    if (new_view_data != 'None'):
         view_data = new_view_data
    elif ((new_view_data == 'None') and (view_data != 'all')):
        view_data = view_data
    else:
        view_data = 'all'


    data_is_present = False
    if data_type != '':
        data_is_present = True

    # print(obs_end)
    # print(obs_start)
    if data_type != 'light_yield':
        light_yield = dumps(collection.find({"%s.names" %(data_type): [ "%s" %(data_type) ]}, {"_id" : False}))

    else:
        light_yield = dumps(collection.find({"names" : [data_type]}, {"_id" : False}))
    light_yield = loads(light_yield)
    ly_data = []
    # print(light_yield)
    count = 0
    for entry in light_yield:
        if data_type == "charge_yield":
            if entry['charge_yield']['values'] > 0:
                if (parse(entry['charge_yield']['time']) >= (obs_start)) and (parse(entry['charge_yield']['time']) <= (obs_end)):
                    ly_data.append(entry)
                    count = count + 1

        else:
            if entry['values'][0] > 0:
                if (parse(entry['time']) >= (obs_start)) and (parse(entry['time']) <= (obs_end)):
                    ly_data.append(entry)
                    count = count + 1

    # print("what is happening", ly_data)
    return render_template('calib.html', title='Calibration Data', user=person, max=8, ly_data=ly_data, data_type=data_type, data_flag=data_is_present, source_type=source, obs_start=obs_start, obs_end=obs_end, view_data=view_data, new_bad_runs=bad_runs)

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

#app.run(host="0.0.0.0", port=5000, threaded=True)
