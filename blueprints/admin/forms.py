from flask_wtf import FlaskForm
from wtforms import (StringField, TextAreaField, SelectField, IntegerField,
                     FloatField, SubmitField)
from wtforms.fields import DateField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


DIFF_CHOICES = [('Easy', 'Easy'), ('Moderate', 'Moderate'), ('Hard', 'Hard')]
STATUS_CHOICES = [
    ('Pending', 'Pending'),
    ('Approved', 'Approved'),
    ('Open', 'Open'),
    ('Closed', 'Closed'),
    ('Completed', 'Completed'),
]


class TrekForm(FlaskForm):
    name = StringField('Trek Name', validators=[DataRequired(), Length(max=160)])
    location = StringField('Location / Region', validators=[DataRequired(), Length(max=160)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=2000)])
    difficulty = SelectField('Difficulty Level', choices=DIFF_CHOICES, validators=[DataRequired()])
    duration_days = IntegerField(
        'Duration (days)', validators=[DataRequired(), NumberRange(min=1, max=365)]
    )
    total_slots = IntegerField(
        'Total Slots (capacity)', validators=[DataRequired(), NumberRange(min=1, max=500)]
    )
    available_slots = IntegerField(
        'Available Slots', validators=[DataRequired(), NumberRange(min=0, max=500)]
    )
    price_per_person = FloatField(
        'Price per Person (₹)', validators=[DataRequired(), NumberRange(min=0)]
    )
    max_altitude = StringField('Max Altitude', validators=[Optional(), Length(max=60)])
    meeting_point = StringField('Meeting Point', validators=[Optional(), Length(max=200)])
    start_date = DateField('Start Date', validators=[Optional()])
    end_date = DateField('End Date', validators=[Optional()])
    status = SelectField('Trek Status', choices=STATUS_CHOICES, validators=[DataRequired()])
    assign_staff = SelectField('Assign Trek Guide', coerce=int, validators=[Optional()])
    image_num = IntegerField(
        'Illustration Number (1–6)', validators=[Optional(), NumberRange(min=1, max=6)],
        default=1
    )
    submit = SubmitField('Save Trek')