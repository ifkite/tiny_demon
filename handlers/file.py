#! encoding=utf-8
import os
import sys
import tornado.web
from tornado.options import options

import utils
from config import redis_conn

reload(sys)
sys.setdefaultencoding("utf-8")

class UploadHandler(tornado.web.RequestHandler):

    def get(self):
        self.render("upload.html")

    def post(self):
        if self.request.files:
            filebody = self.request.files[options.fname][0].body
            filename = self.request.files[options.fname][0].filename
            if (not filebody) or (not filename):
                raise tornado.web.HTTPError(403)
        else:
            raise tornado.web.HTTPError(403)

        # TODO post in form
        file_id = self.get_body_argument('Fileid')
        serial = self.get_body_argument('Serial')

        if not (file_id and serial):
            raise tornado.web.HTTPError(403)

        if not utils.has_fileid(file_id):
            utils.add_fileid(file_id)

        if not utils.get_filename_by_id(file_id):
            utils.set_filename_with_id(file_id, filename)

        if not utils.is_children(file_id, serial):
            utils.add_children(file_id, serial)

        file_dir = os.path.join(options.basedir, filename)
        if not os.path.isdir(file_dir):
            os.makedirs(file_dir)

        sliced_filename = "{0}:{1}".format(file_id, serial)

        save_file = os.path.join(file_dir, sliced_filename)

        # TODO 1.write in chuncks:DONE
        #      2.async
        # in fact, when `redis_conn.sismember("{0}:child".format(file_id), serial)` is True
        # we do not need to write file
        with open(save_file, "wb") as file_write:
            file_write.write(filebody)
        self.write({'success': True})

class DownloadHandler(tornado.web.RequestHandler):
    def get(self, fileid=None):
        fileids = utils.get_fileids()
        files = {fileid: utils.get_filename_by_id(fileid) for fileid in fileids}
        if not fileid:
            self.render('download.html', files=files)
        else:
            # download file
            if fileid in files:
                filename = files.get(fileid)
                self.set_header('Content-Type', 'application/force-download')
                self.set_header('Content-Disposition', 'attachment; filename={0}'.format(filename))

                # NEED SOME MODIFICATION
                # TODO: we should `remember` that we sorted that set
                # even more, we can avoid sort operation if we known the chunk length
                # who are us? we are the servers ;)
                sliced_files_serial = redis_conn.sort("{0}:children".format(fileid))
                sliced_files_name = ["{0}:{1}".format(fileid, serial) for serial in sliced_files_serial]
                file_dir = os.path.join(options.basedir, filename)

                for sliced_file_child in sliced_files_name:
                    sliced_child_path = os.path.join(file_dir, sliced_file_child)
                    with open(sliced_child_path, "rb") as file_read:
                        while True:
                            buffer = file_read.read(options.buf_size)
                            if buffer:
                                self.write(buffer)
                            else:
                                break
                self.finish()
            else:
                # TODO error handling
                raise tornado.web.HttpError(404)
