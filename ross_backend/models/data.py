from __future__ import annotations

from db import db


class RawModel(db.Model):
    __tablename__ = 'data'

    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String)
    mode = db.Column(db.Integer, default=0)  # 0: client, 1: server
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete="CASCADE"))

    # user = db.relationship('UserModel')
    # project = db.relationship('ProjectModel', backref="raw", lazy=True)

    def __init__(self, user_id, data, project_id, mode):
        self.data = data
        self.mode = mode
        self.user_id = user_id
        self.project_id = project_id

    def json(self):
        return {'data': self.data}

    def save_to_db(self):
        # update or insert
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get(cls):
        return cls.query.first()

    @classmethod
    def find_by_user_id(cls, _id) -> RawModel:
        return cls.query.filter_by(user_id=_id, project_id=0).first()

    @classmethod
    def find_by_project_id(cls, project_id) -> RawModel:
        return cls.query.filter_by(project_id=project_id).first()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()


class DetectResultModel(db.Model):
    __tablename__ = 'detection_result'

    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete="CASCADE"))

    # user = db.relationship('UserModel')
    # project = db.relationship('ProjectModel', backref="raw", lazy=True)

    def __init__(self, user_id, data, project_id):
        self.data = data
        self.user_id = user_id
        self.project_id = project_id

    def json(self):
        return {'data': self.data}

    def save_to_db(self):
        # update or insert
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get(cls):
        return cls.query.first()

    # @classmethod
    # def find_by_user_id(cls, _id):
    #     return cls.query.filter_by(user_id=_id, project_id=0).first()

    @classmethod
    def find_by_project_id(cls, project_id) -> DetectResultModel:
        return cls.query.filter_by(project_id=project_id).first()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()


class SortResultModel(db.Model):
    __tablename__ = 'sorting_result'
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete="CASCADE"))

    # user = db.relationship('UserModel')
    # project = db.relationship('ProjectModel', backref="raw", lazy=True)

    def __init__(self, user_id, data, project_id):
        self.data = data
        self.user_id = user_id
        self.project_id = project_id

    def json(self):
        return {'data': self.data}

    def save_to_db(self):
        # update or insert
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get(cls):
        return cls.query.first()

    # @classmethod
    # def find_by_user_id(cls, _id):
    #     return cls.query.filter_by(user_id=_id, project_id=0).first()

    @classmethod
    def find_by_project_id(cls, project_id) -> SortResultModel:
        return cls.query.filter_by(project_id=project_id).first()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
