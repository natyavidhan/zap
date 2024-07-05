from pymongo import MongoClient
from supabase import create_client, Client
from dotenv import load_dotenv

import os
from uuid import uuid4
from datetime import datetime
import random
load_dotenv()

class Database:
    def __init__(self):
        self.db = MongoClient(os.environ.get("MONGO_URL"))['zap']

        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_KEY")
        print(url, key)
        self.supabase: Client = create_client(url, key)

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
            "username": email.split("@")[0] + "".join([str(random.randint(0,9)) for _ in range(5)]),
            "bio": "",
            "created": datetime.now().timestamp(),
            "posts": [],
            "history": [],
            "followers": [],
            "following": []
        }   
        self.users.insert_one(user_obj)
        return user_obj
    
    def edit_profile(self, email, username, name, bio):
        self.users.update({"email": email}, {"$set": {"username": username, "name": name, "bio": bio}})

    def upload_file(self, location, file, content_type):
        return self.supabase.storage.from_("Zap")\
            .upload(file=file, 
                    path=location, 
                    file_options={"content-type": content_type})
# https://okzqzfyhfttiypjfmolk.supabase.co/storage/v1/object/public/