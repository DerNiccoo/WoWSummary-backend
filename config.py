import os

class Config(object):
  SECRET_KEY = os.environ.get('SECRET_KEY') or 'debug-key-use-env'
  
  SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql:///wowsummary'
  SQLALCHEMY_TRACK_MODIFICATIONS = False

  BLIZZ_CLIENT_ID = os.environ.get('BLIZZ_CLIENT_ID') or 'BLIZZ_CLIENT_ID'
  BLIZZ_CLIENT_SECRET = os.environ.get('BLIZZ_CLIENT_SECRET') or 'BLIZZ_CLIENT_SECRET'