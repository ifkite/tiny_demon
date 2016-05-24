from tornado.options import define
import redis

define("port", default=8080, help="run on the given port", type=int)
define("host", default="0.0.0.0", help="listen the given host", type=str)
define("basedir", default="/tmp", help="root path of upload files", type=str)
define("baseurl", default="localhost", help="base host url", type=str)
define("processes", default=8, help="multi fork processes number", type=int)
define("buf_size", default=4096, help="buffer size of readiing file", type=int)
define("chunk_size", default=4096*1024, help="buffer size of readiing file", type=int)

# redis connection
REDIS_HOST = '127.0.0.1'
redis_conn = redis.Redis(host=REDIS_HOST)
