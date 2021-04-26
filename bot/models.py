from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from bot.states import UserState


@dataclass
class User:
    tg_id: str
    username: str = None
    name: str = None
    university: str = None
    peers_met: str = None
    is_graduate: bool = False
    cross_meet: bool = False
    frequency_weekly: int = 1
    state: UserState = UserState.go
