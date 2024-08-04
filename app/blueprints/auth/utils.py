import jwt

from datetime import datetime
from datetime import timedelta

from config import Config
from app import db

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
        "access_token": jwt.encode(access_obj, Config.JWT_SECRET),
        "refresh_token": jwt.encode(refresh_obj, Config.JWT_SECRET),
    }

def regen_tokens(refresh_token):
    try:
        refresh_obj = jwt.decode(refresh_token, Config.JWT_SECRET, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return {"success": False, "message": "refresh token expired"}
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
        return {"success": False, "message": "access token expired"}
    except Exception as e:
        return {"success": False, "message": str(e)}
    return {"success": True, "obj": decoded}