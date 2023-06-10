from app import app
from flask_sqlalchemy import SQLAlchemy

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///questions_and_answers.db"
db = SQLAlchemy(app)
    
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=True)
    username = db.Column(db.String(200), unique=True)
    password = db.Column(db.String(200), nullable=True)
    expert = db.Column(db.Boolean, default=False)
    admin = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return '<User %r>' % self.id

class Questions(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question = db.Column(db.String(500))
    answer = db.Column(db.String(1000))
    question_by_id = db.Column(db.Integer)
    answer_by_id = db.Column(db.Integer)
    
    def __repr__(self):
        return '<Question %r>' % self.id
    
