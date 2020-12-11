from datetime import datetime
from sqlalchemy import or_
from app import db

class Guild(db.Model):
  guild_id = db.Column(db.Integer, primary_key=True)
  realm = db.Column(db.String(32))
  name = db.Column(db.String(32), index=True)
  faction = db.Column(db.String(16))
  last_modified = db.Column(db.DateTime)
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

class Guild_player(db.Model):
  player_id = db.Column(db.Integer, primary_key=True)
  guild_id = db.Column(db.Integer, db.ForeignKey('guild.guild_id'), primary_key=True)
  guild = db.relationship("Guild", back_populates="player", foreign_keys=[guild_id])
  name = db.Column(db.String(32), index=True)
  playable_class = db.Column(db.String(32))
  race = db.Column(db.String(32))
  rank = db.Column(db.Integer)
  last_modified = db.Column(db.DateTime)
  character_id = db.Column(db.Integer)