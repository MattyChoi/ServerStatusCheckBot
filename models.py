from typing import List, Dict, Optional
from uuid import UUID

from pydantic import BaseModel


class MiniProfile(BaseModel):
    uuid: UUID = ""
    name: str = ''
    server: str = ''
    staff: bool = False
    
    
class CoreServer(BaseModel):
    name: str = ''
    type: str = ''
    players: List[MiniProfile] = []
    slots: int = 0
    last_update: int = 0
    uptime: int = 0
    currently_online: bool = True