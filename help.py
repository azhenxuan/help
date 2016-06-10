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

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.String(20), primary_key=True)
    name    = db.Column(db.String(64))
    
    def __repr__(self):
        return '<User {id}: {name}>'.format(id=self.user_id, name=self.name)

class Module(db.Model):
    __tablename__ = 'modules'
    mod_code = db.Column(db.String(20), primary_key=True)
    name     = db.Column(db.String(20))

    def __repr__(self):
        return '<Module {code}: {name}>'.format(code=self.mod_code, name=self.name)

#########
# Forms #
#########

class NewConsultForm(Form):
    mod_code     = SelectField('Module Code', choices = [("MA1101R", "MA1101R"), 
        ("MA1102R", "MA1102R"), ("CS1010S", "CS1010S"), ("CS2020", "CS2020")])
    date         = DateField('Date')
    start        = TimeField('Start')
    end          = TimeField('End')
    venue        = StringField('Venue')
    max_students = SelectField('Max no. of students: ', choices = [("5", 5), ("10", 10), ("15", 15), ("20", 20)])
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

@app.route('/provide_help')
def provide_help():
    form = NewConsultForm()
    if session.get('token'):
        user = UserAPI(session['token'])
        if user.logged_in():
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