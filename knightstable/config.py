import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    # Configure session to use filesystem (instead of signed cookies)
    SESSION_PERMANENT = False
    SESSION_TYPE = "filesystem"
    # Ensure templates are auto-reloaded
    TEMPLATES_AUTO_RELOAD = True
