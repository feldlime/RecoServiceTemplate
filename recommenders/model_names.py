from enum import Enum

class ModelName(str, Enum):
    range = "range"
    popular = "popular"
    userknn = "userknn"
    other = "unknown"