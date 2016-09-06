#from gevent import monkey
#monkey.patch_all()
import gevent.pywsgi
import lib.bottle as bottle


app = bottle.Bottle(__name__)

@app.route('/')
def index():
  return 'Hello World'

server = gevent.pywsgi.WSGIServer(('127.0.0.1', 5000), application=app, log=None)
server.serve_forever()