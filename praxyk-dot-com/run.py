#!/usr/bin/python
from app import app
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

http_server = HTTPServer(WSGIContainer(app))
http_server.listen(int(5000))
IOLoop.instance().start()

# app.run(debug=True)
