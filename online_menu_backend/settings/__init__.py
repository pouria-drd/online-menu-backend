from .env_config import ONLINE_MENU_STAGE


if ONLINE_MENU_STAGE == "production":
    from .production import *
else:
    from .development import *
