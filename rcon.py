import select
import socket
import ssl
import struct
import time

import database
import modules
from WT import WORLD_TELEPOINT
from auth import getUid


class MCRconException(Exception):
    pass


class MCRcon(object):
    """Minecraft服务端远程命令（RCON）模板
	老咩友情提醒您：
		道路千万条，
		规范第一条。
		写码不规范，
		维护两行泪。
    推荐你使用python的'with'语句！
    这样可以确保及时的关闭连接，而不是被遗漏。
    'with'语句例子:
    In [1]: from mcrcon import MCRcon
    In [2]: with MCRcon("这是一个ip", "这是rcon的密码","这是Rcon的端口" ) as mcr:
       ...:     resp = mcr.command("/发送给服务端的指令")
       ...:     print(resp) #输出

	两行泪方式:
	你当然也可以不用python的'with'语句，但是一定要在建立连接后，及时的断开连接。
    In [3]: mcr = MCRcon("这是一个ip", "这是rcon的密码","这是Rcon的端口" )
    In [4]: mcr.connect() #连接建立
    In [5]: resp = mcr.command("/发送给服务端的指令")
    In [6]: print(resp) #输出
    In [7]: mcr.disconnect() #断开连接
    """
    socket = None

    # 重写init方法
    def __init__(self, host, port, password, tlsmode=0):
        self.host = host
        self.password = password
        self.port = port
        self.tlsmode = tlsmode

    def __exit__(self, type, value, tb):
        self.disconnect()

    def __enter__(self):
        self.connect()
        return self

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # 打开 TLS
        if self.tlsmode > 0:
            ctx = ssl.create_default_context()

            # 禁用主机名和证书验证
            if self.tlsmode > 1:
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE

            self.socket = ctx.wrap_socket(self.socket, server_hostname=self.host)

        self.socket.connect((self.host, self.port))
        self._send(3, self.password)

    def _read(self, length):
        data = b""
        while len(data) < length:
            data += self.socket.recv(length - len(data))
        return data

    def disconnect(self):
        if self.socket is not None:
            self.socket.close()
            self.socket = None

    def _send(self, out_type, out_data):
        if self.socket is None:
            raise MCRconException("发送前必须连接！")

        # 发送请求包
        out_payload = struct.pack('<ii', 0, out_type) + out_data.encode('utf8') + b'\x00\x00'
        out_length = struct.pack('<i', len(out_payload))
        self.socket.send(out_length + out_payload)

        # 读取响应包
        in_data = ""
        while True:
            # 读取数据包
            in_length, = struct.unpack('<i', self._read(4))
            in_payload = self._read(in_length)
            in_id, in_type = struct.unpack('<ii', in_payload[:8])
            in_data_partial, in_padding = in_payload[8:-2], in_payload[-2:]

            # 异常处理
            if in_padding != b'\x00\x00':
                raise MCRconException("Incorrect padding")
            if in_id == -1:
                raise MCRconException("登录rcon协议失败")

            in_data += in_data_partial.decode('utf8')

            if len(select.select([self.socket], [], [], 0)[0]) == 0:
                return in_data

    def command(self, command):
        result = self._send(2, command)
        time.sleep(0.003)  # MC-72390 （非线程安全的解决办法）
        return result


SPAWN_POINT = "-78 64 -207"


def getOnlinePlayers():
    with MCRcon("127.0.0.1", 25575, "root") as mcr:
        resp = mcr.command("/list")
        p_list = resp[resp.find(":") + 2:].split(", ")
        online_count = resp[10:resp.find(" of a max of 99 players online")]

    return {
        "online_list": p_list,
        "online_count": online_count,
    }


def setHome(player):
    if player is None:
        return {"msg": "? id ne ?", "suc": False}
    if not __onlineCheck(player):
        return {"msg": "玩家不在线", "suc": False}
    if getUid() != player:
        return {"msg": "Context异常", "suc": False}
    pos, dim = __getPlayerPos(player)
    try:
        row = modules.User.query.get(player)
        row.home_pos = str(pos)[1:-1].replace(",", "")
        row.home_dim = dim
        database.db.session.commit()
    except Exception as e:
        return {"msg": e, "suc": False}
    __tell(player, f"设置Home到 {pos}({dim}).")
    return {"msg": f"Set home to {pos}({dim}).", "suc": True}


def home(player):
    if player is None:
        return {"msg": "? id ne ?", "suc": False}
    if not __onlineCheck(player):
        return {"msg": "玩家不在线", "suc": False}
    if getUid() != player:
        return {"msg": "Context异常", "suc": False}
    home_pos = modules.User.query.get(player).home_pos
    home_dim = modules.User.query.get(player).home_dim
    resp = __tp(player, home_pos, dimension=home_dim)
    if "No entity was found" in resp:
        return {"msg": resp, "suc": False}
    return {"msg": resp, "suc": True}


def spawn(player):
    if player is None:
        return {"msg": "? id ne ?", "suc": False}
    if not __onlineCheck(player):
        return {"msg": "玩家不在线", "suc": False}
    if getUid() != player:
        return {"msg": "Context异常", "suc": False}
    resp = __tp(player, SPAWN_POINT)
    if "No entity was found" in resp:
        return {"msg": resp, "suc": False}
    return {"msg": resp, "suc": True}


def tpSp(player, sp):
    if player is None:
        return {"msg": "? id ne ?", "suc": False}
    if not __onlineCheck(player):
        return {"msg": "玩家不在线", "suc": False}
    if getUid() != player:
        return {"msg": "Context异常", "suc": False}
    if sp not in ["save1", "save2"]:
        return {"msg": "Unknown save point.", "suc": False}
    pos = None
    dim = None
    if sp == "save1":
        pos = modules.User.query.get(player).SavePoint[0].save1_pos
        dim = modules.User.query.get(player).SavePoint[0].save1_dim
    elif sp == "save2":
        pos = modules.User.query.get(player).SavePoint[0].save2_pos
        dim = modules.User.query.get(player).SavePoint[0].save2_dim

    resp = __tp(player, pos, dim)
    if "No entity was found" in resp:
        return {"msg": resp, "suc": False}
    return {"msg": resp, "suc": True}


def setSp(player, sp):
    if player is None:
        return {"msg": "? id ne ?", "suc": False}
    if not __onlineCheck(player):
        return {"msg": "玩家不在线", "suc": False}
    if getUid() != player:
        return {"msg": "Context异常", "suc": False}
    if sp not in ["save1", "save2"]:
        return {"msg": "Unknown save point.", "suc": False}
    pos, dim = __getPlayerPos(player)
    pos = str(pos)[1:-1].replace(",", "")
    try:
        row = modules.SavePoint.query.get(player)
        if sp == "save1":
            row.save1_pos = pos
            row.save1_dim = dim
            database.db.session.commit()
        elif sp == "save2":
            row.save2_pos = pos
            row.save2_dim = dim
            database.db.session.commit()
    except Exception as e:
        print(e)
        return {"msg": e, "suc": False}
    __tell(player, f"设置{sp}到 {pos}({dim}).")
    return {"msg": f"Set {sp} to {pos}({dim}).", "suc": True}


def tpWt(player, wt):
    if player is None:
        return {"msg": "? id ne ?", "suc": False}
    if not __onlineCheck(player):
        return {"msg": "玩家不在线", "suc": False}
    if getUid() != player:
        return {"msg": "Context异常", "suc": False}
    if wt not in WORLD_TELEPOINT:
        return {"msg": "Unknown Wt", "suc": False}
    resp = __tp(player, WORLD_TELEPOINT[wt]["pos"], WORLD_TELEPOINT[wt]["dim"])
    if "No entity was found" in resp:
        return {"msg": resp, "suc": False}
    return {"msg": resp, "suc": True}


def tpPlayer(player, target_player):
    if player is None:
        return {"msg": "? id ne ?", "suc": False}
    if not __onlineCheck(player):
        return {"msg": "玩家不在线", "suc": False}
    if getUid() != player:
        return {"msg": "Context异常", "suc": False}
    resp = __tp(player, target_player)
    if modules.User.query.get(target_player) is None:
        return {"msg": "Unknown target", "suc": False}
    if "No entity was found" in resp:
        return {"msg": resp, "suc": False}
    return {"msg": resp, "suc": True}


def __onlineCheck(player):
    p_list = getOnlinePlayers()["online_list"]
    return player in p_list


def __tell(player, msg):
    with MCRcon("127.0.0.1", 25575, "root") as mcr:
        resp = mcr.command(f"/tell {player} {msg}")
        return resp


def __tp(player, target, dimension="minecraft:overworld"):
    with MCRcon("127.0.0.1", 25575, "root") as mcr:
        resp = mcr.command(f"/execute in {dimension} run tp {player} {target}")
        return resp


def __getPlayerPos(player):
    with MCRcon("127.0.0.1", 25575, "root") as mcr:
        resp = mcr.command(f"/data get entity {player} Pos")
        pos_list = resp[resp.find("the following entity data: ") + 27:].split(", ")
        pos_list[0] = round(float(pos_list[0][1:-1]), 2)
        pos_list[1] = round(float(pos_list[1][:-1]), 2)
        pos_list[2] = round(float(pos_list[2][:-2]), 2)
        resp = mcr.command(f"/data get entity {player} Dimension")
        dim = resp[resp.find("the following entity data: ") + 28:-1]
        return pos_list, dim


if __name__ == '__main__':
    # print("No entity was found" in spawn("Nyanki")['msg'])
    # print("SPAWN" in WORLD_TELEPOINT)
    print(__onlineCheck("Nyanki"))
