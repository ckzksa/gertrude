import discord
import logging

from cogs.games.tictactoe import Tictactoe
from cogs.games.rps import Rockpaperscissors
from discord.ext.commands import Bot, Cog
from discord.ext import commands

log = logging.getLogger(__name__)

class Game(Cog):
  def __init__(self, bot: Bot):
    self.bot = bot

  @commands.command(
    name="tictactoe",
    description="Start a tictactoe with someone",
    brief="Start a tictactoe with someone",
    aliases=['tic', 'tac', 'toe'],
  )
  async def tictactoe_command(self, ctx, user: discord.Member):
    await Tictactoe(self.bot, ctx, user).play()

  @commands.command(
    name="rockpaperscissors",
    description="Play rock paper scissors",
    brief="Play rock paper scissors",
    aliases=['rps'],
  )
  async def rps_command(self, ctx, user: discord.Member):
    await Rockpaperscissors(self.bot, ctx, user).play()
    

def setup(bot: Bot):
  bot.add_cog(Game(bot))
