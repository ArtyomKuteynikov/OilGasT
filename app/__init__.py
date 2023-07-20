# init.py
import json
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.swagger import get_apispec
from flask_swagger_ui import get_swaggerui_blueprint
from flask_qrcode import QRcode

SWAGGER_URL = '/docs'
API_URL = '/swagger'

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///DB.sqlite'
    db.init_app(app)
    QRcode(app)

    from .models import User

    @app.route('/swagger')
    def create_swagger_spec():
        return json.dumps(get_apispec(app).to_dict())    # blueprint for auth routes in our app

    swagger_ui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': 'НефтеГазТ'
        }
    )
    app.register_blueprint(swagger_ui_blueprint)

    # blueprint for api
    from .api import auth_api as api_blueprint
    app.register_blueprint(api_blueprint)

    from .offers_api import api as api_blueprint
    app.register_blueprint(api_blueprint)

    from .car_api import api as api_blueprint
    app.register_blueprint(api_blueprint)

    from .wallet_api import api as api_blueprint
    app.register_blueprint(api_blueprint)

    from .map_api import api as api_blueprint
    app.register_blueprint(api_blueprint)

    return app
