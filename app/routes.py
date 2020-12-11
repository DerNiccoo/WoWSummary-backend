from app import app
from app import db
from app.models import Guild, GuildQuery, Guild_player, Guild_playerQuery
from flask import Flask, render_template, redirect, request, jsonify, make_response

import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
import datetime

classes = ['warrior', 'paladin', 'hunter', 'rogue', 'prist', 'death-knight', 'shamane', 'mage', 'warlock', 'monk', 'druid', 'demon-hunter']
refresh_interval = 5 * 60

@app.route("/guild/<string:realm>/<string:guild>")
def get_guild(realm, guild):
  guild = GuildQuery.get_guild(realm, guild)

  if guild == None:
    return make_response('Guild not found', 404)
  else:
    return make_response(jsonify(guild), 200)


@app.route("/guild/<string:realm>/<string:guild>/roster")
def get_player_from_guild(realm, guild):
  character = Guild_playerQuery.get_all_guild_player(realm, guild)
  
  if character == None:
    return make_response('No Character found', 404)
  else:
    return make_response(jsonify(character), 200)


def refresh_guild(guild_data, last_modified, recorded_modified):
  if recorded_modified == 0: # INSERT INTO
    guild = Guild(guild_data['id'], guild_data['realm'], guild_data['name'], guild_data['faction'], last_modified)
    db.session.add(guild)
    db.session.commit()
  elif recorded_modified + refresh_interval < last_modified: # UPDATE
    guild = Guild(guild_data['id'], guild_data['realm'], guild_data['name'], guild_data['faction'], last_modified)
    GuildQuery.update_guild(guild)

def refresh_guild_roster(guild_roster, guild_id, last_modified, recorded_modified):
  if recorded_modified > last_modified:
    return True
  
  for char in guild_roster:
    if recorded_modified == 0: # INSERT INTO
      char = Guild_player(char['id'], guild_id, char['name'], char['level'], char['_class'], char['race'], char['rank'], last_modified)
      db.session.add(char)
    elif recorded_modified + refresh_interval < last_modified:
      print("asd")

  db.session.commit()

@app.route("/refresh")
def refresh_everything():
  body = 'grant_type=client_credentials'
  header = {'Content-Type': 'application/x-www-form-urlencoded',}
  response = requests.post('https://eu.battle.net/oauth/token', data=body, headers=header, auth=HTTPBasicAuth(app.config['BLIZZ_CLIENT_ID'], app.config['BLIZZ_CLIENT_SECRET']))
  
  access_token = response.json()['access_token']

  guild_roster, guild_roster_lm = update_guild_roster('blackrock', 'shockwave', access_token)
  last_modified = GuildQuery.get_last_modified(guild_roster['guild']['id'])

  refresh_guild(guild_roster['guild'], guild_roster_lm, last_modified)
  refresh_guild_roster(guild_roster['character'], guild_roster['guild']['id'], guild_roster_lm, 0)#last_modified)

  # Schauen ob Gilde bereits vorhanden, wenn ja:
  # Vergleichen, ob LM größer als der in DB ist
  # Wenn ja: Updaten! (Gilden Meta infos)
  # Updaten Spieler: Loopen, Schauen ob ID existiert, wenn ja einfach alle roster Daten überschreiben, wenn ID nicht existiert, neu anlegen mit LM = 0 (maybe guter default wert?)
  # 
  # Spieler Updaten: Loopen über alle Spieler, mini call machen um LM zu erhalten, mit dem im Spieler abgleichen. Wenn neuer -> Alle Spieler Endpunkte updaten!

  return make_response(guild_roster, 200)

def convert_datetime(date_time_str):
  return int(datetime.datetime.strptime(date_time_str, '%a, %d %b %Y %H:%M:%S %Z').timestamp())

def update_guild_roster(realm, name, token):
  response = requests.get(f'https://eu.api.blizzard.com/data/wow/guild/{realm}/{name}/roster?namespace=profile-eu&locale=de_DE&access_token={token}')

  res = response.json()

  data = { 'guild': {'name': '', 'id': '', 'realm': '' , 'faction': ''}, 'character': '' }
  data['guild']['name'] = res['guild']['name']
  data['guild']['id'] = res['guild']['id']
  data['guild']['realm'] = res['guild']['realm']['name']
  data['guild']['faction'] = res['guild']['faction']['name']

  chars = []
  for member in res['members']:
    char = {'id': '', 'leve': '', 'name': '', '_class': '', 'realm': '', 'rank': '', 'race': ''}
    char['id'] = member['character']['id']
    char['level'] = member['character']['level']
    char['name'] = member['character']['name']
    char['_class'] = classes[member['character']['playable_class']['id'] - 1]
    char['realm'] = member['character']['realm']['slug']
    char['rank'] = member['rank']
    char['race'] = member['character']['playable_race']['id']
    chars.append(char)

  data['character'] = chars

  return (data, convert_datetime(response.headers['Date']))