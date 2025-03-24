from flask import Flask, render_template, request, redirect, url_for

from routes import main
from database import db
from models import *

def create_app():
    # create sqlite db file
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///FitTracker.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    app.register_blueprint(main)

    return app

# create app
app = create_app()

with app.app_context():
    db.create_all()

# run app in debug
if __name__ == "__main__":
    app.run(debug=True)