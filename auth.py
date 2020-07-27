import logging

from flask import session
from markupsafe import escape

import modules

logger = logging.getLogger("auth.py")


def auth_check() -> bool:
    if 'uid' in session:
        logger.debug(f"Auth check is succeed")
        return True
    logger.warning(f"Auth check is failed")
    return False


def getUid() -> str or None:
    if auth_check():
        return session['uid']
    else:
        return None


def login(uid, pwd) -> (str, bool):
    res = modules.User.query.get(uid)
    if res is None:
        logger.warning(f"Someone tried to use id \"{uid}\" to login.")
        return f"{uid} is not registered", False

    if res.pwd != pwd:
        logger.warning(f"Someone tried to use wrong pwd \"{pwd}\" to login with id \"{uid}\".")
        return "Wrong password.", False

    logger.debug(f"User \"{uid}\" authenticated with pwd \"{pwd}\" in successfully.")

    session["uid"] = uid

    if 'uid' in session:
        logger.debug(f"User \"{uid}\" logged in with pwd \"{pwd}\" in successfully.")
        return '%s is logged in.' % escape(session['uid']), True
    logger.warning(f"Login of \"{uid}\" with pwd \"{pwd}\" failed.")
    return 'Login failed for unknown reason, please try it later.', False


def logout():
    logger.debug(f"Session {session} logged out.")
    session.pop("uid")
