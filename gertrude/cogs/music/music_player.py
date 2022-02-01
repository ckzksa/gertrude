import json
import logging
import os

from discord import FFmpegPCMAudio
from .playlist import Playlist
from .music_entry import MusicEntry
from .downloader import Downloader
from .exceptions import *

log = logging.getLogger(__name__)

FFMPEG_OPTIONS = {
  'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 
  'options': '-vn'
}

class MusicPlayer():
  def __init__(self, bot, guild_id) -> None:
    self.bot = bot
    self.guild_id = guild_id
    self.downloader = Downloader()
    self.playlist = Playlist(guild_id)
    self.voice_client = None
    self.volume = 0.5
    self.current_track = None

  def is_loop(self):
    return True if self.playlist.is_loop else False

  def is_paused(self):
    return self.voice_client and self.voice_client.is_paused()

  def is_playing(self):
    return self.voice_client and self.voice_client.is_playing()

  def is_connected(self):
    return self.voice_client and self.voice_client.is_connected()

  def loop(self, value=None):
    self.playlist.loop(value)

  def shuffle(self):
    self.playlist.shuffle()

  def playlist_is_empty(self):
    return self.playlist.is_empty()

  def playlist(self, to_play=False):
    if to_play:
      return self.playlist.to_be_played
    else:
      return self.playlist

  def play(self):
    if self.is_playing():
      return

    if self.current_track == None and self.playlist.next_track >= self.playlist.size:
      self.current_track = self.playlist.select(0)
    else:
      self.current_track = self.playlist.next()

    if self.current_track:
      self.voice_client.play(FFmpegPCMAudio(self.current_track.url, **FFMPEG_OPTIONS), after=lambda e: self.play())
      
  def rewind(self):
    self.playlist.select(0)
    if self.is_paused() or self.is_playing():
      self.voice_client.stop()

  def pause(self):
    if self.is_playing():
      self.voice_client.pause()

  def resume(self):
    if self.is_paused():
      self.voice_client.resume()

  def next(self, index=None):
    if self.is_paused() or self.is_playing():
      if index != None:
        self.playlist.next_track = index
      self.voice_client.stop()

  def previous(self):
    if self.is_paused() or self.is_playing():
      if self.playlist.index == 0:
        return False
      self.playlist.next_track = self.playlist.index - 1
      self.voice_client.stop()
      return True

  async def join(self, voice, guild):
    if voice is None:
      raise NotConnectedException(message='You are not in a voice channel')

    if self.is_connected():
      await self.voice_client.move_to(voice.channel)
    else:
      await voice.channel.connect()
    self.voice_client = guild.voice_client

  async def disconnect(self):
    if self.is_connected():
      await self.voice_client.disconnect()

  async def add(self, author, url):
    data = await self.downloader.extract_info(url=url, download=False)
    if isinstance(data, tuple):
      entries, data = data
      for e in entries:
        entry = MusicEntry(author, e)
        self.playlist.add(entry)
      return data
    else:
      entry = MusicEntry(author, data)
      self.playlist.add(entry)
      return entry

  def save_playlist(self, name, author):
    if not os.path.exists(f'./data/playlists/{self.guild_id}'):
      os.makedirs(f'./data/playlists/{self.guild_id}')

    with open(f'./data/playlists/{self.guild_id}/{name}', "w") as fp:
      data = {
        "author": author.name,
        "urls": [entry.webpage_url for entry in self.playlist]
      }
      json.dump(data, fp)

  async def load_playlist(self, author, name):
    with open(f'./data/playlists/{self.guild_id}/{name}', "r") as fp:
      data = json.load(fp)
      for url in data["urls"]:
        await self.add(author, url)
