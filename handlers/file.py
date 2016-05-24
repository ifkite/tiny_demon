#! encoding=utf-8
import os
import shutil
import sys
import logging
import re
from hashlib import md5
from requests import Request, Session
import tornado.web
from tornado.options import options
from tornado.escape import json_encode
from os import listdir
from os.path import isfile, join

from config import redis_conn

reload(sys)
sys.setdefaultencoding("utf-8")

class UploadHandler(tornado.web.RequestHandler):

    def get(self):
        self.render("upload.html")

    def post(self):
        filename = self.request.headers.get('Filename')
        file_id = self.request.headers.get('Fileid')
        serial = self.request.headers.get('Serial')

        filebody = self.request.body
        # no file uploaded
        if not (filename and file_id and serial):
            # upload file in root of mfs is not allowed
            raise tornado.web.HTTPError(403)

        if not redis_conn.sismember("fileids", file_id):
            redis_conn.sadd("fileids", file_id)

        if not redis_conn.get("{0}:filename".format(file_id)):
            redis_conn.set("{0}:filename".format(file_id), filename)

        if not redis_conn.sismember("{0}:child".format(file_id), serial):
            redis_conn.sadd("{0}:child".format(file_id), serial)

        file_dir = os.path.join(options.basedir, filename)
        if not os.path.isdir(file_dir):
            os.makedirs(file_dir)

        sliced_filename = "{0}:{1}".format(file_id, serial)

        save_file = os.path.join(file_dir, sliced_filename)

        # TODO 1.write in chuncks
        #      2.async
        with open(save_file, "w") as fp:
            fp.write(filebody)
        self.write({'success': True})

class DownloadHandler(tornado.web.RequestHandler):
    def get(self, filename=None):
        files = [f for f in listdir(options.basedir) if isfile(join(options.basedir, f))]
        if not filename:
            self.render('download.html', files=files)
        else:
            # download file
            if filename in files:
                self.set_header('Content-Type', 'application/force-download')
                self.set_header('Content-Disposition', 'attachment; filename={0}'.format(filename))

                _filepath = os.path.join(options.basedir, filename)
                with open(_filepath, "rb") as f:
                    try:
                        while True:
                            _buffer = f.read(options.buf_size)
                            if _buffer:
                                self.write(_buffer)
                            else:
                                f.close()
                                self.finish()
                                return
                    except:
                        # TODO error handling
                        raise tornado.web.HttpError(404)
            else:
                # TODO error handling
                raise tornado.web.HttpError(404)
