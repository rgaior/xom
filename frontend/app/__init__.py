import dash
from flask import Flask
from flask.helpers import get_root_path
from flask_login import login_required

from config import BaseConfig


def create_app():
    server = Flask(__name__)
    server.config.from_object(BaseConfig)
    
    register_extensions(server)
    register_blueprints(server)

#     from app.dashapp1.layout import layout as layout1
# #    from app.dashapp1.callbacks import register_callbacks as register_callbacks1
#     from app.dashapp1.layout import register_callbacks as register_callbacks1
#     register_dashapp(server, 'app1', 'dash/app1', layout1, register_callbacks1)

#     from app.dashapp2.layout import layout as layout2
#     from app.dashapp2.layout import register_callbacks as register_callbacks2
# #    from app.dashapp2.callbacks import register_callbacks as register_callbacks2
#     register_dashapp(server, 'app2', 'dash/app2', layout2, register_callbacks2)

    from app.dashapp3.layout import layout as layout3
    from app.dashapp3.layout import register_callbacks as register_callbacks3
    register_dashapp(server, 'app3', 'dash/app3', layout3, register_callbacks3)

    # from app.dashapp4.layout import layout as layout4
    # from app.dashapp4.layout import register_callbacks as register_callbacks4
    # register_dashapp(server, 'app4', 'dash/app4', layout4, register_callbacks4)

    from app.dashapp5.layout import layout as layout5
    from app.dashapp5.layout import register_callbacks as register_callbacks5
    register_dashapp(server, 'app5', 'dash/app5', layout5, register_callbacks5)

    from app.dashapp6.layout import layout as layout6
    from app.dashapp6.layout import register_callbacks as register_callbacks6
    register_dashapp(server, 'app6', 'dash/app6', layout6, register_callbacks6)


    return server


def register_dashapp(app, title, base_pathname, layout, register_callbacks_fun):
    # Meta tags for viewport responsiveness
    meta_viewport = {"name": "viewport", "content": "width=device-width, initial-scale=1, shrink-to-fit=no"}
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    my_dashapp = dash.Dash(__name__,
                           server=app,
                           url_base_pathname=f'/{base_pathname}/',
                           assets_folder=get_root_path(__name__) + f'/assets/',
#                           assets_folder=f'/assets/',
                           meta_tags=[meta_viewport],external_stylesheets=external_stylesheets)

    with app.app_context():
        my_dashapp.title = title
        my_dashapp.layout = layout
        register_callbacks_fun(my_dashapp)
    _protect_dashviews(my_dashapp)


def _protect_dashviews(dashapp):
    for view_func in dashapp.server.view_functions:
        if view_func.startswith(dashapp.config.url_base_pathname):
            dashapp.server.view_functions[view_func] = login_required(dashapp.server.view_functions[view_func])


def register_extensions(server):
    from app.extensions import mongo
    from app.extensions import db
    from app.extensions import login
    from app.extensions import migrate
    from app.extensions import ldap

    db.init_app(server)
    login.init_app(server)
    login.login_view = 'main.login'
    migrate.init_app(server, db)
    mongo.init_app(server)
    ldap.init_app(server)

def register_blueprints(server):
    from app.webapp import server_bp
    from app.webapp import main_bp

    server.register_blueprint(server_bp)
    server.register_blueprint(main_bp)
