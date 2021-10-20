import discord
import asyncio

from discord_components import Button, ButtonStyle

class Tictactoe():
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

    board = [' '] * 9

    players = {
        'X': self.user,
        'O': self.ctx.author,
    }
    turn = 'X'

    components = [
      [Button(style=ButtonStyle.gray, label=' ', custom_id='0'), Button(style=ButtonStyle.gray, label=' ', custom_id='1'), Button(style=ButtonStyle.gray, label=' ', custom_id='2')],
      [Button(style=ButtonStyle.gray, label=' ', custom_id='3'), Button(style=ButtonStyle.gray, label=' ', custom_id='4'), Button(style=ButtonStyle.gray, label=' ', custom_id='5')],
      [Button(style=ButtonStyle.gray, label=' ', custom_id='6'), Button(style=ButtonStyle.gray, label=' ', custom_id='7'), Button(style=ButtonStyle.gray, label=' ', custom_id='8')],
    ]

    game_message = await self.ctx.send(content=f'{self.user.mention} vs {self.ctx.author.mention}', components=components)

    def is_over(board):
      win_states = [
        (0, 1, 2),
        (3, 4, 5),
        (6, 7, 8),
        (0, 3, 6),
        (1, 4, 7),
        (2, 5, 8),
        (0, 4, 8),
        (2, 4, 6),
      ]

      for state in win_states:
        if board[state[0]] == board[state[1]] == board[state[2]] and board[state[0]] in ('X', 'O'):
          return True, board[state[0]]
      if ' ' in board:
        return False, None
      return True, None

    def event_check(event):
      component = event.component
      if type(component) is not dict:
        component = event.component.to_dict()
      return (
        (component['label'] == ' ')
        and event.message.id == game_message.id
        and (event.user == players[turn])
      )
    
    try:
      while True:
        interaction = await self.bot.wait_for("button_click", check=event_check, timeout=60)
        clicked_button = interaction.component

        if type(clicked_button) is not dict:
          clicked_button = interaction.component.to_dict()

        board[int(clicked_button["custom_id"])] = turn
        game_over, winner = is_over(board)

        components = [[Button(style=ButtonStyle.gray, label=board[x+y], disabled=game_over, custom_id=str(x+y)) for x in range(3)] for y in range(0,8,3)]

        if game_over:
          if winner is None:
            await interaction.respond(type=7, content=f'Game Over! It is a tie!', components=components)
            return
          else:
            await interaction.respond(type=7, content=f'Game Over! {players[turn].mention} won!', components=components)
            return

        turn = 'X' if turn == 'O' else 'O'

        await interaction.respond(type=7, content=f"It is {players[turn].mention}'s turn.", components=components)
    except asyncio.exceptions.TimeoutError as e:
      components = [[Button(style=ButtonStyle.gray, label=board[x+y], disabled=True, custom_id=str(x+y)) for x in range(3)] for y in range(0,8,3)]
      print("timeout")
      await game_message.edit(content=f'Game Over! (timeout)', components=components)
    except Exception as e:
      await game_message.edit(content=f'Oooops an error occured')