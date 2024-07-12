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
