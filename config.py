from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    SECRET_KEY              = os.environ.get('SECRET_KEY')
    MONGO_URL               = os.environ.get('MONGO_URL')
    
    SUPABASE_URL            = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY            = os.environ.get('SUPABASE_KEY')

    GOOGLE_CLIENT_ID        = os.environ.get('G_CLIENT_ID')
    GOOGLE_CLIENT_SECRET    = os.environ.get('G_CLIENT_SECRET')

    JWT_SECRET              = os.environ.get('JWT_SECRET')

    TOKEN_EXP = {
        "access": 1,
        "refresh": 30
    }