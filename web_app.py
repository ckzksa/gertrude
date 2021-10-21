import logging
import click

from flask import Flask
from threading import Thread

def secho(text, file=None, nl=None, err=None, color=None, **styles):
  pass

def echo(text, file=None, nl=None, err=None, color=None, **styles):
  pass

click.echo = echo
click.secho = secho

log_flask = logging.getLogger('werkzeug')
log_flask.setLevel(logging.ERROR)

log = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def home():
    return "Gertrude"

def run():
  app.run(host='0.0.0.0', port=8080, debug=False)

def start():
  log.info('Starting thread web server')
  web_app_thread = Thread(target=run)
  web_app_thread.setDaemon(True)
  web_app_thread.start()
  log.info('Web server started')
    

if __name__ == "__main__":
  run()
