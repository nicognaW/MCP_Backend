from database import db
from server import app
from modules import User, SavePoint

db.init_app(app)
db.app = app

row = SavePoint.query.get("Nyanki")
row.save1_pos = "tes1t"
db.session.commit()