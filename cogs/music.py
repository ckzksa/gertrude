import json
import discord
import re
import random

from discord import FFmpegPCMAudio
from discord.ext import commands
from youtube_dl import YoutubeDL

YDL_OPTIONS = {
  'format': 'bestaudio', # bestaudio prevents live streams
  'quiet': True,
  'postprocessors' : [{
      'key' : 'FFmpegExtractAudio',
      'preferredcodec' : 'mp3',
      'preferredquality' : '192',
  }],
  'noplaylist' : True,
  'logtostderr': False,
  'no_warnings': True,
  'nocheckcertificate': True,
  'ignoreerrors': False,
}

FFMPEG_OPTIONS = {
  'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 
  'options': '-vn'
}

URL_VALIDATOR = re.compile(
  r'^(?:http|ftp)s?://' # http:// or https://
  r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
  r'localhost|' #localhost...
  r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
  r'(?::\d+)?' # optional port
  r'(?:/?|[/?]\S+)$', re.IGNORECASE)

class Song():
  def __init__(self, str, requester) -> None:
    self.requester = requester
    with YoutubeDL(YDL_OPTIONS) as ydl:
      if re.match(URL_VALIDATOR, str) is not None:
        self.meta = ydl.extract_info(str, download=False)
      else:
        print(f"Searching for {str} on Youtube")
        self.meta = ydl.extract_info(f"ytsearch:{str}", download=False)['entries'][0]
        print(f"Found {self.meta['title']}")

  @property
  def url(self):
    return self.meta['url'] # TODO select format to handle lives and videos


class  Queue():
  def __init__(self, guild=None) -> None:
    self.guild = guild
    self.queue = []
    self.is_loop = False
  
  @property
  def length(self):
    return len(self.queue)
  
  def add(self, song: Song):
    self.queue.append(song)

  def pop(self):
    if len(self.queue) < 1:
      return None
    song = self.queue.pop(0)
    return song
  
  def clear(self):
    self.queue = []

  def shuffle(self):
    random.shuffle(self.queue)
  
  def remove(self, id):
    del self.queue[id]
    

class Music(commands.Cog, name="Music"):
  def __init__(self, bot: commands.Bot) -> None:
    self.bot = bot
    self.playing_song = None
    self.queues = {}

  def get_queue_or_create(self, guild):
    if self.queues.get(guild) is None:
      self.queues[guild] = Queue(guild)
    return self.queues[guild]

  @commands.command(
    name="join",
    description="Join the dark side of the channel",
    brief="Join the dark side of the channel",
  )
  async def join_command(self, ctx):
    voice = ctx.message.author.voice
    if voice is None:
      await ctx.send('You are not in a voice channel')
      return False
    
    if ctx.voice_client and ctx.voice_client.is_connected():
      await ctx.voice_client.move_to(voice.channel)
    else:
      await voice.channel.connect()
    
    return True

  @commands.command(
    name="leave",
    description="Leave the voice channel",
    brief="Leave the voice channel",
    aliases=['quit', 'getout', 'movebitch'],
  )
  async def leave_command(self, ctx):
    if ctx.voice_client and ctx.voice_client.is_connected():
      await ctx.voice_client.disconnect()

      if self.queues.get(ctx.guild):
        del self.queues[ctx.guild]

  def play_next(self, ctx):
    if not ctx.voice_client:
      return
    
    queue = self.get_queue_or_create(ctx.guild)
    if self.playing_song is not None and queue.is_loop:
      queue.add(self.playing_song)

    self.playing_song = queue.pop()
    if not self.playing_song: return

    print(f"Playing {self.playing_song.meta['title']} on {ctx.guild.name}")
    ctx.voice_client.play(FFmpegPCMAudio(self.playing_song.url, **FFMPEG_OPTIONS), after=lambda e: self.play_next(ctx))

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
      
    if ctx.voice_client.is_paused():
      ctx.voice_client.resume()
    elif not ctx.voice_client.is_playing():
      self.play_next(ctx)
    
  @commands.command(
    name="pause",
    description="Pause the groovy song",
    brief="Pause the groovy song",
  )
  async def pause_command(self, ctx):
    if ctx.voice_client.is_playing():
      ctx.voice_client.pause()

  @commands.command(
    name="resume",
    description="Resume the funky song",
    brief="Resume the funky song",
  )
  async def resume_command(self, ctx):
    if ctx.voice_client.is_paused():
      ctx.voice_client.resume()

  def format_duration(self, duration):
    if duration <= 0:
      return 'LIVE'
      
    formated_duration = ''
    seconds = duration % 60
    minutes = duration // 60 % 60
    hours = duration // 60 // 60

    formated_duration = f'{str(minutes).rjust(2, "0")}:{str(seconds).rjust(2, "0")}'
    if hours > 0:
      return f'{str(hours).rjust(2, "0")}:' + formated_duration
    return formated_duration

  @commands.command(
    name="add",
    description="Add a song to the queue",
    brief="Add a song to the queue",
  )
  async def add_command(self, ctx, *, url):
    try:
      if url:
        song = Song(url, ctx.message.author)
        queue = self.get_queue_or_create(ctx.guild)
        queue.add(song)

        await ctx.message.delete()
        embed = discord.Embed(
          title=song.meta['title'],
          url=song.meta['webpage_url'],
          description=f'{song.meta["uploader"]}  [{self.format_duration(song.meta["duration"])}]',
          color=discord.Colour.dark_purple())
        embed.set_thumbnail(url=song.meta['thumbnails'][0]['url'])
        embed.set_footer(text=f'added by {song.requester.name}')
        await ctx.send(embed=embed)
    except Exception as e:
      await ctx.send(content='Unable to load this song')
      print(e)
      return False
    return True

  @commands.command(
    name="clear",
    description="Clear the queue",
    brief="Clear the queue",
  )
  async def clear_command(self, ctx):
    self.get_queue_or_create(ctx.guild).clear()

  @commands.command(
    name="skip",
    description="Play the next song",
    brief="Play the next song",
    aliases=['next'],
  )
  async def skip_command(self, ctx):
    if ctx.voice_client.is_paused() or ctx.voice_client.is_playing():
      ctx.voice_client.stop()

  @commands.command(
    name="queue",
    description="Show list of songs",
    brief="Show list of songs",
    aliases=['list'],
  )
  async def queue_command(self, ctx):
    total_duration = 0
    list = ''
    queue = self.get_queue_or_create(ctx.guild)

    if queue.length <= 0:
      await ctx.send('The queue is empty')
      return

    for i, song in enumerate(queue.queue):
      list += f'[{i}] {song.meta["title"]} [{self.format_duration(song.meta["duration"])}] added by {song.requester}\n'
      total_duration += song.meta["duration"]

    embed = discord.Embed(
      title=f'{self.playing_song.meta["title"]}',
      url=self.playing_song.meta['url'],
      description=list,
      color=discord.Colour.dark_purple())
    embed.set_author(name='NOW PLAYING', icon_url='https://cdn.pixabay.com/photo/2016/02/01/12/33/play-1173551_1280.png')
    embed.set_thumbnail(url=self.playing_song.meta['thumbnails'][0]['url'])
    embed.set_footer(text=f'{queue.length} tracks [{self.format_duration(total_duration)}] - loop is {"ON" if queue.is_loop else "OFF"}')
    await ctx.send(embed=embed)

  @commands.command(
    name="loop",
    description="Toggle loop of doom",
    brief="Toggle loop of doom",
  )
  async def loop_command(self, ctx):
    queue = self.get_queue_or_create(ctx.guild)
    queue.is_loop = not queue.is_loop
    await ctx.send(content="Loop activated" if queue.is_loop else "Loop deactivated")

  @commands.command(
    name="shuffle",
    description="Shuffle the queue",
    brief="Shuffle the queue",
  )
  async def shuffle_command(self, ctx):
    if self.queues.get(ctx.guild):
      self.queues[ctx.guild].shuffle()

  @commands.command(
    name="remove",
    description="Remove a song from the queue",
    brief="Remove a song from the queue",
  )
  async def remove_command(self, ctx, id=None):
    if id is None:
      self.playing_song = None
      await ctx.invoke(self.skip_command)

    queue = self.get_queue_or_create(ctx.guild)
    try:
      queue.remove(int(id))
    except ValueError as e:
      print(f"Invalid id ({id}), Must be a integer")
      await ctx.send(content=f"Invalid id ({id}), Must be a integer")
    except IndexError as e:
      print(f"Invalid id ({id}), Out of range")
      await ctx.send(content=f"Invalid id ({id}), Out of range")


def setup(bot: commands.Bot):
  bot.add_cog(Music(bot))