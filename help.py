from flask import Flask, render_template, flash, request, session, redirect, url_for
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_wtf import Form
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from wtforms import SubmitField, SelectField, StringField
from wtforms_components import DateField, TimeField
from datetime import datetime
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
login_manager = LoginManager(app)
manager.add_command('db', MigrateCommand)

#########
# Login #
#########
login_manager.session_protection = "strong"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id.decode('utf-8'))

##########
# Models #
##########

registrations = db.Table('registrations',
    db.Column("user_id", db.String(20), db.ForeignKey('users.user_id')),
    db.Column("consult_id", db.Integer, db.ForeignKey('consultations.consult_id')))

class Consultation(db.Model):
    __tablename__ = 'consultations'
    consult_id = db.Column(db.Integer, primary_key=True)
    module_code = db.Column(db.String(8))
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
        return '<User {id}: {name}>'.format(id=self.consult_id, name=self.module_code)
    
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(40))
    teaching = db.relationship('Consultation', backref='teacher')
    
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

#########
# Forms #
#########

class NewConsultForm(Form):
    module_code     = SelectField('Module Code', choices = [("MA1101R", "MA1101R"), 
        ("MA1102R", "MA1102R"), ("CS1010S", "CS1010S"), ("CS2020", "CS2020")])
    date         = StringField('Date', id="datepicker")
    start        = StringField('Start', id="start")
    end          = StringField('End', id="end")
    venue        = StringField('Venue')
    max_students = SelectField('Max no. of students: ', choices = [(5, "5"), (10, "10"), (15, "15"), (20, "20")], coerce=int)
    contact_details = StringField('Handphone Number (Optional)')
    submit       = SubmitField()

##########
# Routes #
##########

@app.route('/')
def index():
    if request.args.get('token'):
        session['token'] = request.args['token']

    if session.get('token'):
        user = UserAPI(session['token'])
        if user.logged_in():
            name = user.get_name()
            user_id = user.get_user_id()
            db_user = User.query.get(user_id)

            # Create user if not in db
            if not db_user:
                db_user = User(name=name, user_id=user_id)
                db.session.add(db_user)

            login_user(db_user)

            return render_template('index.html', name=name.title())

    session['token'] = None
    return render_template('index.html', name=None)

@app.route('/get_help')
@login_required
def get_help():
    consults = Consultation.query.all()
    consults_im_attending = current_user.attending.all()
    consults_im_teaching = current_user.teaching
    consults_im_not_teaching = [consult for consult in consults if consult not in consults_im_teaching]
    return render_template('get_help.html', consults=consults_im_not_teaching, consults_im_attending=consults_im_attending, User=User)

@app.route('/provide_help', methods=['GET', 'POST'])
@login_required
def provide_help():
    form = NewConsultForm()

    if form.validate_on_submit():
        consult = Consultation(module_code=form.module_code.data,
                               consult_date=datetime.strptime(form.date.data, "%d/%m/%Y"),
                               start=datetime.strptime(form.start.data, "%I:%M %p").time(),
                               end=datetime.strptime(form.end.data, "%I:%M %p").time(),
                               venue=form.venue.data,
                               num_of_students=form.max_students.data,
                               contact_details=form.contact_details.data,
                               teacher_id=current_user.user_id)
        flash("New consultation slot added for {module_code}".format(module_code=form.module_code.data))
        db.session.add(consult)
        return redirect(url_for('see_schedule'))

    return render_template('provide_help.html', form=form)

@app.route('/see_schedule')
@login_required
def see_schedule():
    get_help = current_user.attending.all()
    give_help = current_user.teaching
    return render_template('see_schedule.html', get_help=get_help, give_help=give_help, User=User)

@app.route('/join_class/<consult_id>')
@login_required
def join_class(consult_id):
    consult = Consultation.query.get(consult_id)
    if consult not in current_user.attending:
        current_user.attending.append(consult)
    db.session.add(current_user)
    return redirect(url_for('get_help'))

@app.route('/quit_class/<consult_id>')
@login_required
def quit_class(consult_id):
    consult = Consultation.query.get(consult_id)
    if consult in current_user.attending:
        current_user.attending.remove(consult)
    db.session.add(current_user)
    return redirect(url_for('see_schedule'))

@app.route('/update_class', methods=['GET', 'POST'])
@login_required
def update_class():
    consult = Consultation.query.get(request.args.get('consult_id'))
    
    if consult not in current_user.teaching:
        flash("You are not teaching this class.")
        return redirect(url_for('see_schedule'))

    form = NewConsultForm(module_code=consult.module_code,
                          date = datetime.strftime(consult.consult_date, "%d/%m/%Y"),
                          start = consult.start.strftime("%I:%M %p"),
                          end = consult.end.strftime("%I:%M %p"),
                          venue = consult.venue,
                          max_students = consult.num_of_students,
                          contact_details = consult.contact_details)

    if form.validate_on_submit():
        consult.module_code=form.module_code.data
        consult.consult_date=datetime.strptime(form.date.data, "%d/%m/%Y")
        consult.start=datetime.strptime(form.start.data, "%I:%M %p").time()
        consult.end=datetime.strptime(form.end.data, "%I:%M %p").time()
        consult.venue=form.venue.data
        consult.num_of_students=form.max_students.data
        consult.contact_details=form.contact_details.data
        consult.teacher_id=current_user.user_id

        db.session.add(consult)

        flash("You have updated your consultation slot for {module_code}".format(module_code=consult.module_code))
        return redirect(url_for('see_schedule'))

    flash("You are editing a consultation slot.")   
    return render_template('provide_help.html', form=form)

@app.route('/delete_class/<consult_id>')
@login_required
def delete_class(consult_id):
    consult = Consultation.query.get(consult_id)
    
    if consult not in current_user.teaching:
        flash("You are not teaching this class.")
        return redirect(url_for('see_schedule'))

    db.session.delete(consult)
    flash("You have deleted a consultation slot.")
    return redirect(url_for('see_schedule'))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    session['token'] = None

    flash("You have successfully logged out.")
    return redirect(url_for('index'))

# Error Handling
@app.errorhandler(401)
def logged_out(e):
    flash("You are currently logged out. Please log in.")
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
  return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
  return render_template('500.html'), 500

if __name__ == '__main__':
    manager.run()