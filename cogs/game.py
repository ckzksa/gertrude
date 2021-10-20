import discord

from cogs.games.tictactoe import Tictactoe
from discord.ext.commands import Bot, Cog
from discord.ext import commands

class Game(Cog):
  def __init__(self, bot: Bot):
    self.bot = bot

  @commands.command(
    name="tictactoe",
    description="Start a tictactoe with someone",
    brief="Start a tictactoe with someone",
  )
  async def tictactoe_command(self, ctx, user: discord.Member):
    Tictactoe(self.bot, ctx, user).play()
    

def setup(bot: Bot):
  bot.add_cog(Game(bot))
