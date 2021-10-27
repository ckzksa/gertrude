import subprocess
import aiohttp
import logging
import ast

from discord.ext.commands import Bot, Cog
from discord.ext import commands

log = logging.getLogger(__name__)

class Joke(Cog):
  def __init__(self, bot: Bot):
    self.bot = bot

  @commands.command(
    name="yomomma",
    description="Yo Momma joke",
    brief="Yo Momma joke",
    aliases=['yomoma', 'yomama'],
  )
  async def yomomma_command(self, ctx):
    try:
      session = aiohttp.ClientSession()
      req = await session.get('https://api.yomomma.info/')

      joke = await req.read()
      if type(joke) is not dict:
        joke = ast.literal_eval(joke.decode('utf-8'))

      await ctx.send(joke['joke'])

    except Exception as e:
      log.error(e)
      await ctx.send(f'Oooops an error occured')
    finally:
      await session.close()

def setup(bot: Bot):
  bot.add_cog(Joke(bot))
