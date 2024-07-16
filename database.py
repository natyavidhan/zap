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
        if len(res) == 0:
            return None
        return res[0]

    def create_user(self, email, name):
        if self.fetch_user("email", email) is not None:
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
        self.users.update({"username": username, "name": name, "bio": bio}).eq("email", email).execute()

    def upload_file(self, location, file, content_type):
        key =  self.supabase.storage.from_("Zap")\
            .upload(file=file, 
                    path=location, 
                    file_options={"content-type": content_type}).json()['Key']
        return f"{os.environ.get('SUPABASE_URL')}/storage/v1/object/public/{key}"

    def create_post(self, user, caption, img:FileStorage, tags):
        post_id = str(uuid4())
        mime = img.content_type
        url = self.upload_file(f"Posts/{post_id}.{mime.split('/')[1]}", img.read(), mime)

        post = {
            "_id": post_id,
            "caption": caption,
            "img_url": url,
            "user": user,
            "likes": [],
            "comments": [],
            "tags": tags
        }

        self.posts.insert(post).execute()

        posts = self.users.select("posts").eq("_id", user).execute().model_dump()['data'][0]['posts']
        posts.append(post_id)
        self.users.update({"posts": posts}).eq("_id", user).execute()

        return post
    
    def get_posts(self, *post_ids):
        post = self.posts.select("*").in_("_id", post_ids).execute().model_dump()['data']
        if len(post_ids) == 1:
            return post[0]
        return post
    
    def add_comment(self, user_id, post_id, comment):
        user = self.fetch_user("_id", user_id)
        post = self.get_posts(post_id)
        if user is None or len(post) == 0 or comment.strip() == "":
            return False
        post['comments'].append({"userid": user_id, "username": user['name'], "comment": comment, "on": datetime.now().timestamp()})

        self.posts.update({"comments": post['comments']}).eq("_id", post_id).execute()
        return True
    
    def toggle_like(self, user_id, post_id):
        user = self.fetch_user("_id", user_id)
        post = self.get_posts(post_id)
        if user is None or len(post) == 0:
            return False
        if user_id in post['likes']:
            post['likes'].remove(user_id)
        else:
            post['likes'].append(user_id)
        
        self.posts.update({"likes": post['likes']}).eq("_id", post_id).execute()
        return True
    
    def attach_username(self, posts):
        users = [i['user'] for i in posts]
        user_objs = self.supabase.table("zap_users").select("*").in_("_id", users).execute().model_dump()['data']
        new_posts = []
        for post in posts:
            post['username'] = {i['_id']: i['username'] for i in user_objs}[post['user']]
            new_posts.append(post)
        return new_posts

    def random_posts(self):
        return self.attach_username(self.supabase.table("random_posts").select("*").limit(5).execute().model_dump()['data'])
    
    def toggle_follow(self, follower, following):
        user = self.fetch_user("_id", follower)
        other = self.fetch_user("_id", following)

        if following not in user['following']:
            user['following'].append(following)
            other['followers'].append(follower)
        else:
            user['following'].remove(following)
            other['followers'].remove(follower)

        self.users.update({"following": user['following']}).eq("_id", follower).execute()
        self.users.update({"followers": other['followers']}).eq("_id", following).execute()
        return True
    
    def get_followed_content(self, user_id):
        users = self.fetch_user("_id", user_id)['following']
        return self.attach_username(self.supabase.table("random_posts").select("*").in_("user", users).limit(5).execute().model_dump()['data'])
