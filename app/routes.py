from app import app
from app import db
from app.models import Guild, GuildQuery, Guild_player, Guild_playerQuery, Character_equipment, Character_equipmentQuery, Character_dungeon, Character_dungeonQuery, Character_mount, Character_mountQuery, Character_pvp, Character_pvpQuery
from flask import Flask, render_template, redirect, request, jsonify, make_response

import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
import datetime

classes = ['warrior', 'paladin', 'hunter', 'rogue', 'prist', 'death-knight', 'shaman', 'mage', 'warlock', 'monk', 'druid', 'demon-hunter']
refresh_interval = 4 * 60

debug = False

if debug:
  refresh_interval = 0

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
      container['total'] = 0
      container['char_id'] = char['char_id']

      for dungeon in char['dungeon_list']:
        if dungeon.dungeon_type == 'weekly':
          if container['best'] < dungeon.keystone_level:
            container['best'] = dungeon.keystone_level
        if dungeon.dungeon_type == 'highest':
          if container['total'] < dungeon.keystone_level:
            container['total'] = dungeon.keystone_level
      
      result.append(container)

    return make_response(jsonify(result), 200)

@app.route("/guild/<string:realm>/<string:guild>/collection/mounts/overview")
def get_player_mounts_from_guild(realm, guild):
  character = Character_mountQuery.get_mounts_from_guild_player(realm, guild)
  
  if character == None or len(character) == 0:
    return make_response('No Character found', 404)
  else:
    result = []

    for char in character:
      container = dict()
      container['char_id'] = char['char_id']
      container['total'] = 0
      container['usable'] = 0

      for mount in char['mount_list']:
        if mount.useable:
          container['usable'] += 1
        container['total'] += 1
      
      result.append(container)

    return make_response(jsonify(result), 200)

@app.route("/guild/<string:realm>/<string:guild>/pvp/overview")
def get_player_pvp_from_guild(realm, guild):
  character = Character_pvpQuery.get_pvp_from_guild_player(realm, guild)
  
  if character == None or len(character) == 0:
    return make_response('No Character found', 404)
  else:
    result = []

    for char in character:
      container = dict()
      container['char_id'] = char['char_id']
      container['pvp'] = char['pvp_list']
      
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
  
  if guild_character is None:
    return -1

  updated = 0

  for char in guild_roster:
    gear_data, char_last_modified = update_character_equipment(char['realm'], char['name'], token)
    
    if gear_data is None:
      continue

    stored_char = find_char_in_guild_character(guild_character, char)

    if debug and stored_char is not None and stored_char.name == 'Broxger':
      print(f"updating {char['name']}")
      updated += 1
      db.session.delete(stored_char)

    elif stored_char is not None and stored_char.last_modified + refresh_interval  >= char_last_modified: # An dem Char hat sich nix geändert, wir brauchen keine weiteren calls mehr zu machen!
      print(f"skipping {char['name']}")
      continue
      # db.session.delete(stored_char) DEBUG
    elif stored_char is not None and stored_char.last_modified + refresh_interval < char_last_modified: # An dem Char hat sich etwas geändert, wir müssen ALLES dazugehörige löschen!
      print(f"updating {char['name']}")
      updated += 1
      db.session.delete(stored_char)


    player = Guild_player(char, guild_id, char_last_modified)
    #### das davor sollte für alle Endpunkt gleich bleiben, es folgen "nur noch" das erneuern der anderen Endpunkte

    ### Example für Gear, später ausgliedern in eigenen Baustein

    for item in gear_data:
      piece = Character_equipment(char['id'], item)
      db.session.add(piece)

    ### End of Gear

    ### Dungeons
    rio_char, dungeons = get_character_data(char['realm'], char['name'])
    if rio_char is not None:
      player.active_spec_name = rio_char['active_spec_name']
      player.active_spec_role = rio_char['active_spec_role']
      player.achievement_points = rio_char['achievement_points']
      player.covenant = rio_char['covenant']
      player.mythic_rio = rio_char['mythic_rio']
      player.renown_level = rio_char['renown_level']
      player.raid_summary = rio_char['raid_summary']
      player.normal_bosses = rio_char['normal_bosses']
      player.heroic_bosses = rio_char['heroic_bosses']
      player.mythic_bosses = rio_char['mythic_bosses']

      for dungeon in dungeons:
        dung = Character_dungeon(char['id'], dungeon)
        db.session.add(dung)

    ### End of Dungeons
    ### Collection Mounts
    mounts = update_character_collection_mounts(char['realm'], char['name'], token)
    if mounts is not None:
      for mount in mounts:
        horse = Character_mount(char['id'], mount)
        db.session.add(horse)
    ### End of Collection Mounts

    ### PvP
    pvp = update_character_pvp(char['realm'], char['name'], token)
    if pvp is not None:
      for p in pvp:
        char_pvp = Character_pvp(char['id'], p)
        db.session.add(char_pvp)
    ### End of PvP

    db.session.add(player)

  db.session.commit()
  print(f'Updated {updated} Player')
  return updated

@app.route("/refresh")
def refresh_everything():
  guild = GuildQuery.get_guild('blackrock', 'shockwave')

  if guild is not None and guild.last_modified + refresh_interval > datetime.datetime.now().timestamp():
    return make_response(jsonify(action='To early to refresh'), 200)

  body = 'grant_type=client_credentials'
  header = {'Content-Type': 'application/x-www-form-urlencoded',}
  response = requests.post('https://eu.battle.net/oauth/token', data=body, headers=header, auth=HTTPBasicAuth(app.config['BLIZZ_CLIENT_ID'], app.config['BLIZZ_CLIENT_SECRET']))
  
  access_token = response.json()['access_token']

  guild_roster, guild_roster_lm = update_guild_roster('blackrock', 'shockwave', access_token)
  last_modified = GuildQuery.get_last_modified(guild_roster['guild']['id'])

  refresh_guild(guild_roster['guild'], guild_roster_lm, last_modified)
  player_updated = refresh_guild_roster(guild_roster['character'], guild_roster['guild']['id'], access_token)   #guild_roster['guild']['id'], guild_roster_lm, 0)#last_modified)

  return make_response(jsonify(action='Success', updated=player_updated), 200)

def convert_datetime(date_time_str):
  return int(datetime.datetime.strptime(date_time_str, '%a, %d %b %Y %H:%M:%S %Z').timestamp())

#region BlizzardCalls (outsource)

def update_guild_roster(realm, name, token):
  response = requests.get(f'https://eu.api.blizzard.com/data/wow/guild/{realm}/{name}/roster?namespace=profile-eu&locale=de_DE&access_token={token}')

  res = ''

  try:
    res = response.json()
  except:
    print('error with json: ' + res)
    return (None, None)

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

  res = ''

  try:
    res = response.json()
  except:
    print('error with json: ' + res)
    return (None, None)

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
  ''' Currently not used anymore since the raider.io api offers more and better values for the same data with less aggregation '''
  response = requests.get(f'https://eu.api.blizzard.com/profile/wow/character/{realm}/{character.lower()}/mythic-keystone-profile?namespace=profile-eu&locale=de_DE&access_token={token}')

  res = ''

  try:
    res = response.json()
  except:
    print('error with json: ' + res)
    return None

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

def update_character_collection_mounts(realm, character, token):
  response = requests.get(f'https://eu.api.blizzard.com/profile/wow/character/{realm}/{character.lower()}/collections/mounts?namespace=profile-eu&locale=de_DE&access_token={token}')
  
  res = ''

  try:
    res = response.json()
  except:
    print('error with json: ' + res)
    return None

  if 'mounts' not in res:
    return None

  result = []
  
  for iteration in res['mounts']:
    if 'is_character_specific' in iteration:
      continue

    data = dict()
    data['name'] = iteration['mount']['name']
    data['mount_id'] = iteration['mount']['id']
    data['useable'] = iteration['is_useable']
    result.append(data)

  return result

def update_character_pvp(realm, character, token):
  brackets = ['2v2', '3v3']

  result = []
  for bracket in brackets:
    response = requests.get(f'https://eu.api.blizzard.com/profile/wow/character/{realm}/{character.lower()}/pvp-bracket/{bracket}?namespace=profile-eu&locale=de_DE&access_token={token}')
    res = ''

    try:
      res = response.json()
    except:
      print('error with json: ' + res)
      return None
    
    if 'rating' not in res:
      return None

    data = dict()
    data['pvp_type'] = res['bracket']['type']
    data['season'] = res['season']['id']
    data['rating'] = res['rating']
    data['season_won'] = res['season_match_statistics']['won']
    data['season_lost'] = res['season_match_statistics']['lost']
    data['weekly_won'] = res['weekly_match_statistics']['won']
    data['weekly_lost'] = res['weekly_match_statistics']['lost']
    result.append(data)

  return result

#endregion

#region RaiderIO
def create_dungeon_list(dungeon_list, dungeon_type):
  list_runs = []
  for run in dungeon_list:
    run_dict = dict()
    run_dict['dungeon'] = run['dungeon']
    run_dict['dungeon_short'] = run['short_name']
    run_dict['keystone_level'] = run['mythic_level']
    run_dict['duration'] = run['clear_time_ms']
    run_dict['keystone_upgrades'] = run['num_keystone_upgrades']
    run_dict['dungeon_id'] = run['map_challenge_mode_id']
    run_dict['score'] = run['score']
    run_dict['completed_at'] = run['completed_at']
    run_dict['dungeon_type'] = dungeon_type
    list_runs.append(run_dict)      
  
  return list_runs


def get_character_data(realm, name):
  response = requests.get(f'https://raider.io/api/v1/characters/profile?region=eu&realm={realm}&name={name}&fields=covenant%2Craid_progression%2Cmythic_plus_scores_by_season%3Acurrent%2Cmythic_plus_ranks%2Cmythic_plus_recent_runs%2Cmythic_plus_highest_level_runs%2Cmythic_plus_weekly_highest_level_runs')
  res = response.json()

  char = dict()
  if 'name' not in res:
    return (None, None)

  curr_raid = list(res['raid_progression'].values())[0]
  print(curr_raid)

  char['raid_summary'] = curr_raid['summary']
  char['normal_bosses'] = curr_raid['normal_bosses_killed']
  char['heroic_bosses'] = curr_raid['heroic_bosses_killed']
  char['mythic_bosses'] = curr_raid['mythic_bosses_killed']
  char['active_spec_name'] = res['active_spec_name']
  char['active_spec_role'] = res['active_spec_role']
  char['achievement_points'] = res['achievement_points']
  if res['covenant'] is not None:
    char['covenant'] = res['covenant']['name']
    char['renown_level'] = res['covenant']['renown_level']
  else:
    char['covenant'] = '-'
    char['renown_level'] = 0
   

  if 'mythic_plus_scores_by_season' in res:
    char['mythic_rio'] = res['mythic_plus_scores_by_season'][0]['scores']['all']
  
  dungeons = []
  if 'mythic_plus_recent_runs' in res:
    dungeons.extend(create_dungeon_list(res['mythic_plus_recent_runs'], 'recent'))

  if 'mythic_plus_highest_level_runs' in res:
    dungeons.extend(create_dungeon_list(res['mythic_plus_highest_level_runs'], 'highest'))

  if 'mythic_plus_weekly_highest_level_runs' in res:
    dungeons.extend(create_dungeon_list(res['mythic_plus_weekly_highest_level_runs'], 'weekly'))

  return (char, dungeons)

#endregion