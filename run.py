import os
import json
import sys
import discord

from discord import Intents
from discord.ext import commands
from discord_components import DiscordComponents

if not os.path.isfile("config.json"):
  sys.exit("'config.json' not found! Please add it and try again.")
else:
  with open("config.json") as file:
    config = json.load(file)

def prefixes(client, message):
  prefixes = ['!', '*']
  return commands.when_mentioned_or(*prefixes)(client, message)

bot = commands.Bot(
  command_prefix=config['prefix'],
  description="Gertrude the handly bot",
  owner_id=config['owner'],
  case_insensitive=True,
  intents=Intents.default(),
)
DiscordComponents(bot)

@bot.event
async def on_ready():
  print(" _____           _                  _      \n|  __ \         | |                | |     \n| |  \/ ___ _ __| |_ _ __ _   _  __| | ___ \n| | __ / _ \ '__| __| '__| | | |/ _` |/ _ \ \n| |_\ \  __/ |  | |_| |  | |_| | (_| |  __/\n \____/\___|_|   \__|_|   \__,_|\__,_|\___|\n")
  print(f"Discord.py v{discord.__version__}")
  print(f"Logged in as {bot.user.name}")
  
@bot.event
async def on_message(message):
  if message.author.bot:
    return
  await bot.process_commands(message)

if __name__ == "__main__":
  for file in os.listdir("./cogs"):
    if file.endswith(".py"):
      extension = file[:-3]
      try:
        bot.load_extension(f"cogs.{extension}")
        print(f"Loaded extension '{extension}'")
      except Exception as e:
        exception = f"{type(e).__name__}: {e}"
        print(f"Failed to load extension {extension}\n{exception}")
  bot.config = config
  bot.run(config["token"])
