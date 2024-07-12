import supabase
from dotenv import load_dotenv
import requests

import os
from uuid import uuid4
from io import BytesIO
import random

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = supabase.create_client(url, key)

users = supabase.table("zap_users")
posts_ = supabase.table("zap_posts")

tags_ = [
    "#CutePets",
    "#PetLovers",
    "#PetsOfInstagram",
    "#PetPhotography",
    "#FurryFriends",
    "#AnimalLovers",
    "#Instapets",
    "#PetGoals",
    "#FurBabies",
    "#BestFriends",
    "#PetCuteness",
    "#Pawsome",
    "#Fluffy",
    "#PetSnuggles"
]

def create_user():
    data = requests.get("https://randomuser.me/api/").json()['results'][0]
    user_obj = {
        "_id": str(uuid4()),
        "name": f"{data['name']['first']} {data['name']['last']}",
        "email": data['email'],
        "username": data['login']['username'],
        "bio": f"My name is {data['name']['title']} {data['name']['first']} {data['name']['last']}, I live in {data['location']['street']['name']} street, {data['location']['city']}, {data['location']['state']}, {data['location']['postcode']}, {data['location']['country']}",
        "posts": [],
        "history": [],
        "followers": [],
        "following": []
    }   
    users.insert(user_obj).execute()
    return user_obj

def upload_file(location, file, content_type):
    key =  supabase.storage.from_("Zap")\
            .upload(file=file, 
                path=location, 
                file_options={"content-type": content_type}).json()['Key']
    return f"{os.environ.get('SUPABASE_URL')}/storage/v1/object/public/{key}"

def create_post(user):
    post_id = str(uuid4())
    caption = str(uuid4())
    count =  random.randint(1, 200)
    img = requests.get(f"https://cataas.com/cat").content
    tags = random.sample(tags_, 4)
    mime = "image/jpg"
    url = upload_file(f"Posts/{post_id}.{mime.split('/')[1]}", img, mime)

    post = {
        "_id": post_id,
        "caption": caption,
        "img_url": url,
        "user": user,
        "likes": [],
        "comments": [],
        "tags": tags
    }

    posts_.insert(post).execute()

    posts = users.select("posts").eq("_id", user).execute().model_dump()['data'][0]['posts']
    posts.append(post_id)
    users.update({"posts": posts}).eq("_id", user).execute()

for i in range(10):
    usr = create_user()
    for j in range(10):
        create_post(usr['_id'])