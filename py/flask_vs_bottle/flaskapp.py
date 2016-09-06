from gevent import monkey
monkey.patch_all()
from flask import Flask
from gevent import wsgi


app = Flask(__name__)

@app.route('/')
def index():
  return 'Hello World'

server = wsgi.WSGIServer(('127.0.0.1', 5000), application=app, log=None)
server.serve_forever()
