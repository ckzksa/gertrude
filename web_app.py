from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Gertrude"

def run():
  app.run(host='0.0.0.0', port=8080)

def start_thread():
    t = Thread(target=run)
    t.daemon = True
    t.start()

if __name__ == "__main__":
  run()
