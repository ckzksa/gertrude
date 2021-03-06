import discord
import logging

from .tictactoe import Tictactoe
from .rps import Rockpaperscissors
from .dice import Dice
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
    
  @commands.command(
    name="dice",
    description="Roll a dice",
    brief="Roll a dice",
  )
  async def dice_command(self, ctx, dice: str):
    await Dice(self.bot, ctx, dice).play()

def setup(bot: Bot):
  bot.add_cog(Game(bot))
