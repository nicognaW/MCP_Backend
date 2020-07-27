import os
import sys

from flask import Flask
from flask_restful import Api

from database import db
from resources import *

__all__ = ["app", "api", "isWin", "logger"]

from resources import Wt, Sp, SetSp

isWin = sys.platform.startswith('win')
if isWin:  # 如果是 Windows 系统，使用三个斜线
    prefix = 'sqlite:///'
else:  # 否则使用四个斜线
    prefix = 'sqlite:////'

app = Flask("app")
api = Api(app)
logger = app.logger

app.secret_key = "19970401np"

app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控
db.init_app(app)


def dbInit(drop=False):
    """Initialize the database."""
    if drop:
        db.drop_all()
    db.create_all(app=app)
    logger.debug("Database initialized")


# ROOT URL SHOULD START AND END WITH /
root_url = '/'

api.add_resource(Login, root_url + 'login')
api.add_resource(Logout, root_url + 'logout')
api.add_resource(Logcheck, root_url + 'logcheck')
api.add_resource(GetOnlinePlayers, root_url + 'getonlineplayers')
api.add_resource(SetHome, root_url + "sethome")
api.add_resource(Home, root_url + "home")
api.add_resource(Spawn, root_url + "spawn")
api.add_resource(Tp, root_url + "tp")
api.add_resource(Wt, root_url + "wt")
api.add_resource(Sp, root_url + "sp")
api.add_resource(SetSp, root_url + "setsp")
