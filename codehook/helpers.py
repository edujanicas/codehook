from enum import Enum

class Source(str, Enum):
    stripe = "stripe"

class Events(str, Enum):
    all = "*"
