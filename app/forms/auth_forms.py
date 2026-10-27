from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, SubmitField, TextAreaField, DateField, FloatField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, ValidationError
from app.models.user import User

class LoginForm(FlaskForm):
    role = SelectField('Login As', choices=[
        ('member', 'Member'),
        ('trainer', 'Trainer / Coach'),
        ('receptionist', 'Front Desk / Receptionist')
    ], validators=[Optional()], default='member')
    email = StringField('Email Address', validators=[DataRequired(), Email(), Length(max=120)], render_kw={"placeholder": "name@domain.com", "autocomplete": "email"})
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)], render_kw={"placeholder": "••••••••", "autocomplete": "current-password"})
    remember_me = BooleanField('Keep me signed in on this device')
    submit = SubmitField('Sign In')

class AdminLoginForm(FlaskForm):
    email = StringField('Master Admin Email', validators=[DataRequired(), Email(), Length(max=120)], render_kw={"placeholder": "admin@setfitgym.com", "autocomplete": "username"})
    password = PasswordField('Master Password', validators=[DataRequired(), Length(min=8)], render_kw={"placeholder": "••••••••••••", "autocomplete": "current-password"})
    admin_secret = PasswordField('Security Passcode (ADMIN_SECRET)', validators=[DataRequired(), Length(min=6)], render_kw={"placeholder": "Enter Admin Passcode"})
    submit = SubmitField('Authorize Executive Terminal')

class MemberRegisterForm(FlaskForm):
    first_name = StringField('First Name *', validators=[DataRequired(), Length(min=2, max=60)], render_kw={"placeholder": "First Name"})
    last_name = StringField('Last Name', validators=[Optional(), Length(max=60)], render_kw={"placeholder": "Last Name"})
    email = StringField('Email Address *', validators=[DataRequired(), Email(), Length(max=120)], render_kw={"placeholder": "name@domain.com"})
    phone = StringField('Mobile Number (WhatsApp) *', validators=[DataRequired(), Length(min=8, max=20)], render_kw={"placeholder": "+91 98765 43210"})
    
    password = PasswordField('Password *', validators=[DataRequired(), Length(min=6, message="Password must be at least 6 characters.")], render_kw={"placeholder": "Create secure password"})
    confirm_password = PasswordField('Confirm Password *', validators=[DataRequired(), EqualTo('password', message='Passwords must match.')], render_kw={"placeholder": "Re-enter password"})
    
    dob = DateField('Date of Birth', validators=[Optional()], format='%Y-%m-%d', render_kw={"placeholder": "YYYY-MM-DD"})
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], default='Male')
    emergency_contact = StringField('Emergency Contact', validators=[Optional(), Length(max=50)], render_kw={"placeholder": "Name & Phone"})
    fitness_goal = SelectField('Primary Goal', choices=[
        ('Muscle Building', 'Hypertrophy & Muscle Building'),
        ('Fat Loss', 'Fat Loss & Conditioning'),
        ('Powerlifting', 'Strength & Olympic Powerlifting'),
        ('General Fitness', 'General Athletic Fitness')
    ], default='Muscle Building')
    
    plan_id = SelectField('Select Initial Membership Tier (₹)', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Claim Membership Pass')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.strip().lower()).first()
        if user:
            raise ValidationError('An account with this email already exists. Please sign in instead.')

class EnquiryForm(FlaskForm):
    name = StringField('Full Name *', validators=[DataRequired(), Length(min=2, max=100)], render_kw={"placeholder": "Enter your full name"})
    phone = StringField('Mobile Phone (WhatsApp) *', validators=[DataRequired(), Length(min=8, max=25)], render_kw={"placeholder": "+91 98765 43210"})
    email = StringField('Email (Optional)', validators=[Optional(), Email(), Length(max=120)], render_kw={"placeholder": "name@domain.com"})
    preferred_branch = SelectField('Preferred Gym Location', choices=[
        ('Karve Nagar Pune', 'SETFIT Main Arena (Karve Nagar, Pune)')
    ], default='Karve Nagar Pune')
    fitness_goal = SelectField('Primary Fitness Goal', choices=[
        ('Muscle Building', 'Hypertrophy & Muscle Building'),
        ('Fat Loss', 'Fat Loss & Body Conditioning'),
        ('Powerlifting', 'Strength & Olympic Powerlifting'),
        ('Endurance', 'Athletic Stamina & Endurance'),
        ('General Fitness', 'General Health & Mobility')
    ], default='Muscle Building')
    notes = TextAreaField('Time Preference / Questions', validators=[Optional()], render_kw={"rows": 2, "placeholder": "e.g. Morning 7 AM session, interested in personal trainer"})
    submit = SubmitField('Book Free Assessment Now')
