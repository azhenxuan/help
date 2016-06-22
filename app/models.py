from flask_login import UserMixin
from . import db, login_manager

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
    teacher_id = db.Column(db.String(20), db.ForeignKey('users.user_id'))
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
    teaching = db.relationship('Consultation', backref='teacher')
    modules = db.relationship('UserModule',
                              foreign_keys=[UserModule.user_id],
                              backref=db.backref('user', lazy='joined'),
                              lazy='dynamic',
                              cascade='all, delete-orphan')
    
    def __repr__(self):
        return '<User {id}: {name}>'.format(id=self.user_id, name=self.name)

    def is_authenticated(self):
        return True
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
        elif year == current_year:
            if int(module['Semester']) == 1:
                return False
            else:
                return (datetime.now().month < 8)
        else:
            return False

    @property
    def modules_taken(self):
        return Module.query.join(UserModule, UserModule.module_id == Module.module_code).filter(UserModule.user_id == self.user_id)

    @property
    def current_mods(self):
        return Module.query.join(UserModule, UserModule.module_id == Module.module_code).filter(
            UserModule.user_id == self.user_id and \
            self.currently_taking(Module.year, Module.sem))

class Module(db.Model):
    __tablename__ = 'modules'
    module_code = db.Column(db.String(40), primary_key=True)
    name = db.Column(db.String(60))
    consults = db.relationship('Consultation', backref='module')
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

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id.decode('utf-8'))