from flask import session, request, redirect, render_template, url_for, jsonify

from app import db
from app.blueprints.post import bp
from app.blueprints.auth import utils

@bp.route("/new", methods=["GET", "POST"])
def new():
    if 'user' not in session:
        return redirect(url_for('index'))
    
    error = request.args.get("error")

    if request.method == "GET":
        return render_template("new.html", error=error)

    session_obj = utils.get_current_user()
    if session_obj is False:
        return "False"
    
    image   = request.files.get("image")
    caption = request.form.get("caption")
    tags    = [i.strip() for i in request.form.get("tags").split(",") if i.strip() != ""]

    if image is None or caption.strip() == "":
        return redirect("/new?error=No image/caption provided")
    
    post = db.create_post(session_obj['_id'], caption, image, tags)

    return redirect(f"/post/{post['_id']}")

@bp.route("/<post_id>")
def post(post_id):
    post = db.get_posts(post_id)
    if len(post) == 0:
        return redirect("/")
    post = post[0]
    is_json = request.args.get("json")
    user = db.fetch_user("_id", post['user'])
    if 'user' in session:
        session_obj = utils.get_current_user()
        if session_obj is False:
            liked = False
        else:
            liked = session_obj['_id'] in post['likes']
    else:
        liked = False
    if is_json:
        return jsonify({"post": post, "user": user, "liked": liked})
    return render_template("post.html", post=post, user=user, liked=liked)

@bp.route("/comment", methods=["POST"])
def comment():
    if 'user' not in session:
        return "False"
    
    session_obj = utils.get_current_user()
    if session_obj is False:
        return "False"

    post = request.args.get("post")
    comment = request.args.get("comment")
    res = db.add_comment(session_obj['_id'], post, comment)
    if res:
        return "True"
    return "False"

@bp.route("/like", methods=["POST"])
def like():
    if 'user' not in session:
        return "False"
    
    session_obj = utils.get_current_user()
    if session_obj is False:
        return "False"

    post = request.args.get("post")
    res = db.toggle_like(session_obj['_id'], post)
    if res:
        return "True"
    return "False"

@bp.route("/random")
def random_posts():
    return jsonify(db.random_posts())