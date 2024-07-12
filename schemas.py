from typing import Optional

from pydantic import BaseModel


class Base(BaseModel):  # Unit
    attack: Optional[int]
    health: Optional[int]
    id: Optional[str]
    isHead: Optional[bool]
    lastAttack: Optional[str] = None
    range: Optional[int]
    x: Optional[int]
    y: Optional[int]


class Player(BaseModel):  # Unit
    enemyBlockKills: Optional[int]
    gameEndedAt: Optional[str] = None
    gold: Optional[int] = None
    name: Optional[str]
    points: Optional[int]
    zombieKills: Optional[int]


class Zombies(BaseModel):  # Unit
    attack: Optional[int]
    direction: Optional[str]
    health: Optional[int]
    id: Optional[str]
    speed: Optional[int]
    type: Optional[str]
    waitTurns: Optional[int]
    x: Optional[int]
    y: Optional[int]


class Zpots(BaseModel):  # World
    type: Optional[str]
    x: Optional[str]
    y: Optional[str]


class World(BaseModel):
    realmName: Optional[str]
    zpots: list[Zpots]


class Units(BaseModel):
    base: Optional[Base]
    enemyBlocks: Optional[None]
    player: Optional[Player]
    zombies: Optional[list[Zombies]]
    zpots: Optional[list[Zpots]]
    realmName: Optional[str]
    turn: Optional[int]
    turnEndsInMs: Optional[int]
