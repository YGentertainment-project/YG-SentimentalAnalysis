import pymongo
import sshtunnel

from .apikey import *

class MongoDBPipelines:
    BUF_SIZE = 300
    def __init__(self) -> None:
        super().__init__()
        if SSH_ENABLE:
            self.tunnel = sshtunnel.SSHTunnelForwarder(
                (SSH_HOST, SSH_PORT),
                ssh_username=SSH_USER,
                ssh_password=SSH_PSWD,
                remote_bind_address=('127.0.0.1', 27017),
                local_bind_address=('0.0.0.0', MONGO_PORT)
            )
            self.tunnel.start()
            connection = pymongo.MongoClient(f'mongodb://{MONGO_USER}:{MONGO_PSWD}@127.0.0.1:{MONGO_PORT}')
        else:
            connection = pymongo.MongoClient(f'mongodb://{MONGO_USER}:{MONGO_PSWD}@{MONGO_ADDR}:{MONGO_PORT}')
        self.db = connection[MONGO_DB]
        self.buffer = {}
    def process_item(self, item, spider):
        if spider.name not in self.buffer:
            self.buffer[spider.name] = []
        self.buffer[spider.name].append(dict(item))
        
        if len(self.buffer[spider.name]) == self.BUF_SIZE:
            self.db[spider.name].insert_many(self.buffer[spider.name])
            del self.buffer[spider.name]
        return item
    
    def close_spider(self, spider):
        for key in self.buffer:
            self.db[key].insert_many(self.buffer[key])
        if SSH_ENABLE:
            self.tunnel.stop()