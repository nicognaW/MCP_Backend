import database


class User(database.db.Model):
    uid = database.db.Column(database.db.String(18), primary_key=True)
    pwd = database.db.Column(database.db.String(18))
    home_pos = database.db.Column(database.db.String(50), default="-78 64 -207")
    home_dim = database.db.Column(database.db.String(50), default="minecraft:overworld")


class SavePoint(database.db.Model):
    uid = database.db.Column(database.db.String(18), database.db.ForeignKey('user.uid'),  primary_key=True)
    user = database.db.relationship("User", backref=database.db.backref('SavePoint'))
    save1_pos = database.db.Column(database.db.String(50), default="-78 64 -207")
    save1_dim = database.db.Column(database.db.String(50), default="minecraft:overworld")
    save2_pos = database.db.Column(database.db.String(50), default="-78 64 -207")
    save2_dim = database.db.Column(database.db.String(50), default="minecraft:overworld")
