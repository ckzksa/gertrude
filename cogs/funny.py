import subprocess
import aiohttp
import logging
import ast

from discord.ext.commands import Bot, Cog
from discord.ext import commands

log = logging.getLogger(__name__)

class Funny(Cog):
  def __init__(self, bot: Bot):
    self.bot = bot

  async def get(self, url):
    try:
      session = aiohttp.ClientSession()
      req = await session.get(url)

      response = await req.read()
      if type(response) is not dict:
        response = ast.literal_eval(response.decode('utf-8'))

      return response
    except:
      raise
    finally:
      await session.close()
    
  @commands.command(
    name="yomomma",
    description="Yo Momma joke",
    brief="Yo Momma joke",
    aliases=['yomoma', 'yomama'],
  )
  async def yomomma_command(self, ctx):
    try:
      response = await self.get('https://api.yomomma.info/')
      await ctx.send(response['joke'])

    except Exception as e:
      log.error(e)
      await ctx.send(f'Oooops an error occured')

  @commands.command(
    name="advice",
    description="Free advice",
    brief="Free advice",
  )
  async def advice_command(self, ctx):
    try:
      response = await self.get('https://api.adviceslip.com/advice')
      await ctx.send(response['slip']['advice'])

    except Exception as e:
      log.error(e)
      await ctx.send(f'Oooops an error occured')

  @commands.command(
    name="boostme",
    description="Gertrude will comfort you",
    brief="Gertrude will comfort you",
  )
  async def boostme_command(self, ctx):
    try:
      response = await self.get('https://www.affirmations.dev/')
      await ctx.send(response['affirmation'])

    except Exception as e:
      log.error(e)
      await ctx.send(f'Oooops an error occured')

  @commands.command(
    name="quote",
    description="Inspiring quote",
    brief="Inspiring quote",
  )
  async def quote_command(self, ctx):
    try:
      response = await self.get('https://api.fisenko.net/v1/quotes/en/random')
      await ctx.send(f"{response['text']} - {response['author']['name']}")

    except Exception as e:
      log.error(e)
      await ctx.send(f'Oooops an error occured')

  @commands.command(
    name="chucknorris",
    description="What would Chuck do?",
    brief="WWCD",
  )
  async def chucknorris_command(self, ctx):
    try:
      response = await self.get('https://api.chucknorris.io/jokes/random')
      await ctx.send(f"{response['value']}")

    except Exception as e:
      log.error(e)
      await ctx.send(f'Oooops an error occured')

def setup(bot: Bot):
  bot.add_cog(Funny(bot))
