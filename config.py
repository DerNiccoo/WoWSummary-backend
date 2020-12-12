import os
import json

with open('config.json') as config_file:
  config = json.load(config_file)

class Config(object):
  SECRET_KEY = config.get('SECRET_KEY') or 'debug-key-use-env'
  
  SQLALCHEMY_DATABASE_URI = config.get('DATABASE_URL') or 'postgresql:///wowsummary'
  SQLALCHEMY_TRACK_MODIFICATIONS = False

  BLIZZ_CLIENT_ID = config.get('BLIZZ_CLIENT_ID') or 'BLIZZ_CLIENT_ID'
  BLIZZ_CLIENT_SECRET = config.get('BLIZZ_CLIENT_SECRET') or 'BLIZZ_CLIENT_SECRET'