from config import redis_conn

def has_fileid(file_id):
    return redis_conn.sismember("fileids", file_id)

def add_fileid(file_id):
    redis_conn.sadd("fileids", file_id)

def get_filename_by_id(file_id):
    return redis_conn.get("{0}:filename".format(file_id))

def set_filename_with_id(file_id, filename):
    return redis_conn.set("{0}:filename".format(file_id), filename)

def is_children(file_id, serial):
    return redis_conn.sismember("{0}:children".format(file_id), serial)

def add_children(file_id, serial):
    redis_conn.sadd("{0}:children".format(file_id), serial)

def get_fileids():
    return redis_conn.smembers("fileids")

def sort_children_by_id(file_id):
    return redis_conn.sort("{0}:children".format(file_id))
