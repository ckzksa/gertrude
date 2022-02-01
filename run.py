import os
import json
import web.web_app as web
import logging

from logging.config import dictConfig
from gertrude import bot
log_config_filename = 'log_config.json'

log = logging.getLogger(__name__)
if os.path.isfile(log_config_filename):
  with open(log_config_filename) as file:
    log_config = json.load(file)
    dictConfig(log_config)

if __name__ == "__main__":
  web.start()
  bot = bot.Bot()
  bot.launch()
