"""User Settings.
TODO: Implement/integrate this module
"""

from collections import ChainMap

default_settings: dict[str, str | bool] = {
    "file_format": "yaml",
    "theme": "dark",
    "language": "English",
    "notifications": True
}

user_preferences: dict[str, str | bool] = {
    "theme": "light",
    "language": "Spanish",
    "notifications": False
}

preferences: ChainMap[str, str | bool] = ChainMap(user_preferences, default_settings)
