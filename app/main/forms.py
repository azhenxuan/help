from wtforms import SubmitField, SelectField, StringField, IntegerField, TextAreaField
from wtforms.validators import Required, NumberRange, Length
from wtforms_components import DateField, TimeField
from flask_wtf import Form
from datetime import datetime

class NewConsultForm(Form):
    module_code  = SelectField('Module Code', choices = [], validators=[Required()])
    date         = StringField('Date', id="datepicker", validators=[Required()])
    start        = StringField('Start', id="start", validators=[Required()])
    end          = StringField('End', id="end", validators=[Required()])
    venue        = StringField('Venue', validators=[Required()])
    max_students = IntegerField('Max no. of students', validators=[NumberRange(min=1, 
        message="Please allow at least 1 student to join your class."), Required()])
    contact_details = StringField('HP Number (Optional)', validators=[Length(max=8, 
        message="Please input a valid phone number")])
    description = TextAreaField("What're you teaching?", validators=[Length(max=140,
        message="Please keep it to less than 140 chars"), Required()])
    submit       = SubmitField()

    # Check that start time is before end time
    def validate(self):
        if not Form.validate(self):
            return False

        result = True

        start = datetime.strptime(self.start.data, "%I:%M %p").time()
        end   = datetime.strptime(self.end.data, "%I:%M %p").time()

        if start >= end:
            self.end.errors.append("Make sure your consult doesn't end before it starts")
            return False
        return result