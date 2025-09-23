import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Handle DATABASE_URL (fix postgres:// to postgresql:// if needed)
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = database_url or \
        'sqlite:///' + os.path.join(basedir, '..', 'instance', 'aethermere.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False

    # Rate limiting configuration - use Redis if available, otherwise use PostgreSQL
    redis_url = os.environ.get('REDIS_URL')
    if redis_url:
        RATELIMIT_STORAGE_URL = redis_url
    elif database_url and 'postgresql' in database_url:
        RATELIMIT_STORAGE_URL = database_url
    else:
        RATELIMIT_STORAGE_URL = 'memory://'

    RATELIMIT_DEFAULT = "1000 per hour"