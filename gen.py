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
    "CutePets",
    "PetLovers",
    "PetsOfInstagram",
    "PetPhotography",
    "FurryFriends",
    "AnimalLovers",
    "Instapets",
    "PetGoals",
    "FurBabies",
    "BestFriends",
    "PetCuteness",
    "Pawsome",
    "Fluffy",
    "PetSnuggles"
]

captions = [
    "Purrfectly content with my feline friend 🐾",
    "Life is better with a cat by your side 🐱",
    "Pawsitively adorable moments with my kitty 😻",
    "Whiskers and purrs make everything better 🐈",
    "Feline good with this little furball 🐾",
    "Cat naps and cozy cuddles 💤🐱",
    "A house isn't a home without a cat 🏠❤️",
    "Paws and reflect: cats make life purrfect 🐾",
    "Living that cat life 🐱✨",
    "Every cat is a masterpiece 🖼️🐱",
    "Whisker Wednesday 🐱✨",
    "Just another day in paradise with my cat 🌴🐱",
    "Caught in a purrfect moment 🐾",
    "Cats are like potato chips, you can’t have just one 🐱",
    "Fur real though, my cat is the cutest 😻",
    "The more people I meet, the more I love my cat 🐱❤️",
    "Purring into the weekend like... 😺🎉",
    "Cats leave paw prints on your heart 🐾❤️",
    "You had me at meow 🐱💕",
    "Just a girl/boy and her/his cat 🐾",
    "Home is where the cat is 🏡🐱",
    "My therapist has whiskers and a tail 🐈",
    "Adopt a cat, gain a best friend 🐾",
    "Kittens are angels with whiskers 🐱😇",
    "Having a purrfectly good time 🐾",
    "Pawsitive vibes only 🐱✨",
    "Not all heroes wear capes, some have fur 🦸‍♂️🐱",
    "My cat is my best friend and my pillow 😺🛏️",
    "Meow is the time for a catnap 💤",
    "Love me, love my cat 🐱❤️",
    "Catitude: having a cat-like attitude 🐾",
    "Caturday vibes every day 🐱🎉",
    "Happiness is a warm cat 🐱🔥",
    "Whiskers, purrs, and playful pounces 🐾",
    "Live, love, purr 🐱❤️",
    "Cats are the purrfect companions 🐾",
    "Cat hair, don't care 🐱",
    "Fur-tunately, I have a cat 🐱✨",
    "Feline fine today 🐾",
    "Cats make life meowgical 🐱✨",
    "Snuggle time with my furry friend 🐾",
    "Every day is Caturday with my cat 🐱",
    "My cat thinks I'm pawsome 🐾",
    "Purrfection in every whisker 🐱",
    "Cat's out of the bag 🐾",
    "My cat completes me 🐱❤️",
    "In a purrfect world, every home would have a cat 🐾",
    "Napping like a cat 🐱💤",
    "Paws and enjoy the moment 🐾",
    "Cats: because people suck sometimes 🐱",
    "Keep calm and love cats 🐾",
    "Living my best cat life 🐱✨",
    "Crazy cat person? More like dedicated cat lover 🐾",
    "The purrfect companion 🐱❤️",
    "Purrs and whisker kisses 🐾",
    "Fur-iendship goals 🐱✨",
    "My heart belongs to my cat 🐾",
    "Whisker kisses are the best 😽",
    "Cats rule, dogs drool 🐱",
    "Pawsome adventures with my cat 🐾",
    "Kneading some love 🐱❤️",
    "Just a cat and her/his human 🐾",
    "I work hard so my cat can have a better life 🐱",
    "Cat kisses fix everything 🐾",
    "Purrspective is everything 🐱✨",
    "A cat's love is fur real 🐾",
    "In ancient times, cats were worshipped. They haven't forgotten this 🐱",
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
    img = requests.get(f"https://cataas.com/cat").content
    tags = random.sample(tags_, 4)
    mime = "image/jpg"
    url = upload_file(f"Posts/{post_id}.{mime.split('/')[1]}", img, mime)

    post = {
        "_id": post_id,
        "caption": random.choice(captions),
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