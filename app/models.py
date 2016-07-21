from flask_login import UserMixin
from . import db, login_manager
from datetime import datetime
from sqlalchemy import or_, and_
from sqlalchemy.ext.hybrid import hybrid_property

##########
# Models #
##########

registrations = db.Table('registrations',
    db.Column("user_id", db.String(20), db.ForeignKey('users.user_id')),
    db.Column("consult_id", db.Integer, db.ForeignKey('consultations.consult_id')))

class UserModule(db.Model):
    __tablename__ = 'usermodules'
    user_id = db.Column(db.String(20), db.ForeignKey('users.user_id'), primary_key=True)
    module_id = db.Column(db.String(40), db.ForeignKey('modules.module_code'), primary_key=True)
    year = db.Column(db.Integer)
    sem = db.Column(db.Integer)

class Consultation(db.Model):
    __tablename__ = 'consultations'
    consult_id = db.Column(db.Integer, primary_key=True)
    module_code = db.Column(db.String(40), db.ForeignKey('modules.module_code'))
    consult_date = db.Column(db.Date)
    start = db.Column(db.Time)
    end = db.Column(db.Time)
    venue = db.Column(db.String(40))
    num_of_students = db.Column(db.Integer)
    contact_details = db.Column(db.String(40), nullable=True) 
    description = db.Column(db.String(140))
    teacher_id = db.Column(db.String(20), db.ForeignKey('users.user_id'))
    comments = db.relationship('Comment', backref='consult')
    attendees = db.relationship('User',
                                secondary=registrations,
                                backref=db.backref('attending', lazy='dynamic'),
                                lazy='dynamic')
    
    def __repr__(self):
        return '<Consult {id}: {name}>'.format(id=self.consult_id, name=self.module_code)

    def not_full(self):
        return (len(self.attendees.all()) < self.num_of_students)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(40))
    teaching = db.relationship('Consultation', backref='teacher', lazy='dynamic')
    modules = db.relationship('UserModule',
                              foreign_keys=[UserModule.user_id],
                              backref=db.backref('user', lazy='joined'),
                              lazy='dynamic',
                              cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author')
    
    def __repr__(self):
        return '<User {id}: {name}>'.format(id=self.user_id, name=self.name)

    def is_authenticated(self):
        if session.get('token'):
            user = UserAPI(session['token'])
            return user.logged_in()
        return False

    def is_active(self):
        return self.is_authenticated()

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.user_id.encode('utf-8')

    def takes(self, module, year, sem):
        t = UserModule(user=self, module=module, year=year, sem=sem)
        db.session.add(t)

    def currently_taking(self, year, sem):
        current_year = datetime.now().year
        if year > current_year:
            return True
        elif year == current_year and sem != 1:
            return (datetime.now().month < 8)
        else:
            return False

    @property
    def modules_taken(self):
        return Module.query.join(UserModule, UserModule.module_id == Module.module_code).filter(UserModule.user_id == self.user_id)

    @property
    def current_mods(self):
        return Module.query.join(UserModule, UserModule.module_id == Module.module_code).filter(
            UserModule.user_id == self.user_id,
            or_(UserModule.year > datetime.now().year,
                and_(UserModule.year == datetime.now().year, 
                 UserModule.sem != 1,
                 (datetime.now().month < 8)
                )
            ))

class Module(db.Model):
    __tablename__ = 'modules'
    module_code = db.Column(db.String(40), primary_key=True)
    name = db.Column(db.String(200))
    consults = db.relationship('Consultation', backref='module', lazy='dynamic')
    modules = db.relationship('UserModule',
                              foreign_keys=[UserModule.module_id],
                              backref=db.backref('module', lazy='joined'),
                              lazy='dynamic',
                              cascade='all, delete-orphan')

    @property
    def users_read(self):
        return User.query.join(UserModule, UserModule.user_id == User.user_id).filter(UserModule.module_id == self.module_code)


    def __repr__(self):
        return '<Module {module_code}: {name}>'.format(module_code=self.module_code, name=self.name) 

class Comment(db.Model):
    __tablename__ = 'comments'
    comment_id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(140))
    user_id = db.Column(db.String(20), db.ForeignKey('users.user_id'))
    consult_id = db.Column(db.Integer, db.ForeignKey('consultations.consult_id'))

    def __repr__(self):
        return '<Comment {}: {}>'.format(comment_id, message) 

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id.decode('utf-8'))