from flask import Flask, render_template, flash, request, session, redirect, url_for
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_wtf import Form
from wtforms import SubmitField, SelectField, StringField
from wtforms_components import DateField, TimeField
from api import *
import requests
import json
import os

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard2guess'
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

manager = Manager(app)
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

##########
# Models #
##########

class Creation(db.Model):
    _tablename_ = 'creations'
    teacher_id = db.Column(db.String(20), db.ForeignKey('users.user_id'), primary_key=True)
    consult_id = db.Column(db.Integer, db.ForeignKey('consultations.consult_id'), primary_key=True)
    
class Registration(db.Model):
    _tablename_ = 'registrations'
    user_id = db.Column(db.String(20), db.ForeignKey('users.user_id'), primary_key=True)
    consult_id = db.Column(db.Integer, db.ForeignKey('consultations.consult_id'), primary_key=True)

class Consultation(db.Model):
    __tablename__ = 'consultations'
    consult_id = db.Column(db.Integer, primary_key=True)
    module_code = db.Column(db.String(8))
    date = db.Column(db.Date)
    start = db.Column(db.Time)
    end = db.Column(db.Time)
    venue = db.Column(db.String(40))
    num_of_students = db.Column(db.Integer)
    contact_details = db.Column(db.String(40), nullable=True) 
    
    def __repr__(self):
        return '<User {id}: {name}>'.format(id=self.consult_id, name=self.module_code)
    
class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(40))
    teaching = db.relationship('Creation', 
                               foreign_keys=[Creation.teacher_id],
                               backref=db.backref('teacher', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    attending = db.relationship('Registration', 
                                foreign_keys=[Registration.user_id],
                                backref=db.backref('attendees', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')
    
    def __repr__(self):
        return '<User {id}: {name}>'.format(id=self.user_id, name=self.name)

    

#########
# Forms #
#########

class NewConsultForm(Form):
    module_code     = SelectField('Module Code', choices = [("MA1101R", "MA1101R"), 
        ("MA1102R", "MA1102R"), ("CS1010S", "CS1010S"), ("CS2020", "CS2020")])
    date         = DateField('Date')
    start        = TimeField('Start')
    end          = TimeField('End')
    venue        = StringField('Venue')
    max_students = SelectField('Max no. of students: ', choices = [(5, "5"), (10, "10"), (15, "15"), (20, "20")], coerce=int)
    contact_details = StringField('Handphone Number (Optional)')
    submit       = SubmitField('Create')

##########
# Routes #
##########

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/inside')
def inside():
    if request.args.get('token'):
        session['token'] = request.args['token']

    if session.get('token'):
        user = UserAPI(session['token'])
        if user.logged_in():
            name = user.get_name()
            user_id = user.get_user_id()

            # Create user if not in db
            if not User.query.filter_by(user_id = user_id).first():
                new_user = User(name=name, user_id=user_id)
                db.session.add(new_user)
            return render_template('inside.html', name=name.title())

    session['token'] = None
    flash("You are currently logged out. Please log in.")
    return redirect(url_for('index'))

@app.route('/get_help')
def get_help():
    if session.get('token'):
        user = UserAPI(session['token'])
        if user.logged_in():
            return render_template('get_help.html')

    session['token'] = None
    flash("You are currently logged out. Please log in.")
    return redirect(url_for('index'))

@app.route('/provide_help', methods=['GET', 'POST'])
def provide_help():
    form = NewConsultForm()
    user = UserAPI(session.get('token'))
    if user.logged_in():
        if form.validate_on_submit():
            consult = Consultation(module_code=form.module_code.data,
                                   date=form.date.data,
                                   start=form.start.data,
                                   end=form.end.data,
                                   venue=form.venue.data,
                                   num_of_students=form.max_students.data,
                                   contact_details=form.contact_details.data)
            creation = Creation(teacher_id=user.user_id, consult_id=consult.consult_id)
            db.session.add(consult)
            db.session.add(creation)

            flash("New consultation slot added for {module_code}".format(module_code=form.module_code.data))
        return render_template('provide_help.html', form=form)

    session['token'] = None
    flash("You are currently logged out. Please log in.")
    return redirect(url_for('index'))

@app.route('/see_schedule')
def my_schedule():
    if session.get('token'):
        user = UserAPI(session['token'])
        if user.logged_in():
            return render_template('my_schedule.html')

    session['token'] = None
    flash("You are currently logged out. Please log in.")
    return redirect(url_for('index'))


# Error Handling
# @app.errorhandler(404)
# def page_not_found(e):
#   return render_template('404.html'), 404

# @app.errorhandler(500)
# def internal_server_error(e):
#   return render_template('500.html'), 500

if __name__ == '__main__':
    manager.run()