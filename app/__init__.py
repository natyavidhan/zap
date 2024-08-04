from flask import Flask, render_template, session, url_for, redirect, request, jsonify
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv

import os

from app.database import Database

load_dotenv()

db = Database()
oauth = OAuth()


def create_app():
    app = Flask(__name__, template_folder="templates")
    app.config.from_mapping(dict(os.environ))
    oauth.init_app(app)

    from app.blueprints.auth import bp as auth_bp
    from app.blueprints.user import bp as user_bp
    from app.blueprints.post import bp as post_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(post_bp)

    @app.route("/")
    def index():
        if 'user'not in session:
            return render_template("index.html")
        posts = db.get_followed_content(session['user']['_id'])
        posts.extend(db.random_posts())
        for post_ in posts:
            post_["liked"] = session['user']['_id'] in post_['likes']
        return render_template("home.html", user=session['user'], posts = posts)
        
    return app