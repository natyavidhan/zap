from supabase import create_client, Client

import os
from uuid import uuid4
from datetime import datetime
import random
from werkzeug.datastructures import FileStorage



class Database:
    def __init__(self):
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_KEY")
        self.supabase: Client = create_client(url, key)

        self.users = self.supabase.table("zap_users")
        self.posts = self.supabase.table("zap_posts")
        
    def fetch_user(self, key, value):
        res = self.users.select("*").eq(key, value).execute().model_dump()['data']
        return res

    def create_user(self, email, name):
        if len(self.fetch_user("email", email)) != 0:
            return False
        user_obj = {
            "_id": str(uuid4()),
            "name": name,
            "email": email,
            "username": email.split("@")[0] + "".join([str(random.randint(0,9)) for _ in range(5)]),
            "bio": "",
            "posts": [],
            "history": [],
            "followers": [],
            "following": []
        }   
        self.users.insert(user_obj).execute()
        return user_obj
    
    def edit_profile(self, email, username, name, bio):
        self.users.update({"email": email}, {"$set": {"username": username, "name": name, "bio": bio}})

    def upload_file(self, location, file, content_type):
        key =  self.supabase.storage.from_("Zap")\
            .upload(file=file, 
                    path=location, 
                    file_options={"content-type": content_type}).json()['Key']
        return f"{os.environ.get("SUPABASE_URL")}/storage/v1/object/public/{key}"

    def create_post(self, user, caption, img:FileStorage, tags):
        post_id = str(uuid4())
        mime = img.content_type
        url = self.upload_file(f"Posts/{post_id}.{mime.split("/")[1]}", img.read(), mime)

        post = {
            "_id": post_id,
            "captions": caption,
            "img_url": url,
            "user": user,
            "likes": [],
            "comments": [],
            "tags": tags
        }

        self.posts.insert(post).execute()

        posts = self.users.select("posts").eq("_id", user).execute().model_dump()['data'][0]
        posts.append(post_id)
        self.users.update({"posts": posts}).eq("_id", user).execute()

        return post