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

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)

    @app.route("/")
    def index():
        if 'user'not in session:
            return render_template("index.html")
        posts = db.get_followed_content(session['user']['_id'])
        posts.extend(db.random_posts())
        for post_ in posts:
            post_["liked"] = session['user']['_id'] in post_['likes']
        return render_template("home.html", user=session['user'], posts = posts)


    @app.route("/new", methods=["GET", "POST"])
    def new():
        if 'user' not in session:
            return redirect(url_for(index))
        
        error = request.args.get("error")

        if request.method == "GET":
            return render_template("new.html", error=error)
        
        image   = request.files.get("image")
        caption = request.form.get("caption")
        tags    = [i.strip() for i in request.form.get("tags").split(",") if i.strip() != ""]

        print(dict(request.form))

        if image is None or caption.strip() == "":
            return redirect("/new?error=No image/caption provided")
        
        post = db.create_post(session['user']['_id'], caption, image, tags)

        return redirect(f"/post/{post['_id']}")

    @app.route("/post/<post_id>")
    def post(post_id):
        post = db.get_posts(post_id)
        if len(post) == 0:
            return redirect("/")
        post = post[0]
        is_json = request.args.get("json")
        user = db.fetch_user("_id", post['user'])
        if 'user' in session:
            liked = session['user']['_id'] in post['likes']
        else:
            liked = False
        if is_json:
            return jsonify({"post": post, "user": user, "liked": liked})
        return render_template("post.html", post=post, user=user, liked=liked)

    @app.route("/comment", methods=["POST"])
    def comment():
        if 'user' not in session:
            return "False"
        post = request.args.get("post")
        comment = request.args.get("comment")
        res = db.add_comment(session['user']['_id'], post, comment)
        if res:
            return "True"
        return "False"

    @app.route("/like", methods=["POST"])
    def like():
        if 'user' not in session:
            return "False"
        post = request.args.get("post")
        res = db.toggle_like(session['user']['_id'], post)
        if res:
            return "True"
        return "False"

    @app.route("/random")
    def random_posts():
        return jsonify(db.random_posts())
        
    return app