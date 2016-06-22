from wtforms import SubmitField, SelectField, StringField, IntegerField 
from wtforms.validators import Required, NumberRange
from wtforms_components import DateField, TimeField
from flask_wtf import Form

class NewConsultForm(Form):
    module_code  = SelectField('Module Code', choices = [], validators=[Required()])
    date         = StringField('Date', id="datepicker", validators=[Required()])
    start        = StringField('Start', id="start", validators=[Required()])
    end          = StringField('End', id="end", validators=[Required()])
    venue        = StringField('Venue', validators=[Required()])
    max_students = IntegerField('Max no. of students', validators=[NumberRange(min=1, message="Please allow at least 1 student to join your class."), Required()])
    contact_details = StringField('HP Number (Optional)')
    submit       = SubmitField()