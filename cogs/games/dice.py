import discord
import asyncio
import logging
import re
import random

from discord_components import Button, ButtonStyle

log = logging.getLogger(__name__)

class Dice():
  number_to_emoji = {
    '0': '<:zero:902233086761250886>',
    '1': '<:one:902233086761250886>',
    '2': '<:two:902233086761250886>',
    '3': '<:three:902233086761250886>',
    '4': '<:four:902233227744391178>',
    '5': '<:five:902233227744391178>',
    '6': '<:six:902233227744391178>',
    '7': '<:seven:902233227744391178>',
    '8': '<:eight:902233227744391178>',
    '9': '<:nine:902233227744391178>',
  }

  def __init__(self, bot, ctx, dice: int) -> None:
    self.bot = bot
    self.ctx = ctx
    self.dice = dice
  
  async def play(self):
    try:
      if re.search('^[dD][0-9]+', self.dice) is not None:
        dice = self.dice[1:]
      value = random.randint(1, int(dice))

      str = ''
      for digit in str(value):
        str += self.number_to_emoji[digit]
      await self.ctx.send(str)
    except ValueError as e:
      log.error(e)
      await self.ctx.send(content=f'It ain\'t a number #nobrain')
    except Exception as e:
      log.error(e)
      await self.ctx.send(content=f'Oooops an error occured')