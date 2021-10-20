import os
import subprocess
import sys

from discord.ext.commands import Bot, Cog
from discord.ext import commands

class Admin(Cog):
  def __init__(self, bot: Bot):
    self.bot = bot

  @commands.command(
    name="update",
    description="Update the client",
    brief="Update the client",
    hidden=True,
  )
  async def update_command(self, ctx):
    if str(ctx.author.id) not in self.bot.owner_id:
      return
    
    cmd = subprocess.run(["git", "pull"])
    if cmd.returncode == 0:
      await ctx.send('Bot updated\nRestart the bot to apply the changes')
    else:
      await ctx.send(f'Error at update [{cmd.returncode}]')

  @commands.command(
    name="restart",
    description="Restart the client",
    brief="Restart the client",
    hidden=True,
  )
  async def restart_command(self, ctx):
    if str(ctx.author.id) not in self.bot.owner_id:
      return
    
    try:
      os.execv(sys.executable, ['python'] + sys.argv)
    except Exception as e:
      print(e)
      await ctx.send(f'Error at restart')

  @commands.command(
    name="shutdown",
    description="Shutdown the client",
    brief="Shutdown the client",
    hidden=True,
  )
  async def shutdown_command(self, ctx):
    if str(ctx.author.id) not in self.bot.owner_id:
      return
    sys.exit()


def setup(bot: Bot):
  bot.add_cog(Admin(bot))
