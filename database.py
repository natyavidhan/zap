from pymongo import MongoClient

import os
from uuid import uuid4
from datetime import datetime

class Database:
    def __init__(self):
        self.db = MongoClient(os.environ.get("MONGO_URL"))['zap']

        self.users = self.db.users
        self.posts = self.db.posts
        
    def fetch_user(self, key, value):
        return self.users.find_one({key: value})

    def create_user(self, email, name):
        if self.fetch_user("email", email) is not None:
            return False
        user_obj = {
            "_id": str(uuid4()),
            "name": name,
            "email": email,
            "bio": "",
            "created": datetime.now().timestamp(),
            "posts": [],
            "history": [],
            "followers": [],
            "following": []
        }   
        self.users.insert_one(user_obj)
        return user_obj
    