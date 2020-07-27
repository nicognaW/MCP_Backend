import flask
from flask import abort
from flask_restful import Resource
from flask_restful import reqparse

import auth
import rcon

__all__ = [
    # Auth Api
    "Login", "Logout", "Logcheck",
    # Rcon Api
    "GetOnlinePlayers", "SetHome", "Home", "Spawn", "Tp"
]


class Login(Resource):
    """
    @url /login
    @:param
    {
        uid: "USER ID"
        pwd: "USER PASSWORD"
    }
    @:return
    {
        msg: "MESSAGE"
        suc: TRUE IF LOGIN IS SUCCEED
    }
    """

    def get(self):
        abort(404)

    def post(self) -> dict:
        if auth.auth_check():
            return {
                "msg": "Already logged in",
                "suc": True
            }

        parser = reqparse.RequestParser()
        parser.add_argument('uid', type=str)
        parser.add_argument('pwd', type=str)
        args = parser.parse_args()
        msg = auth.login(args["uid"], args["pwd"])
        return {
            "msg": msg[0],
            "suc": msg[1],
        }


class Logout(Resource):
    """
    @url /logout
    @:param {}(void)
    @return
    {
        msg: "MESSAGE"
        suc: TRUE IF LOGOUT IS SUCCEED
    }
    """

    def get(self):
        abort(404)

    def post(self):
        if not auth.auth_check():
            return {
                "msg": "Not logged in.",
                "suc": False
            }
        auth.logout()
        return {
            "msg": "Logout successfully.",
            "suc": True,
        }


class Logcheck(Resource):
    def post(self):
        if auth.auth_check():
            return {
                "msg": "Already logged in",
                "uid": flask.session['uid'],
                "suc": True
            }
        else:
            return {
                "msg": "Not logged in",
                "suc": False
            }


class GetOnlinePlayers(Resource):
    def get(self):
        return rcon.getOnlinePlayers()


class SetHome(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('uid', type=str)
        args = parser.parse_args()
        uid = args['uid']
        return rcon.setHome(uid)


class Home(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('uid', type=str)
        args = parser.parse_args()
        uid = args['uid']
        return rcon.home(uid)


class Spawn(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('uid', type=str)
        args = parser.parse_args()
        uid = args['uid']
        return rcon.spawn(uid)


class Tp(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('uid', type=str)
        parser.add_argument('target_uid', type=str)
        args = parser.parse_args()
        uid = args['uid']
        target_uid = args['target_uid']
        return rcon.tpPlayer(uid, target_uid)


class Wt(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('uid', type=str)
        parser.add_argument('wt', type=str)
        args = parser.parse_args()
        uid = args['uid']
        wt = args['wt']
        return rcon.tpWt(uid, wt)


class Sp(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('uid', type=str)
        parser.add_argument('sp', type=str)
        args = parser.parse_args()
        uid = args['uid']
        sp = args['sp']
        return rcon.tpSp(uid, sp)


class SetSp(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('uid', type=str)
        parser.add_argument('sp', type=str)
        args = parser.parse_args()
        uid = args['uid']
        sp = args['sp']
        return rcon.setSp(uid, sp)
