import jwt
from flask import session

from datetime import datetime
from datetime import timedelta

from config import Config
from main import db

def gen_tokens(user_obj):
    d = datetime.now()
    access_obj = {
        "_id": user_obj['_id'],
        "name": user_obj['name'],
        "email": user_obj['email'],
        'username': user_obj['username'],
        "exp": d+timedelta(days=Config.TOKEN_EXP['access'])
    }

    refresh_obj = {
        "_id": user_obj['_id'],
        "exp": d+timedelta(days=Config.TOKEN_EXP['refresh'])
    }

    return {
        "success": True,
        "access_token": jwt.encode(access_obj, Config.JWT_SECRET),
        "refresh_token": jwt.encode(refresh_obj, Config.JWT_SECRET),
    }

def regen_tokens(refresh_token):
    try:
        refresh_obj = jwt.decode(refresh_token, Config.JWT_SECRET, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return {"success": False, "message": Config.REFRESH_EXPIRE}
    except jwt.DecodeError:
        return {"success": False, "message": "malformed refresh token"}
    except Exception as e:
        return {"success": False, "message": str(e)}
    _id = refresh_obj['_id']
    user = db.fetch_user("_id", _id)

    return gen_tokens(user)

def validate_access_token(access_token):
    try:
        decoded = jwt.decode(access_token, Config.JWT_SECRET, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return {"success": False, "message": Config.ACCESS_EXPIRE}
    except Exception as e:
        return {"success": False, "message": str(e)}
    return {"success": True, "obj": decoded}

def get_current_user():
    if 'user' not in session:
        return False
    user = validate_access_token(session['user']['access_token'])
    if user['success'] == False and user['message'] == Config.ACCESS_EXPIRE:
        new_tokens = regen_tokens(session['user']['refresh_token'])
        if new_tokens['success'] == False:
            session.pop('user')
            return False
        session['user'] = new_tokens
        user = validate_access_token(new_tokens['access_token'])
    return user['obj']