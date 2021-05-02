from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from datetime import datetime

from bot.states import UserState


@dataclass
class User:
    tg_id: str
    username: str = None
    name: str = None
    university: str = None
    peers_met: str = None
    is_graduate: bool = None
    grad_year: int = None
    payment_pending: bool = None
    frequency: int = None
    frequency_updated: datetime = None
    state: UserState = UserState.go
