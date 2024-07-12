from pydantic import BaseModel


class Base(BaseModel):  # Unit
    attack: int
    health: int
    id: str
    isHead: bool
    lastAttack: str = None
    range: int
    x: int
    y: int


class Player(BaseModel):  # Unit
    enemyBlockKills: int
    gameEndedAt: str = None
    gold: int = None
    name: str
    points: int
    zombieKills: int


class Zombies(BaseModel):  # Unit
    attack: int
    direction: str
    health: int
    id: str
    speed: int
    type: str
    waitTurns: int
    x: int
    y: int


class Zpots(BaseModel):  # World
    type: str
    x: str
    y: str


{
    "base": None,
    "enemyBlocks": None,
    "player": {
        "enemyBlockKills": 0,
        "gameEndedAt": "2024-07-12T16:45:56.464926635Z",
        "gold": 10,
        "name": "ГомЛомНом",
        "points": 0,
        "zombieKills": 0,
    },
    "realmName": "test-day1-3",
    "turn": 184,
    "turnEndsInMs": 1425,
    "zombies": None,
}


class Units(BaseModel):
    base: Base
    enemyBlocks: None
    player: Player
    zombies: list[Zombies]
    zpots: list[Zpots]
    realmName: str
    turn: int
    turnEndsInMs: int
