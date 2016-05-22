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

reload(sys)
sys.setdefaultencoding("utf-8")

class UploadHandler(tornado.web.RequestHandler):

    def get(self):
        self.render("upload.html")

    def post(self):
        # # file handler
        filename = self.request.headers.get('Filename')
        filebody = self.request.body
        # no file uploaded
        if not filename:
            # upload file in root of mfs is not allowed
            raise tornado.web.HTTPError(403)

        # save_path = os.path.join(options.basedir, filepath)
        # if not os.path.exists(save_path):
            # os.makedirs(save_path)

        save_file = os.path.join(options.basedir, filename)

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
