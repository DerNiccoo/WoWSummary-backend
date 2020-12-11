from app import app
from app import db
from app.models import Guild, Guild_player
from flask import Flask, render_template, redirect, request, jsonify, make_response

import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
import datetime

@app.route("/guild/<string:realm>/<string:guild>/roster")
def get_player_from_guild(realm, guild):

  body = 'grant_type=client_credentials'
  header = {'Content-Type': 'application/x-www-form-urlencoded',}
  response = requests.post('https://eu.battle.net/oauth/token', data=body, headers=header, auth=HTTPBasicAuth(app.config['BLIZZ_CLIENT_ID'], app.config['BLIZZ_CLIENT_SECRET']))

  return make_response(jsonify(action = response.text), 200)

@app.route("/refresh")
def refresh_everything():
  body = 'grant_type=client_credentials'
  header = {'Content-Type': 'application/x-www-form-urlencoded',}
  response = requests.post('https://eu.battle.net/oauth/token', data=body, headers=header, auth=HTTPBasicAuth(app.config['BLIZZ_CLIENT_ID'], app.config['BLIZZ_CLIENT_SECRET']))
  
  access_token = response.json()['access_token']

  guild_roster, guild_roster_lm = update_guild_roster('blackrock', 'shockwave', access_token)
  print(guild_roster_lm.timestamp())
  # Schauen ob Gilde bereits vorhanden, wenn ja:
  # Vergleichen, ob LM größer als der in DB ist
  # Wenn ja: Updaten! (Gilden Meta infos)
  # Updaten Spieler: Loopen, Schauen ob ID existiert, wenn ja einfach alle roster Daten überschreiben, wenn ID nicht existiert, neu anlegen mit LM = 0 (maybe guter default wert?)
  # 
  # Spieler Updaten: Loopen über alle Spieler, mini call machen um LM zu erhalten, mit dem im Spieler abgleichen. Wenn neuer -> Alle Spieler Endpunkte updaten!

  return make_response(guild_roster, 200)

def convert_datetime(date_time_str):
  return datetime.datetime.strptime(date_time_str, '%a, %d %b %Y %H:%M:%S %Z')

def update_guild_roster(realm, name, token):
  response = requests.get(f'https://eu.api.blizzard.com/data/wow/guild/{realm}/{name}/roster?namespace=profile-eu&locale=de_EU&access_token={token}')
  return (response.json(), convert_datetime(response.headers['Date']))
  