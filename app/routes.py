from app import app
from app import db
from app.models import Guild, GuildQuery, Guild_player, Guild_playerQuery, Character_equipment, Character_equipmentQuery, Character_dungeon, Character_dungeonQuery
from flask import Flask, render_template, redirect, request, jsonify, make_response

import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
import datetime

classes = ['warrior', 'paladin', 'hunter', 'rogue', 'prist', 'death-knight', 'shaman', 'mage', 'warlock', 'monk', 'druid', 'demon-hunter']
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

@app.route("/guild/<string:realm>/<string:guild>/dungeons/overview")
def get_player_dungeon_from_guild(realm, guild):
  character = Character_dungeonQuery.get_dungeons_from_guild_player(realm, guild)
  
  if character == None or len(character) == 0:
    return make_response('No Character found', 404)
  else:
    result = []

    for char in character:
      container = dict()
      container['best'] = 0
      container['char_id'] = char['char_id']

      for dungeon in char['dungeon_list']:
        if container['best'] < dungeon.keystone_level:
          container['best'] = dungeon.keystone_level
      
      result.append(container)

    return make_response(jsonify(result), 200)


#region Gear Sektion

@app.route("/guild/<string:realm>/<string:guild>/gear")
def get_player_gear_from_guild(realm, guild):
  characters_gear = Character_equipmentQuery.get_gear_from_guild_player(realm, guild)

  if characters_gear == None or len(characters_gear) == 0:
    return make_response('No Characters found', 404)
  else:
    return make_response(jsonify(characters_gear), 200)

@app.route("/guild/<string:realm>/<string:guild>/gear/overview")
def get_overview_gear(realm, guild):
  characters_gear = Character_equipmentQuery.get_gear_from_guild_player(realm, guild)

  if characters_gear == None or len(characters_gear) == 0:
    return make_response('No Characters found', 404)
  else:
    result = []
    
    for char in characters_gear:
      container = dict()
      container['char_id'] = char['char_id'] # Immer mit ID
      container['gs'] = calculate_char_gs(char['items'])
      legy_level, legy_spell = get_legy_from_gear(char)
      if legy_level is not None:
        container['legy_level'] = legy_level
        container['legy_spell'] = legy_spell

      socketed, total_sockets = get_sockets_for_char(char)
      container['socket_curr'] = socketed
      container['socket_total'] = total_sockets
      container['enchantments'] = get_enchants_for_char(char)
      result.append(container)

    return make_response(jsonify(result), 200)

def get_enchants_for_char(char_gear):
  enchantable_slots = ['MAIN_HAND', 'OFF_HAND', 'BACK', 'CHEST', 'FINGER_1', 'FINGER_2']
  primay_slots = ['WRIST', 'HANDS', 'FEET']
  res = []

  for item in char_gear['items']:
    if item.slot in enchantable_slots:
      res.append({'slot': item.slot, 'enchant': item.enchantments})
    if item.slot in primay_slots:
      res.append({'slot': 'PRIMARY', 'enchant': item.enchantments})

  return res

def get_sockets_for_char(char_gear):
  current = 0
  total = 0

  for item in char_gear['items']:
    if item.socket is not None:
      if item.socket > 0:
        current += 1
      total += 1

  return (current, total)

def get_legy_from_gear(char_gear):
  for item in char_gear['items']:
    if item.legy_spell is not None:
      return (item.level, item.legy_spell)
  return (None, None)


def calculate_char_gs(gear_data):
  dont_count = ['SHIRT', 'TABARD']
  
  gs = 0
  use_two_handed = True
  for item in gear_data:
    if item.slot not in dont_count:
      gs += item.level
    if item.slot == 'OFF_HAND':
      use_two_handed = False

  if use_two_handed:
    gs = gs / 15
  else:
    gs = gs / 16

  return float("{:.2f}".format(gs))

#endregion

def refresh_guild(guild_data, last_modified, recorded_modified):
  if recorded_modified == 0: # INSERT INTO
    guild = Guild(guild_data['id'], guild_data['realm'], guild_data['name'], guild_data['faction'], last_modified)
    db.session.add(guild)
    db.session.commit()
  elif recorded_modified + refresh_interval < last_modified: # UPDATE
    guild = Guild(guild_data['id'], guild_data['realm'], guild_data['name'], guild_data['faction'], last_modified)
    GuildQuery.update_guild(guild)

def find_char_in_guild_character(guild_character, char):
  for g_chars in guild_character:
    if g_chars.name == char['name']:
      return g_chars
  return None

def refresh_guild_roster(guild_roster, guild_id, token):
  guild_character = Guild_playerQuery.get_all_guild_id_player(guild_id)

  for char in guild_roster:
    gear_data, char_last_modified = update_character_equipment(char['realm'], char['name'], token)
    
    if gear_data is None:
      continue

    stored_char = find_char_in_guild_character(guild_character, char)

    if stored_char is not None and stored_char.last_modified + refresh_interval  >= char_last_modified: # An dem Char hat sich nix geändert, wir brauchen keine weiteren calls mehr zu machen!
      continue
      # db.session.delete(stored_char) DEBUG
    elif stored_char is not None and stored_char.last_modified + refresh_interval < char_last_modified: # An dem Char hat sich etwas geändert, wir müssen ALLES dazugehörige löschen!
      db.session.delete(stored_char)

    player = Guild_player(char, guild_id, char_last_modified)
    #### das davor sollte für alle Endpunkt gleich bleiben, es folgen "nur noch" das erneuern der anderen Endpunkte

    ### Example für Gear, später ausgliedern in eigenen Baustein

    for item in gear_data:
      piece = Character_equipment(char['id'], item)
      db.session.add(piece)

    ### End of Gear

    dungeons = update_character_mythic_plus(char['realm'], char['name'], token)
    if dungeons is not None:
      for dungeon in dungeons:
        dung = Character_dungeon(dungeon)
        db.session.add(dung)


    db.session.add(player)

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
  refresh_guild_roster(guild_roster['character'], guild_roster['guild']['id'], access_token)   #guild_roster['guild']['id'], guild_roster_lm, 0)#last_modified)








  # Schauen ob Gilde bereits vorhanden, wenn ja:
  # Vergleichen, ob LM größer als der in DB ist
  # Wenn ja: Updaten! (Gilden Meta infos)
  # Updaten Spieler: Loopen, Schauen ob ID existiert, wenn ja einfach alle roster Daten überschreiben, wenn ID nicht existiert, neu anlegen mit LM = 0 (maybe guter default wert?)
  # 
  # Spieler Updaten: Loopen über alle Spieler, mini call machen um LM zu erhalten, mit dem im Spieler abgleichen. Wenn neuer -> Alle Spieler Endpunkte updaten!

  return make_response(guild_roster, 200)

def convert_datetime(date_time_str):
  return int(datetime.datetime.strptime(date_time_str, '%a, %d %b %Y %H:%M:%S %Z').timestamp())

#region BlizzardCalls (outsource)

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
    if member['character']['level'] < 60:
      continue

    char = dict()
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

def update_character_equipment(realm, character, token):
  response = requests.get(f'https://eu.api.blizzard.com/profile/wow/character/{realm}/{character.lower()}/equipment?namespace=profile-eu&locale=de_DE&access_token={token}')

  res = response.json()
  items = []

  if not 'equipped_items' in res:
    print(character)
    return None, None

  for char_item in res['equipped_items']:
    item = dict()
    item['id'] = char_item['item']['id']
    item['slot'] = char_item['slot']['type']
    item['quality'] = char_item['quality']['type']
    item['name'] = char_item['name']
    item['itemClass'] = char_item['item_class']['name']
    item['itemSubclass'] = char_item['item_subclass']['name']
    item['level'] = char_item['level']['value']

    if "sockets" in char_item:
      if 'item' in char_item['sockets'][0]:
        item['socket'] = char_item['sockets'][0]['item']['id']
      else:
        item['socket'] = 0

    if "enchantments" in char_item:
      if 'enchantment_id' in char_item['enchantments'][0]:
        item['enchantments'] = char_item['enchantments'][0]['enchantment_id']

    if item['quality'] == 'LEGENDARY':
      if 'legacy' not in char_item:
        item['legy_spell'] = char_item['spells'][0]['spell']['id']

    items.append(item)

  return (items, convert_datetime(response.headers['Last-Modified']))

def update_character_mythic_plus(realm, character, token):
  response = requests.get(f'https://eu.api.blizzard.com/profile/wow/character/{realm}/{character.lower()}/mythic-keystone-profile?namespace=profile-eu&locale=de_DE&access_token={token}')
  res = response.json()

  if 'current_period' not in res:
    return None

  if 'best_runs' not in res['current_period']:
    return None

  result = []
  for run in res['current_period']['best_runs']:
    data = dict()
    data['intime'] = run['is_completed_within_time']
    data['keystone_level'] = run['keystone_level']
    data['dungeon'] = run['dungeon']['name']
    data['duration'] = run['duration']
    data['dungeon_id'] = run['dungeon']['id']
    data['player_id'] = res['character']['id']
    data['dungeon_period'] = res['current_period']['period']['id']
    result.append(data)

  return result

#endregion