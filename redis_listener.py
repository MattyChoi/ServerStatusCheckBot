from dotenv import load_dotenv
import json
import os
from redis import Redis
import threading

from models import CoreServer, MiniProfile

class RedisListener():
    def __init__(self) -> None:
        load_dotenv()
        
        # Redis Setup
        redis_host = os.getenv("REDIS_HOST")
        redis_port = os.getenv("REDIS_PORT")

        # subscribe to the desired
        r = Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.p = r.pubsub()
        # use .subscribe() method to subscribe to topic on which you want to listen for messages
        self.p.subscribe(os.getenv("REDIS_CHANNEL"))
        
        self.servers = {}
        
        self.servers_lock = threading.Lock()
        
    
    def get_servers(self):
        self.servers_lock.acquire()
        servers = self.servers
        self.servers_lock.release()
        return servers
    
    def update_online_status(self, server_name: str, online: bool):
        self.servers_lock.acquire()
        self.servers[server_name].currently_online = online
        self.servers_lock.release()
    

    def redis_listener(self):
        print("Starting listener")
        for msg in self.p.listen():
            if msg["type"] != "message":
                continue
            msg = json.loads(msg["data"])
            
            self.servers_lock.acquire()
            
            if msg["name"] not in self.servers:
                self.servers[msg["name"]] = CoreServer(
                    name=msg["name"],
                    type=msg["type"],
                    # players=msg.players,
                    slots=msg["slots"],
                    last_update=msg["last_update"],
                    uptime=msg["uptime"],
                    currently_online=True,
                )
            else:
                name = msg["name"]
                # self.servers[msg.name].players = msg.players
                self.servers[name].last_update = msg["last_update"]
                self.servers[name].uptime = msg["uptime"]
                self.servers[name].currently_online = True
                
            self.servers_lock.release()
                
    def start_listener(self):
        thread = threading.Thread(target=self.redis_listener)
        thread.daemon = True
        thread.start()
        