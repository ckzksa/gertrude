import discord

from discord.ext.commands import Bot, Cog
from discord.ext import commands
from discord_components import DiscordComponents, Button, ButtonStyle

class General(Cog):
  def __init__(self, bot: Bot):
    self.bot = bot

  @commands.command(
    name="serverinfo",
    description="Get some info about this server",
    brief="Get some info about this server",
  )
  async def serverinfo_command(self, ctx):
    server = ctx.guild
    roles = [x.name for x in server.roles]
    role_length = len(roles)
    if role_length > 50:
        roles = roles[:50]
        roles.append(f">>>> Displaying[50/{len(roles)}] Roles")
    roles = ", ".join(roles)
    channels = len(server.channels)
    time = str(server.created_at)
    time = time.split(" ")
    time = time[0]

    embed = discord.Embed(
        title="**Server Name:**",
        description=f"{server}",
        color=0x42F56C
    )
    embed.set_thumbnail(
        url=server.icon_url
    )
    embed.add_field(
        name="Server ID",
        value=server.id
    )
    embed.add_field(
        name="Member Count",
        value=server.member_count
    )
    embed.add_field(
        name="Text/Voice Channels",
        value=f"{channels}"
    )
    embed.add_field(
        name=f"Roles ({role_length})",
        value=roles
    )
    embed.set_footer(
        text=f"Created at: {time}"
    )
    await ctx.send(embed=embed)

  @commands.command(
    name="ping",
  )
  async def ping_command(self, ctx):
    await ctx.send(content=f'🏓 pong! `{round(self.bot.latency * 1000)}ms`')

  @commands.group(
    name="invite",
    description="Get an invite link",
    brief="Get an invite link",
  )
  async def invite_command(self, ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send('Invalid command')

  @invite_command.command(
    name="bot",
    description="Get the invite link of the bot",
    brief="Get the invite link of the bot",
  )
  async def invite_bot_command(self, ctx):
    link = f"https://discordapp.com/oauth2/authorize?&client_id={self.bot.config['application_id']}&permissions=8&scope=bot%20applications.commands"
    await ctx.send(content='Here is a link to invite Gertrude:', components = [Button(label = "Invite me!", url=link, style=ButtonStyle.URL)],)
  
  @invite_command.command(
    name="server",
    description="Get an invite link to join the server",
    brief="Get an invite link to join the server",
  )
  async def invite_server_command(self, ctx):
    link = await ctx.channel.create_invite(max_uses=1, unique=True)
    await ctx.send(link)

def setup(bot: Bot):
  bot.add_cog(General(bot))