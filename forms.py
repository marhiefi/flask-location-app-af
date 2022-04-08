from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from models import User, Pet

class RegistrationForm(FlaskForm):
   username = StringField('Username', validators=[DataRequired(), Length(min=3, max= 20)])
   email= StringField('Email', validators=[DataRequired(), Email()])
   password= PasswordField('Password', validators=[DataRequired()])
   confirm_password= PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
   submit= SubmitField('Register')

   def validate_username(self, username):
        user= User.query.filter_by(username=username.data).first() 
        if user:
           raise ValidationError('Username already exists. Please choose another one.')

   def validate_email(self, email):
        user= User.query.filter_by(email=email.data).first() 
        if user:
           raise ValidationError('Email already exists. Please choose another one or log in.')


class LoginForm(FlaskForm):
   email= StringField('Email', validators=[DataRequired(), Email()])
   password= PasswordField('Password', validators=[DataRequired()])
   remember= BooleanField('Remember Me')
   submit= SubmitField('Log In')
     
class LostPetForm(FlaskForm):
   status_lostorfound = StringField('Please enter "Lost"', validators=[DataRequired()])
   petname = StringField('Pet Name', validators=[DataRequired(), Length(min=2, max= 20)])
   image_file= FileField('Optional but recommended: Upload a photo', validators=[FileAllowed(['jpg', 'png'])])
   date_lostorfound = StringField('On what date was the pet lost?', validators=[DataRequired(), Length(min=2, max= 20)])
   description = TextAreaField('Describe your lost pet, add what type (and breed if it helps) plus helpful details about it getting lost', validators=[DataRequired()])
   #describe = StringField('Choose a title for the location where it was last seen (For ex: Dog Laika lost here.)',
                           #validators=[DataRequired(), Length(min=1, max=80)])
   lookup_address = StringField('Find on the map the location where your pet was lost by searching for a nearby address')
   coord_latitude = HiddenField('Latitude',validators=[DataRequired()])
   coord_longitude = HiddenField('Longitude', validators=[DataRequired()])                 
   submit = SubmitField('Save your entry')
   
   def validate_status_lostorfound(self, status_lostorfound):
        pet= Pet.query.filter_by(status_lostorfound=status_lostorfound.data).first() 
        if pet:
           raise ValidationError('Please enter "Lost"')

   def validate_petname(self, petname):
        pet= Pet.query.filter_by(petname=petname.data).first() 
        if pet:
           raise ValidationError('Please enter the name of the pet')
   
   def validate_description(self, description):
        pet= Pet.query.filter_by(description=description.data).first() 
        if pet:
           raise ValidationError('Please enter descroption of the pet and any details about his disappearance')
   
   '''def validate_describe(self, describe):
        pet= Pet.query.filter_by(describe=describe.data).first() 
        if pet:
           raise ValidationError('Please enter a title to mark the location where the pet was lost') '''
        
   
   

    
class FoundPetForm(FlaskForm):   
   describe = StringField('Choose a title for your location (For ex: Husky found here.)',
                           validators=[DataRequired(), Length(min=1, max=80)])
   lookup_address = StringField('Find the address')
   coord_latitude = HiddenField('Latitude',validators=[DataRequired()])
   coord_longitude = HiddenField('Longitude', validators=[DataRequired()])                    
   submit = SubmitField('Save location on map')

class NewLocationForm(FlaskForm):
    describe = StringField('Location description',
                           validators=[DataRequired(), Length(min=1, max=80)])
    lookup_address = StringField('Search address')

    coord_latitude = HiddenField('Latitude',validators=[DataRequired()])

    coord_longitude = HiddenField('Longitude', validators=[DataRequired()])                    

    submit = SubmitField('Create Location')

