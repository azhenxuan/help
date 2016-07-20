from flask import Flask, render_template, flash, request, session, redirect, url_for, current_app
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime
from threading import Thread
from ..models import UserModule, Consultation, User, Module
from .forms import NewConsultForm
from . import main
from .. import db
from .api import *
import requests
import json
import os

@main.route('/')
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
            db.session.commit()

            def update_modules(app, user_api):
                with app.app_context():
                    # Get your modules
                    user_id = user_api.get_user_id()
                    db_user = User.query.get(user_id)
                    modules_taken = user_api.get_modules_taken()

                    if len(modules_taken) == len(db_user.modules_taken.all()):
                        return
                    
                    for module in modules_taken:
                        module_name = module['ModuleTitle']
                        module_code = module['ModuleCode']
                        module_year = int(module['AcadYear'].split('/')[1])
                        module_sem = int(module['Semester'])

                        curr_mod = Module.query.filter_by(module_code=module_code).first()

                        if not curr_mod:
                            curr_mod = Module(module_code=module_code, name=module_name)
                            db.session.add(curr_mod)

                        if curr_mod not in db_user.modules_taken.all():
                            db_user.takes(curr_mod, year=module_year, sem=module_sem)

            ##### START PROCESS IN THREAD #####
            app = current_app._get_current_object()
            thr = Thread(target=update_modules, args=[app, user])
            thr.start()
            ##### END PROCESS IN THREAD #####

            login_user(db_user)

            return redirect(url_for('.home'))
        session['token'] = None
    return render_template('index.html', name=None)

@main.route('/get_help')
@login_required
def get_help():
    consults = Consultation.query.filter(Consultation.consult_date >= datetime.date(datetime.now())).all()
    consults_im_attending = current_user.attending.all()
    consults_im_teaching = current_user.teaching
    modules_im_taking = current_user.current_mods.all()
    consults_to_display = [consult for consult in consults if consult not in consults_im_teaching and consult.not_full() and (consult.module in modules_im_taking)]
    consults_to_display.sort(key=lambda x: x.consult_date)

    module_codes = [module.module_code for module in modules_im_taking]
    return render_template('get_help.html', 
                           consults=consults_to_display, 
                           consults_im_attending=consults_im_attending, 
                           module_codes=module_codes, 
                           User=User)

@main.route('/provide_help', methods=['GET', 'POST'])
@login_required
def provide_help():
    form = NewConsultForm()
    mods = current_user.modules_taken.all()
    if not len(mods):
        flash("Wait, we don't have your modules yet! Please refresh the page so we can find them. Thanks!")
    mod_choices = [(mod.module_code, str(mod)[8:-1]) for mod in mods]
    form.module_code.choices = mod_choices

    if form.validate_on_submit():
        consult = Consultation(module_code=form.module_code.data,
                               consult_date=datetime.strptime(form.date.data, "%d/%m/%Y"),
                               start=datetime.strptime(form.start.data, "%I:%M %p").time(),
                               end=datetime.strptime(form.end.data, "%I:%M %p").time(),
                               venue=form.venue.data,
                               num_of_students=form.max_students.data,
                               contact_details=form.contact_details.data,
                               teacher_id=current_user.user_id,
                               description=form.description.data)
        flash("New consultation slot added for {module_code}".format(module_code=form.module_code.data))
        db.session.add(consult)
        return redirect(url_for('.home'))

    return render_template('provide_help.html', form=form)

@main.route('/home')
@login_required
def home():
    get_help = sorted(current_user.attending.filter(Consultation.consult_date >= datetime.date(datetime.now())).all(), key=lambda x: x.consult_date)
    give_help = sorted(current_user.teaching.filter(Consultation.consult_date >= datetime.date(datetime.now())).all(), key=lambda x: x.consult_date)
    return render_template('see_schedule.html', get_help=get_help, give_help=give_help, User=User)

###########
# Consult #
###########

@main.route('/join_class/<consult_id>')
@login_required
def join_class(consult_id):
    consult = Consultation.query.get(consult_id)
    if consult not in current_user.attending and consult.not_full():
        current_user.attending.append(consult)
        db.session.add(current_user)
        flash("You have successfully enrolled in this class.")
    elif not consult.not_full():
        flash("You're too late! There are no more slots left for this consult.")
    else:
        flash("You've already enrolled in this class.")
    return redirect(url_for('.get_help'))

@main.route('/quit_class/<consult_id>')
@login_required
def quit_class(consult_id):
    consult = Consultation.query.get(consult_id)
    if consult in current_user.attending:
        current_user.attending.remove(consult)
    db.session.add(current_user)
    return redirect(url_for('.home'))

@main.route('/update_class', methods=['GET', 'POST'])
@login_required
def update_class():
    consult = Consultation.query.get(request.args.get('consult_id'))
    
    if consult not in current_user.teaching:
        flash("You are not teaching this class.")
        return redirect(url_for('.home'))

    form = NewConsultForm(module_code=consult.module_code,
                          date = datetime.strftime(consult.consult_date, "%d/%m/%Y"),
                          start = consult.start.strftime("%I:%M %p"),
                          end = consult.end.strftime("%I:%M %p"),
                          venue = consult.venue,
                          max_students = consult.num_of_students,
                          contact_details = consult.contact_details,
                          description = consult.description)

    mods = current_user.modules_taken.all()
    mod_choices = [(mod.module_code, str(mod)[8:-1]) for mod in mods]
    form.module_code.choices = mod_choices

    if form.validate_on_submit():
        consult.module_code=form.module_code.data
        consult.consult_date=datetime.strptime(form.date.data, "%d/%m/%Y")
        consult.start=datetime.strptime(form.start.data, "%I:%M %p").time()
        consult.end=datetime.strptime(form.end.data, "%I:%M %p").time()
        consult.venue=form.venue.data
        consult.num_of_students=form.max_students.data
        consult.contact_details=form.contact_details.data
        consult.teacher_id=current_user.user_id
        consult.description=form.description.data

        db.session.add(consult)

        flash("You have updated your consultation slot for {module_code}".format(module_code=consult.module_code))
        return redirect(url_for('.home'))

    flash("You are editing a consultation slot.")   
    return render_template('provide_help.html', form=form)

@main.route('/delete_class/<consult_id>')
@login_required
def delete_class(consult_id):
    consult = Consultation.query.get(consult_id)
    
    if consult not in current_user.teaching:
        flash("You are not teaching this class.")
        return redirect(url_for('.home'))

    db.session.delete(consult)
    flash("You have deleted a consultation slot.")
    return redirect(url_for('.home'))

@main.route('/class_admin/<consult_id>')
@login_required
def class_admin(consult_id):
    consult = Consultation.query.get(consult_id)

    if consult not in current_user.teaching:
        flash("You are not teaching this class.")
        return redirect(url_for('.home'))

    return render_template('class_admin.html', consult=consult)

@main.route('/class_details/<consult_id>')
@login_required
def class_details(consult_id):
    consult = Consultation.query.get(consult_id)
    
    if consult not in current_user.attending:
        flash("You are not attending this class.")
        return redirect(url_for('.home'))

    return render_template('class_details.html', consult=consult)

@main.route("/logout")
@login_required
def logout():
    logout_user()
    session['token'] = None

    flash("You have successfully logged out.")
    return redirect(url_for('.index'))

@main.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'

