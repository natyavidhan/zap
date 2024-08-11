from flask import Flask, render_template, session, url_for, redirect, request, jsonify
from authlib.integrations.flask_client import OAuth

from database import Database
from config import Config

db = Database()
oauth = OAuth()

def create_app():
    app = Flask(__name__, template_folder="templates")
    app.config.from_object(Config)
    oauth.init_app(app)

    from blueprints.auth import bp as auth_bp
    from blueprints.user import bp as user_bp
    from blueprints.post import bp as post_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(post_bp)

    from blueprints import utils

    @app.route("/")
    def index():
        if 'user'not in session:
            return render_template("index.html")

        session_obj = utils.get_current_user()
        if session_obj is False:
            return redirect(url_for("index"))
        print(session_obj)
        posts = db.get_followed_content(session_obj['_id'])
        posts.extend(db.random_posts())
        for post_ in posts:
            post_["liked"] = session_obj['_id'] in post_['likes']
        return render_template("home.html", user=session_obj, posts = posts)
    return app
    
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)