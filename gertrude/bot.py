import os
import json
import sys
import discord
import logging

from discord import Intents
from discord_components import ComponentsBot
from importlib.util import resolve_name


__version__ = '1.0'
log = logging.getLogger(__name__)

class ServerEntry():
  def __init__(self, guild_id) -> None:
    self.guild_id = guild_id

class Bot(ComponentsBot):
  def __init__(self, config_filename='config/config.json') -> None:
    if not os.path.isfile(config_filename):
      log.critical(f'No \'{config_filename}\' found! Please add it and try again.')
      sys.exit(-1)
    else:
      with open(config_filename) as file:
        self.config = json.load(file)

    super().__init__(
      command_prefix=self.config['prefix'],
      description='Gertrude the handly bot',
      owner_id=self.config['owner'],
      case_insensitive=True,
      intents=Intents.default(),
    )

    self.server_entries = {}

    @self.event
    async def on_ready():
      print(f" _____           _                  _      \n|  __ \         | |                | |     \n| |  \/ ___ _ __| |_ _ __ _   _  __| | ___ \n| | __ / _ \ '__| __| '__| | | |/ _` |/ _ \ \n| |_\ \  __/ |  | |_| |  | |_| | (_| |  __/\n \____/\___|_|   \__|_|   \__,_|\__,_|\___| v{__version__}\n")
      print(f'Discord.py v{discord.__version__}')
      log.info('Bot started')
      log.info(f'Logged in as {self.user.name}')
    
    @self.event
    async def on_message(message):
      if message.author.bot:
        return
      await self.process_commands(message)

    @self.event
    async def on_guild_available(ctx):
      if self.server_entries.get(ctx.id) is None:
        self.server_entries[ctx.id] = ServerEntry(ctx.id)
      return self.server_entries[ctx.id]

  # TODO change to full modable
  def load_extensions(self):
    cogs = [
      '.'.join(os.path.normpath(os.path.join(dp, f)).split(os.sep))[:-3]
      for dp, _, fn in os.walk(os.path.expanduser("./gertrude/cogs")) 
      for f in fn if f.endswith('_cog.py')
    ]

    for cog in cogs:
      try:
        self.load_extension(resolve_name(cog, __package__))
        log.error(f'Loaded extension \'{cog}\'')
      except Exception as e:
        exception = f"{type(e).__name__}: {e}"
        log.error(f'Failed to load extension {cog}\n{exception}')

  def launch(self):
    self.load_extensions()
    self.run(self.config['token'])

if __name__ == "__main__":
  bot = Bot()
  bot.launch()
