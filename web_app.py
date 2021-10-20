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

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)

@app.route('/')
def home():
    return "Gertrude"

def run():
  app.run(host='0.0.0.0', port=8080, debug=False)

def start():
  print('Starting thread web server')
  web_app_thread = Thread(target=run)
  web_app_thread.setDaemon(True)
  web_app_thread.start()
  print('Web server started')
    

if __name__ == "__main__":
  run()
