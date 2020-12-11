from datetime import datetime
from sqlalchemy import or_
from app import db
from dataclasses import dataclass

@dataclass
class Guild(db.Model):
  guild_id : int = db.Column(db.Integer, primary_key=True)
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
  guild_id: int = db.Column(db.Integer, db.ForeignKey('guild.guild_id'), primary_key=True)
  guild = db.relationship("Guild", back_populates="player", foreign_keys=[guild_id])
  name: str = db.Column(db.String(32), index=True)
  level: int = db.Column(db.Integer)
  playable_class: str = db.Column(db.String(32))
  race: str = db.Column(db.String(32))
  rank: int = db.Column(db.Integer)
  last_modified: int = db.Column(db.Integer)

  def __init__(self, player_id, guild_id, name, level, playable_class, race, rank, last_modified):
    self.player_id = player_id
    self.guild_id = guild_id
    self.name = name
    self.level = level
    self.playable_class = playable_class
    self.race = race
    self.rank = rank
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
