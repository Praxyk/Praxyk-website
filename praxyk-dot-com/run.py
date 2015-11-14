#!flask/bin/python3
from app import app
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
import sys

if len(sys.argv) > 1 :
    if sys.argv[1] == "--local" :
        app.run(debug=True)
else :
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(int(5000))
    IOLoop.instance().start()

