from datetime import datetime
from sqlalchemy import or_
from app import db

class Guild(db.Model):
  guild_id = db.Column(db.Integer, primary_key=True)
  realm = db.Column(db.String(32))
  name = db.Column(db.String(32), index=True)
  faction = db.Column(db.String(16))
  player = db.relationship("Guild_player", back_populates="guild")

class Guild_player(db.Model):
  player_id = db.Column(db.Integer, primary_key=True)
  guild_id = db.Column(db.Integer, db.ForeignKey('guild.guild_id'), primary_key=True)
  guild = db.relationship("Guild", back_populates="player", foreign_keys=[guild_id])
  name = db.Column(db.String(32), index=True)
  playable_class = db.Column(db.String(32))
  race = db.Column(db.String(32))
  rank = db.Column(db.Integer)
  character_id = db.Column(db.Integer)