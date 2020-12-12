from datetime import datetime
from sqlalchemy import or_
from app import db
from dataclasses import dataclass
from sqlalchemy import UniqueConstraint
from flask import jsonify
import json

@dataclass
class Guild(db.Model):
  guild_id : int = db.Column(db.Integer, primary_key=True, unique=True)
  realm: str = db.Column(db.String(32))
  name: str = db.Column(db.String(32), index=True)
  faction: str = db.Column(db.String(16))
  last_modified: int = db.Column(db.Integer)
  player = db.relationship("Guild_player", back_populates="guild")

  def __init__(self, guild_id, realm, name, faction, last_modified):
    self.guild_id = guild_id
    self.realm = realm
    self.name = name
    self.faction = faction
    self.last_modified = last_modified

class GuildQuery(object):
  @staticmethod
  def get_last_modified(guild_id):
    guild = Guild.query.filter(Guild.guild_id == guild_id).first()
    return guild.last_modified if hasattr(guild, 'last_modified') else 0

  @staticmethod
  def get_guild(realm, name):
    guild = Guild.query.filter(Guild.realm.ilike(realm), Guild.name.ilike(name)).first()
    return guild

  @staticmethod
  def update_guild(guild_new):
    guild = Guild.query.filter(Guild.guild_id == guild_new.guild_id).first()
    guild.realm = guild_new.realm
    guild.faction = guild_new.faction
    guild.last_modified = guild_new.last_modified
    db.session.commit()
    return True

@dataclass
class Guild_player(db.Model):
  player_id: int = db.Column(db.Integer, primary_key=True)
  guild_id: int = db.Column(db.Integer, db.ForeignKey('guild.guild_id'))
  guild = db.relationship("Guild", back_populates="player", foreign_keys=[guild_id])
  gear = db.relationship("Character_equipment", back_populates="player_gear")
  name: str = db.Column(db.String(32), index=True)
  level: int = db.Column(db.Integer)
  playable_class: str = db.Column(db.String(32))
  race: str = db.Column(db.String(32))
  rank: int = db.Column(db.Integer)
  last_modified: int = db.Column(db.Integer)
  gear_score: float = db.Column(db.Float)
  UniqueConstraint(player_id, guild_id)

  def __init__(self, char_dict, guild_id, last_modified):
    self.player_id = char_dict['id']
    self.guild_id = guild_id
    self.name = char_dict['name']
    self.level = char_dict['level']
    self.playable_class = char_dict['_class']
    self.race = char_dict['race']
    self.rank = char_dict['rank']
    self.last_modified = last_modified

class Guild_playerQuery(object):
  @staticmethod
  def get_last_modified(player_id):
    player = Guild_player.query.filter(Guild_player.player_id == player_id).first()
    return player.last_modified if hasattr(player, 'last_modified') else 0

  @staticmethod
  def get_all_guild_player(realm, name):
    character = Guild_player.query\
      .join(Guild, Guild.guild_id == Guild_player.guild_id)\
      .filter(Guild.name.ilike(name))\
      .filter(Guild.realm.ilike(realm))\
      .all()
    return character


@dataclass
class Character_equipment(db.Model):
  item_id: int = db.Column(db.Integer, primary_key=True)
  slot: str = db.Column(db.String(32), primary_key=True)

  player_id: int = db.Column(db.Integer, db.ForeignKey('guild_player.player_id'), primary_key=True)
  player_gear = db.relationship("Guild_player", back_populates="gear", foreign_keys=[player_id])

  itemClass: str = db.Column(db.String(32))
  itemSubclass: str = db.Column(db.String(32))
  level: int = db.Column(db.Integer)
  name: str = db.Column(db.String(128))
  quality: str = db.Column(db.String(32))
  UniqueConstraint(item_id, slot, player_id)
  

  def __init__(self, player_id, gear_dict):
    self.player_id = player_id
    self.item_id = gear_dict['id']
    self.itemClass = gear_dict['itemClass']
    self.itemSubclass = gear_dict['itemSubclass']
    self.level = gear_dict['level']
    self.name = gear_dict['name']
    self.quality = gear_dict['quality']
    self.slot = gear_dict['slot']

class Character_equipmentQuery(object):
  @staticmethod
  def get_gear_from_guild_player(realm, guild):
    character = Guild_playerQuery.get_all_guild_player(realm, guild)

    res = []
    for char in character:
      gear_list = Character_equipment.query.filter(Character_equipment.player_id == char.player_id).all()
      res.append({'name': char.name, 'gear_score': char.gear_score, 'items': gear_list})

    return res