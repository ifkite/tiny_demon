##tiny_demon: upload/download large files  

1. ###使用  
`git clone https://github.com/ifkite/tiny_demon.git`  
`cd tiny_demon`  
`virtualenv venv`  
`. venv/bin/activate`  
安装 redis  
`pip install -r requirements.txt`  
启动 redis-server  
`python app.py` （占用8080端口）  
上传：[torandohost]:8080/upload/  
下载：[torandohost]:8080/download/  
tornadohost: 跑tornado的host ip.  

2. ###重要配置  
     文件块的大小 chunk_size，数据传输的单位。**默认16M**。可适当向上调整。  
     文件存储位置为 basedir，**默认 /tmp**， 为方便测试。**系统重启后文件会消失**。所以系统重启后要 <code>FLUSHALL redis</code>。  
