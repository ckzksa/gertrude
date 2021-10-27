import os
import subprocess
import sys
import logging

from discord.ext.commands import Bot, Cog
from discord.ext import commands

log = logging.getLogger(__name__)

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
  
    process = subprocess.Popen(["git", "pull"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    if type(out) is bytes:
      out = out.decode("utf-8").replace("\n", "")
    if type(err) is bytes:
      err = err.decode("utf-8").replace("\n", "")
    
    if process.returncode == 0:
      log.info(out)
      await ctx.send(f'{out}')
    else:
      log.error(f'Code={process.returncode} - {err}')
      await ctx.send(f'Error at update [{process.returncode}] - {err}')

  # TODO remember you restarted
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
      log.info('Restarting bot')
      os.execv(sys.executable, ['python'] + sys.argv)
    except Exception as e:
      log.error(e)
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
    log.info('Shutting down bot')
    sys.exit()


def setup(bot: Bot):
  bot.add_cog(Admin(bot))
