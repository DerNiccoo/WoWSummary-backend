from app import app
from app import db
from app.models import Guild, Guild_player
from flask import Flask, render_template, redirect, request, jsonify, make_response

import requests
from requests.auth import HTTPBasicAuth

@app.route("/guild/<string:realm>/<string:guild>/roster")
def get_player_from_guild(realm, guild):

  body = 'grant_type=client_credentials'
  header = {'Content-Type': 'application/x-www-form-urlencoded',}
  response = requests.post('https://eu.battle.net/oauth/token', data=body, headers=header, auth=HTTPBasicAuth(app.config['BLIZZ_CLIENT_ID'], app.config['BLIZZ_CLIENT_SECRET']))

  return make_response(jsonify(action = response.text), 200)