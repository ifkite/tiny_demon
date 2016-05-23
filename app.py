#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import logging
import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado.options import define, options
from tornado.web import URLSpec

from handlers.file import UploadHandler
from handlers.file import DownloadHandler

define("port", default=8080, help="run on the given port", type=int)
define("host", default="0.0.0.0", help="listen the given host", type=str)
define("basedir", default="/tmp", help="root path of upload files", type=str)
define("baseurl", default="localhost", help="base host url", type=str)
define("processes", default=8, help="multi fork processes number", type=int)
define("buf_size", default=4096, help="buffer size of readiing file", type=int)
define("chunk_size", default=4096*1024, help="buffer size of readiing file", type=int)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            URLSpec(r"/upload/", UploadHandler, name='upload'),
            URLSpec(r"/download/([^/]+)?", DownloadHandler, name='download'),
        ]

        settings = {
            "template_path": os.path.join(os.path.dirname(__file__), "templates"),
            "static_path": os.path.join(os.path.dirname(__file__), "static"),
            "debug": True,
        }

        tornado.web.Application.__init__(self, handlers, **settings)


def main():
    tornado.options.parse_command_line()
    sockets = tornado.netutil.bind_sockets(port=options.port, address=options.host)
    # tornado.process.fork_processes(options.processes)
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.add_sockets(sockets)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
