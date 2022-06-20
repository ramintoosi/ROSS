from db import db


class ProjectModel(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"))
    config_detect = db.relationship('ConfigDetectionModel', backref='project', uselist=False, cascade="all,delete,delete-orphan")
    config_sort = db.relationship('ConfigSortModel', backref='project', uselist=False, cascade="all,delete,delete-orphan")
    raw = db.relationship('RawModel', backref='project', uselist=False, cascade="all,delete,delete-orphan")
    detection_result = db.relationship('DetectResultModel', backref='project', uselist=False, cascade="all,delete,delete-orphan")
    sorting_result = db.relationship('SortResultModel', backref='project', uselist=False, cascade="all,delete,delete-orphan")
    # user = db.relationship('UserModel', backref="projects", lazy=True)
    # raw = db.relationship('RawModel', back_populates="project")

    def __init__(self, user_id, name=None, isDefault=True):
        self.name = name
        self.user_id = user_id
        if isDefault:
            self.id = 0

    def json(self):
        return {'name': self.name, 'id': self.id}

    def save_to_db(self):
        # update or insert
        db.session.add(self)
        db.session.commit()

    # @classmethod
    # def save_new_to_db(cls, self):
    #     new_project = cls(_id, name, isDefault=False)
    #     new_project.raw = 
    #     db.session.add(self)
    #     db.session.commit()

    # @classmethod
    # def get(cls):
    #     return cls.query.first()
    
    @classmethod
    def get_all_by_user_id(cls, _id):
        projects = cls.query.filter_by(user_id=_id).all()
        return {'projects': [project.json() for project in projects]}

    @classmethod
    def find_by_user_id(cls, _id):
        return cls.query.filter_by(user_id=_id, id=0).first()

    @classmethod
    def find_by_project_name(cls, user_id, name):
        return cls.query.filter_by(user_id=user_id, name=name).first()

    def setId(self):
        id = db.session.query(db.func.max(self.id)).scalar()
        self.id = id+1

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
