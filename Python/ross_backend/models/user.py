from db import db


class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    password = db.Column(db.String(80))
    project = db.relationship('ProjectModel', backref='user', cascade="all,delete,delete-orphan")
    # projects = db.relationship('ProjectModel', back_populates="user")
    # raw = db.relationship('RawModel', lazy='dynamic')

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def json(self):
        # return {
        #     'id': self.id,
        #     'username': self.username
        # }
        return {'name': self.username, 'projects': [project.json() for project in self.projects.all()]}

    def get_id(self):
        return int(self.id)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

        
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()