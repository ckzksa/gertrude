import discord
import asyncio
import logging

from discord_components import Button, ButtonStyle

log = logging.getLogger(__name__)

class Rockpaperscissors():
  def __init__(self, bot, ctx, user: discord.Member) -> None:
    self.bot = bot
    self.ctx = ctx
    self.user = user
  
  async def play(self):
    if self.ctx.author == self.user:
      await self.ctx.send(f"{self.ctx.author.mention} You can't challenge yourself!")
      return
    if self.user.bot:
      await self.ctx.send(f"{self.ctx.author.mention} Bots can't play!")
      return

    game_over = False
    players = {
      self.user: None,
      self.ctx.author: None,
    }

    components = [
      [
        Button(style=ButtonStyle.gray, label='Rock', custom_id='0'), 
        Button(style=ButtonStyle.gray, label='Paper', custom_id='1'), 
        Button(style=ButtonStyle.gray, label='Scissors', custom_id='2')
      ],
    ]

    log.debug(f'RockPaperScissors started between {self.user} and {self.ctx.author}')

    challenge_message = await self.ctx.send(content=f'{self.user.mention}, {self.ctx.author.mention} challenged you to Rock Paper Scissors!', components=components)

    def event_check(event):
      return (
        event.message.id == challenge_message.id
        and event.user in players
        and players[event.user] is None
      )

    def is_win():
      if None in players.values():
        return False, None

      player_iter = iter(players.items())
      player_one = next(player_iter)
      player_two = next(player_iter)

      if player_one[1] == player_two[1]:
        return True, None

      if ((player_one[1] == 0 and player_two[1] == 2)
        or (player_one[1] == 1 and player_two[1] == 0)
        or (player_one[1] == 2 and player_two[1] == 1)):
        return True, player_one[0]
      return True, player_one[1]
    
    try:
      while True:
        interaction = await self.bot.wait_for("button_click", check=event_check, timeout=60)
        clicked_button = interaction.component

        if type(clicked_button) is not dict:
          clicked_button = interaction.component.to_dict()
        players[interaction.user] = int(clicked_button["custom_id"])

        game_over, winner = is_win()
        components = [
          [
            Button(style=ButtonStyle.gray, label='Rock', disabled=game_over, custom_id='0'), 
            Button(style=ButtonStyle.gray, label='Paper', disabled=game_over, custom_id='1'), 
            Button(style=ButtonStyle.gray, label='Scissors', disabled=game_over, custom_id='2')
          ],
        ]

        if game_over:
          if winner is None:
            await interaction.respond(type=7, content=f'It is a tie!')
            return
          else:
            await interaction.respond(type=7, content=f'{winner.mention} won!')
            return

        await interaction.respond(type=7, content=f'{self.user.mention}, {self.ctx.author.mention} challenged you to Rock Paper Scissors!', components=components)
        
    except asyncio.exceptions.TimeoutError as e:
      log.warn(f'RockPaperScissors Timeout message_id={challenge_message.id}')
      await challenge_message.delete()
    except Exception as e:
      log.error(e)
      await challenge_message.edit(content=f'Oooops an error occured')