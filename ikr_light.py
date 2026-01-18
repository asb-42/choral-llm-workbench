from dataclasses import dataclass
from typing import Union, Optional, Dict, Any
from fractions import Fraction


@dataclass
class NoteEvent:
    onset: Fraction
    duration: Fraction
    pitch_step: str  # A–G
    pitch_alter: int  # -1, 0, 1
    octave: int
    tie: Optional[str] = None  # "start" | "stop" | None


@dataclass
class RestEvent:
    onset: Fraction
    duration: Fraction


@dataclass
class HarmonyEvent:
    onset: Fraction
    harmony: str
    key: Optional[str] = None  # Optional key context (e.g., "E minor")


@dataclass
class LyricEvent:
    onset: Fraction
    text: str


Event = Union[NoteEvent, RestEvent, HarmonyEvent, LyricEvent]


@dataclass
class Measure:
    number: int
    time_signature: str
    events: list[Event]


@dataclass
class Voice:
    id: str
    measures: list[Measure]


@dataclass
class Part:
    id: str
    name: str
    role: str  # "choir" | "instrument"
    voices: list[Voice]


@dataclass
class Score:
    metadata: Dict[str, Any]
    parts: list[Part]