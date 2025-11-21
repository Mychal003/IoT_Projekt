from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask_cors import CORS



load_dotenv()

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 

    CORS(app)

    db.init_app(app)

    from app.routes import api_bp

    app.register_blueprint(api_bp, url_prefix='/api')

    with app.app_context():
        db.create_all()

    return app