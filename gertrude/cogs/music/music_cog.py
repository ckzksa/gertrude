import json
import logging
import discord
import time
import asyncio

from discord.ext import commands
from discord_components import Button, ButtonStyle

from .music_entry import MusicEntry
from .exceptions import *
from .utils import *
from .music_player import MusicPlayer

log = logging.getLogger(__name__)

class Music(commands.Cog, name="Music"):
  def __init__(self, bot: commands.Bot) -> None:
    super().__init__()
    self.bot = bot
    self.player_entries = {}
    self.on_button_click_callbacks= {
      "add_music": self.add_music_callback,
      "del_music": self.del_music_callback,
      "playlist_music": self.playlist_music_callback,
      "pause_music": self.pause_music_callback,
      "play_music": self.play_music_callback,
      "previous_music": self.previous_music_callback,
      "next_music": self.next_music_callback,
    }

  @commands.command(
    name="join",
    description="Join the dark side of the channel",
    brief="Join the dark side of the channel",
  )
  async def join_command(self, ctx):
    try:
      await ctx.player.join(ctx.message.author.voice, ctx.message.guild)
      return True
    except NotConnectedException as e:
      await ctx.send(e.message)
    

  @commands.command(
    name="disconnect",
    description="Leave the voice channel",
    brief="Leave the voice channel",
    aliases=['leave', 'quit', 'getout', 'movebitch'],
  )
  async def disconnect_command(self, ctx):
    await ctx.player.disconnect()

  @commands.command(
    name="pause",
    description="Pause the groovy song",
    brief="Pause the groovy song",
  )
  async def pause_command(self, ctx):
    ctx.player.pause()

  @commands.command(
    name="resume",
    description="Resume the funky song",
    brief="Resume the funky song",
  )
  async def resume_command(self, ctx):
    ctx.player.resume()

  @commands.command(
    name="play",
    description="Play a song. Maybe not the expected one",
    brief="Play a song. Maybe not the expected one",
  )
  async def play_command(self, ctx, *, url=None):
    if not ctx.voice_client:
      success = await ctx.invoke(self.join_command)
      if not success:
        return
        
    success = await ctx.invoke(self.add_command, url=url)
    if not success:
      return
    
    if not ctx.player.is_playing():
      ctx.player.play()

  def create_add_embed(self, entry):
    embed = discord.Embed(
      title=entry.title,
      url=entry.webpage_url,
      description=f'{entry.uploader}  [{format_duration(entry.duration)}]',
      color=discord.Colour.dark_purple())
    embed.set_thumbnail(url=entry.thumbnails_url)
    embed.set_footer(text=f'{entry.id}\nadded by {entry.author.name}')
    components = [[
      Button(style=ButtonStyle.blue, label='Add', custom_id='{"id":"add_music"}'),
      Button(style=ButtonStyle.red, label='Remove', custom_id=f'{{"id":"del_music", "track":"{entry.id}"}}'),
      Button(style=ButtonStyle.gray, label='Playlist', custom_id='{"id":"playlist_music"}'),
      ]]
    return embed, components


  def create_add_embed_playlist(self, entry, author):
    embed = discord.Embed(
      title=entry['title'],
      url=entry['webpage_url'],
      description=f'Playlist from {entry["uploader"]}',
      color=discord.Colour.dark_purple())
    embed.set_footer(text=f'added by {author}')
    components = [[
      Button(style=ButtonStyle.blue, label='Add', custom_id='{"id":"add_music"}'),
      # Button(style=ButtonStyle.red, label='Remove', custom_id=f'{{"id":"del_music", "track":"{song.id}"}}'),
      Button(style=ButtonStyle.gray, label='Playlist', custom_id='{"id":"playlist_music"}'),
      ]]
    return embed, components


  @commands.command(
    name="add",
    description="Add a song to the queue",
    brief="Add a song to the queue",
  )
  async def add_command(self, ctx, *, url=None):
    try:
      async with ctx.typing():
        if url:
          entry = await ctx.player.add(ctx.message.author, url)
          await ctx.message.delete()
          if isinstance(entry, MusicEntry):
            embed, components = self.create_add_embed(entry)
          else:
            embed, components = self.create_add_embed_playlist(entry, ctx.message.author)
          await ctx.send(embed=embed, components=components)
    except Exception as e:
      # await ctx.send(content='Unable to load this song')
      await ctx.send(content=e)
      log.error(e)
      return False
    return True

  @commands.command(
    name="next",
    description="Play the next song",
    brief="Play the next song",
    aliases=["skip"],
  )
  async def skip_command(self, ctx):
    ctx.player.next()

  @commands.command(
    name="previous",
    description="Play the previous song",
    brief="Play the previous song",
    aliases=["prev"],
  )
  async def previous_command(self, ctx):
    ctx.player.previous()
    
  def create_playlist_embed(self, player):
    _total_duration = 0
    _playlist = ''

    for i, entry in enumerate(player.playlist[player.playlist.index:]):
      _playlist += f'[{player.playlist.index + i}] {entry.title} [{format_duration(entry.duration)}] added by {entry.author}\n'
      _total_duration += 0 if entry.duration == None else entry.duration

    if player.current_track == None:
      embed = discord.Embed(
        description=_playlist,
        color=discord.Colour.dark_purple())
    else:
      embed = discord.Embed(
        title=f'{player.current_track.title}',
        url=player.current_track.webpage_url,
        description=_playlist,
        color=discord.Colour.dark_purple())
      embed.set_thumbnail(url=player.current_track.thumbnails_url)

    if player.is_playing():
      embed.set_author(name='NOW PLAYING', icon_url='https://cdn.pixabay.com/photo/2016/02/01/12/33/play-1173551_1280.png')
    elif player.is_paused():
      embed.set_author(name='PAUSED', icon_url='https://img.icons8.com/color/50/000000/pause-squared.png')
    else:
      embed.set_author(name='STOPPED', icon_url='https://img.icons8.com/color/50/000000/stop-squared.png')
    embed.set_footer(text=f'{len(player.playlist[player.playlist.index:])} tracks [{format_duration(_total_duration)}] - loop is {"ON" if player.playlist.is_loop else "OFF"}')
    
    components = [[
      Button(style=ButtonStyle.grey, label='⏮️', custom_id='{"id":"previous_music"}'),
      Button(style=ButtonStyle.grey, label='⏸️', custom_id='{"id":"pause_music"}'),
      Button(style=ButtonStyle.grey, label='▶️', custom_id='{"id":"play_music"}'),
      Button(style=ButtonStyle.grey, label='⏭️', custom_id='{"id":"next_music"}')
      ]]

    return embed, components

  @commands.group(
    name="playlist",
    description="Show list of songs",
    brief="Show list of songs",
    aliases=["list", "queue"],
  )
  async def playlist_command(self, ctx):
    if ctx.invoked_subcommand is None:
      if ctx.player.playlist_is_empty():
        await ctx.send('The queue is empty')
        return

      async with ctx.typing():
        embed, components = self.create_playlist_embed(ctx.player)
        await ctx.send(embed=embed, components=components)

  @playlist_command.command(
    name="rewind",
    description="Rewind the playlist",
    brief="Rewind the playlist",
  )
  async def rewind_playlist_command(self, ctx):
    ctx.player.playlist.rewind()

  @playlist_command.command(
    name="save",
    description="Save the current playlist",
    brief="Save the current playlist",
  )
  async def save_playlist_command(self, ctx, name=None):
    try:
      async with ctx.typing():
        if not name:
          await ctx.send('Give it a name.')
          return
        ctx.player.save_playlist(name, ctx.message.author)
        await ctx.send(content="Playlist saved.")
    except Exception as e:
      await ctx.send(content="An error occured.")
      print(e)

  @playlist_command.command(
    name="load",
    description="Load a playlist",
    brief="Load a playlist",
  )
  async def load_playlist_command(self, ctx, name=None):
    try:
      async with ctx.typing():
        if not name:
          await ctx.send('Give me its name.')
          return
        await ctx.player.load_playlist(ctx.message.author, name)
        await ctx.send(content="Playlist loaded.")
    except Exception as e:
      await ctx.send(content="An error occured.")
      print(e)

  @commands.command(
    name="loop",
    description="Toggle loop of doom",
    brief="Toggle loop of doom",
  )
  async def loop_command(self, ctx):
    ctx.player.loop()
    await ctx.send(content="Loop activated" if ctx.player.is_loop else "Loop deactivated")

  @commands.command(
    name="shuffle",
    description="Shuffle the queue",
    brief="Shuffle the queue",
  )
  async def shuffle_command(self, ctx):
    ctx.player.shuffle()

  @commands.command(
    name="remove",
    description="Remove a song from the queue",
    brief="Remove a song from the queue",
    aliases=["rm"],
  )
  async def remove_command(self, ctx, id=None):
    if id == None:
      id = ctx.player.playlist.index
      if id == None:
        await ctx.send(content=f"No playing track.")
        return

    try:
      title = ctx.player.playlist.get(int(id)).meta["title"]
      ctx.player.playlist.remove_by_index(int(id))
      await ctx.send(content=f"{title} removed from the queue")
    except ValueError as e:
      log.warn(f"Invalid id ({id}), Must be a integer")
      await ctx.send(content=f"Invalid id ({id}), Must be a integer")
    except IndexError as e:
      log.warn(f"Invalid id ({id}), Out of range")
      await ctx.send(content=f"Invalid id ({id}), Out of range")

  @commands.command(
    name="clear",
    description="Clear the queue",
    brief="Clear the queue",
  )
  async def clear_command(self, ctx):
    ctx.player.playlist.clear()

  @commands.Cog.listener()
  async def on_button_click(self, interaction):
    try:
      id = json.loads(interaction.custom_id)['id']
    except:
      id = interaction.custom_id
      
    if id in self.on_button_click_callbacks:
      callback = self.on_button_click_callbacks[id]
      await callback(interaction)

  async def add_music_callback(self, interaction):
    player = self.get_player(interaction.guild.id)
    entry = await player.add(interaction.author, interaction.message.embeds[0].url)
    embed, components = self.create_add_embed(entry)
    await interaction.send(embed=embed, components=components)
    
  async def del_music_callback(self, interaction):
    try:
      id = json.loads(interaction.custom_id)['track']
      player = self.get_player(interaction.guild.id)
      track = player.playlist.remove_by_id(int(id))
      if track == None:
        await interaction.send(content="Track not in playlist.")
      else:
        await interaction.send(content=f"{track.title} removed.")
    except Exception as e:
      await interaction.send(content="Impossible to remove track.")
      log.warn(e)

  async def playlist_music_callback(self, interaction):
    player = self.get_player(interaction.guild.id)
    if player.playlist.is_empty():
      await interaction.send('The queue is empty')
      return
    embed, components = self.create_playlist_embed(player)
    await interaction.send(embed=embed, components=components)

  async def pause_music_callback(self, interaction):
    player = self.get_player(interaction.guild.id)
    player.pause()
    await interaction.edit_origin(
      embeds=interaction.message.embeds,
      components=interaction.message.components
    )

  async def play_music_callback(self, interaction):
    player = self.get_player(interaction.guild.id)

    await interaction.edit_origin(
      embeds=interaction.message.embeds,
      components=interaction.message.components
    )
    if not player.voice_client:
      await player.join(interaction.author.voice, interaction.guild)

    if not player.is_playing():
      player.play()

  async def previous_music_callback(self, interaction):
    player = self.get_player(interaction.guild.id)
    player.previous()
    await interaction.edit_origin(
      embeds=interaction.message.embeds,
      components=interaction.message.components
    )

  async def next_music_callback(self, interaction):
    player = self.get_player(interaction.guild.id)
    player.next()
    await interaction.edit_origin(
      embeds=interaction.message.embeds,
      components=interaction.message.components
    )

  def get_player(self, guild_id):
    if guild_id not in self.player_entries:
      self.player_entries[guild_id] = MusicPlayer(self.bot, guild_id)
    return self.player_entries[guild_id]

  async def cog_before_invoke(self, ctx):
    ctx.player = self.get_player(ctx.guild.id)

def setup(bot: commands.Bot):
  bot.add_cog(Music(bot))
