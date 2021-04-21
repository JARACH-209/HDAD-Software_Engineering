from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, IntegerField , SubmitField, RadioField, SelectField , DecimalField  
from flask_wtf.file import FileField, FileRequired
from wtforms.validators import InputRequired, Email, Length , NumberRange, Regexp , EqualTo
from wtforms.fields.html5 import EmailField
from wtforms.widgets import TextArea

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[
                           InputRequired(), Length(min=1, max=15)])
    password = PasswordField('Password', validators=[
                             InputRequired(), Length(min=1, max=80)])
    remember = BooleanField('Remember me')

class UploadCSV(FlaskForm):
    csv = FileField(validators=[FileRequired()])

class UsernameForm(FlaskForm):

    Email = EmailField('Email', validators=[
                          InputRequired(), Length(max=100)])


class RegisterForm(FlaskForm):
    DocName = StringField('Name', validators=[ Regexp(r'[a-zA-Z ]+$', message='can only contain alphabets.'),
                          InputRequired('Name must not be empty'), Length(max=100)])
    DocHospital = StringField('Hospital', validators=[
                              InputRequired(), Length(max=100)])
    Email = EmailField('Email', validators=[
                          InputRequired(), Length(max=100)])
    password = PasswordField('Password', validators=[ EqualTo('Confirmpassword', message='Passwords must match'),
                             InputRequired(), Length(min=8, max=80 ,message='must be between 8 and 80 characters long.')])
    Confirmpassword = PasswordField('Confirm Password', validators=[ 
                             InputRequired(), Length(min=8, max=80)])

class PatientForm(FlaskForm):
    PatientName = StringField('Patient Name', validators=[ Regexp(r'[a-zA-Z0-9 ]+$', message='can only contain alphabets.'),
        InputRequired(), Length(min=1,max=100)])

class ConfirmDelete(FlaskForm):
    Input = StringField('Delete', validators=[
        InputRequired(), Length(min=1,max=100)])
class TokenForm(FlaskForm):
    Token = StringField('Security Key', validators=[
        InputRequired(), Length(max=10)])
class NewPassword(FlaskForm):
    password = PasswordField('password', validators=[
                             InputRequired(), Length(min=8, max=80)])
    Confirmpassword = PasswordField('password', validators=[
                             InputRequired(), Length(min=8, max=80)])
class MailForm(FlaskForm):
    email = StringField('Patient Email', validators=[
        InputRequired(), Email(message='Invalid email'),Length(max=100)])
    message = StringField('message', widget=TextArea(),validators=[ Regexp(r'[a-zA-Z0-9]+$', message='can only contain alphabets.'),
                             InputRequired(), Length(min=1, max=1000)])
    
class UsernameRecoveryForm(FlaskForm):
    email = StringField('Email', validators=[ EqualTo('Confirmemail', message='Both the Emails must match'),
        InputRequired(), Email(message='Invalid email'),Length(max=100)])
    confirmemail = StringField('Confirm Email', validators=[ 
        InputRequired(), Email(message='Invalid email'),Length(max=100)])

class PasswordRecoveryForm(FlaskForm):
    username = StringField('Username', validators=[
                           InputRequired(), Length(min=1, max=15)])
    email = StringField('Email', validators=[ 
        InputRequired(), Email(message='Invalid email'),Length(max=100)])    

class StatsSelector(FlaskForm):
    Feature1 = SelectField('Label1', 
    choices=[
        ('Age','Age'),
        ('BNP','Brain Natriuretic Peptide'),
        ('Cholestrol','Cholestrol'),
        ('CEM','Creatnine Enzymetic Method'),
        ('CreatnineKinase','Creatnine Kinase'),
        ('Cystatin','Cystatin'),
        ('Killip','Killip Grade'),
        ('BMI','Body Mass Index'),
        ('LVEDD','left ventricular end diastolic diameter LV'),
        ('NYHA','NYHA Cardiac Function Classification'),
        ('Potassium','Potassium'),
        ('Pulse','Pulse'),
        ('SystolicBP','Systolic Blood Presure'),
        ('Sex','Sex'),
        ('CP','Chest Pain type'),
        ('BP','Resting Blood Pressure ( mm/Hg )'),
        ('CholestrolHeart','Fasting Blood Sugar > 120 mg/d'),
        ('ECG','Resting ECG'),
        ('Thalach','Maximum heart rate achieved'),
        ('Exang','Exercise induced angina'),
        ('OldPeak','ST depression induced by exercise relative to rest'),
        ('Slope','The slope of the peak exercise ST segment'),
        ('Ca','Number of major vessels (0-3) colored by flourosopy'),
        ('Thal','Thalassemia (1-7) 3 = normal; 6 = fixed defect; 7 = reversable defect'),
        ])
    Feature2 = SelectField('Label2', 
    choices=[('Date','Date'),
        ('Age','Age'),
        ('BNP','Brain Natriuretic Peptide'),
        ('Cholestrol','Cholestrol'),
        ('CEM','Creatnine Enzymetic Method'),
        ('CreatnineKinase','Creatnine Kinase'),
        ('Cystatin','Cystatin'),
        ('Killip','Killip Grade'),
        ('BMI','Body Mass Index'),
        ('LVEDD','left ventricular end diastolic diameter LV'),
        ('NYHA','NYHA Cardiac Function Classification'),
        ('Potassium','Potassium'),
        ('Pulse','Pulse'),
        ('SystolicBP','Systolic Blood Presure'),
        ('Sex','Sex'),
        ('CP','Chest Pain type'),
        ('BP','Resting Blood Pressure ( mm/Hg )'),
        ('CholestrolHeart','Fasting Blood Sugar > 120 mg/d'),
        ('ECG','Resting ECG'),
        ('Thalach','Maximum heart rate achieved'),
        ('Exang','Exercise induced angina'),
        ('OldPeak','ST depression induced by exercise relative to rest'),
        ('Slope','The slope of the peak exercise ST segment'),
        ('Ca','Number of major vessels (0-3) colored by flourosopy'),
        ('Thal','Thalassemia (1-7) 3 = normal; 6 = fixed defect; 7 = reversable defect'),
    ])



class CHFDiagnostics(FlaskForm):
    Pulse = IntegerField('Pulse ( beats per minute ) ', validators=[ InputRequired(), NumberRange(min=30,max=300,message="Enter Correct Value")] )
    NYHA = SelectField('New York Heart Association (NYHA) Functional Classification', choices=[('','---------Select---------'),(1,'1'),(2,'2'),(3,'3'),(4,'4')],validators=[InputRequired()])
    Killip = SelectField('Killip Grade', choices=[('','---------Select---------'),(1,'1'),(2,'2'),(3,'3'),(4,'4')],validators=[InputRequired()])
    BNP = DecimalField('Brain Natriuretic Peptide ( pg/ml )', validators=[NumberRange(min=1,max=8001,message="Enter Correct Value"),  InputRequired()])
    Cystatin = DecimalField('Cystatin ( mg/l )', validators=[NumberRange(min=0,max=7,message="Enter Correct Value"), InputRequired()])
    Potassium = DecimalField('Potassium ( mmol/L )', validators=[NumberRange(min=0,max=10,message="Enter Correct Value"), InputRequired()])

class HeartDiseaseDiagnostics(FlaskForm):
    Age = DecimalField('Age', validators=[NumberRange(min=0,max=130,message="Enter Correct Value"), InputRequired()] )
    Sex = SelectField('Sex', choices=[('','---------Select---------'),(1,'Male'),(0,'Female')],validators=[InputRequired()])
    CP = SelectField('Chest Pain type', choices=[('','---------Select---------'),(1,' typical angina'),(2,' atypical angina'),(3,' non-anginal pain'),(4,' asymptomatic')],validators=[InputRequired()])
    BP = DecimalField('Resting Blood Pressure ( mm/Hg )', validators=[ NumberRange(min=30,max=300,message="Enter Correct Value"),  InputRequired()])
    CholestrolHeart = DecimalField('Serum Cholestoral ( mg/dl )', validators=[NumberRange(min=0,max=388,message="Enter Correct Value"),   InputRequired()])
    FBS = SelectField('Fasting Blood Sugar > 120 mg/d', choices=[('','---------Select---------'),(1,'True'),(0,'False')],validators=[InputRequired()])
    ECG = SelectField('Resting ECG', choices=[('','---------Select---------'),(0,'normal'),(1,'having ST-T wave abnormality'),(2,"showing probable or definite left ventricular hypertrophy by Estes' criteria")],validators=[InputRequired()])
    Thalach = DecimalField('Maximum heart rate achieved', validators=[ NumberRange(min=30,max=300,message="Enter Correct Value"), InputRequired()])
    Exang = SelectField('Exercise induced angina', choices=[('','---------Select---------'),(0,'No'),(1,'Yes')],validators=[InputRequired()])
    OldPeak = DecimalField('ST depression induced by exercise relative to rest', validators=[NumberRange(min=0,max=15,message="Enter Correct Value"), InputRequired()])
    Slope = SelectField('The slope of the peak exercise ST segment', choices=[('','---------Select---------'),(1,'Upsloping'),(2,'Flat'),(3,"Downsloping")],validators=[InputRequired()])
    Ca = SelectField('Number of major vessels (0-3) colored by flourosopy', choices=[('','---------Select---------'),(0,'Zero'),(1,'One'),(2,"Two"),(3,'Three')],validators=[InputRequired()])
    Thal = DecimalField('Thalassemia (1-7) 3 = normal; 6 = fixed defect; 7 = reversable defect',validators=[InputRequired(),NumberRange(min=0,max=7)])

class CompleteDiagnostics(FlaskForm):
    Pulse4 = DecimalField('Pulse ( beats  per minute )', validators=[ NumberRange(min=30,max=300,message="Enter Correct Value"),InputRequired()] )
    NYHA4 = SelectField('NYHA', choices=[('','---------Select---------'),(1,'1'),(2,'2'),(3,'3'),(4,'4')],validators=[InputRequired()])
    Killip4 = SelectField('Killip Grade', choices=[('','---------Select---------'),(1,'1'),(2,'2'),(3,'3'),(4,'4')],validators=[InputRequired()])
    BNP4 = DecimalField('Brain Natriuretic Peptide ( pg/ml )', validators=[ NumberRange(min=1, max=8001, message='Enter Correct Value'),InputRequired()])
    Cystatin4 = DecimalField('Cystatin ( mg/l )', validators=[NumberRange(min=0,max=7,message="Enter Correct Value"), InputRequired()])
    Potassium4 = DecimalField('Potassium ( mmol/L )', validators=[NumberRange(min=0,max=10,message="Enter Correct Value"), InputRequired()])
    SystolicBP4 = DecimalField('Systolic Blood Presure ( mm/Hg )', validators=[NumberRange(min=30,max=300,message="Enter Correct Value"), InputRequired() ])
    BMI4 = DecimalField('Body Mass Index', validators=[NumberRange(min=10,max=50,message="Enter Correct Value"), InputRequired()])
    LVEDD4 = DecimalField('Left Ventricular End Diastolic Diameter LV ( mm )', validators=[NumberRange(min=5,max=200,message="Enter Correct Value"), InputRequired()])
    CreatnineKinase4 = DecimalField('Creatnine Kinase ( U/L )', validators=[NumberRange(min=30,max=300,message="Enter Correct Value"), InputRequired()])
    Cholestrol4 = DecimalField('Cholestrol ( mmol/L )', validators=[NumberRange(min=0,max=10,message="Enter Correct Value"),InputRequired()])
    CEM4 = DecimalField('Creatinine Enzymetic Method ( umol/L )', validators=[NumberRange(min=30,max=300,message="Enter Correct Value"), InputRequired()])
    Age4 = DecimalField('Age', validators=[NumberRange(min=1,max=130,message="Enter Correct Value"),  InputRequired()] )
    Sex4 = SelectField('Sex', choices=[('','---------Select---------'),(1,'Male'),(0,'Female')],validators=[InputRequired()])
    CP4 = SelectField('Chest Pain type', choices=[('','---------Select---------'),(1,' typical angina'),(2,' atypical angina'),(3,' non-anginal pain'),(4,' asymptomatic')],validators=[InputRequired()])
    BP4 = DecimalField('Resting Blood Pressure', validators=[NumberRange(min=30,max=300,message="Enter Correct Value"), InputRequired()])
    FBS4 = SelectField('Fasting Blood Sugar > 120 mg/d', choices=[('','---------Select---------'),(1,'True'),(0,'False')],validators=[InputRequired()])
    ECG4 = SelectField('Resting ECG', choices=[('','---------Select---------'),(0,'normal'),(1,'having ST-T wave abnormality'),(2,"showing probable or definite left ventricular hypertrophy by Estes' criteria")],validators=[InputRequired()])
    Thalach4 = DecimalField(' Maximum heart rate achieved', validators=[NumberRange(min=30,max=300,message="Enter Correct Value"), InputRequired()])
    Exang4 = SelectField('Exercise induced angina', choices=[('','---------Select---------'),(0,'No'),(1,'Yes')],validators=[InputRequired()])
    OldPeak4 = DecimalField('ST depression induced by exercise relative to rest', validators=[NumberRange(min=0,max=15,message="Enter Correct Value"), InputRequired()])
    Slope4 = SelectField('the slope of the peak exercise ST segment', choices=[('','---------Select---------'),(1,'Upsloping'),(2,'Flat'),(3,"Downsloping")],validators=[InputRequired()])
    Ca4 = SelectField('number of major vessels (0-3) colored by flourosopy', choices=[('','---------Select---------'),(0,'Zero'),(1,'One'),(2,"Two"),(3,'Three')],validators=[InputRequired()])
    Thal4 = IntegerField('Thalassemia (1-7) 3 = normal; 6 = fixed defect; 7 = reversable defect',validators=[InputRequired(),NumberRange(min=0,max=7)])

class HFDiagnostics(FlaskForm):
    Pulse2 = DecimalField('Pulse ( beats per minute )', validators=[NumberRange(min=30,max=300,message="Enter Correct Value"), InputRequired() ])
    SystolicBP = DecimalField('Systolic Blood Presure ( mm/Hg )', validators=[ NumberRange(min=30,max=300,message="Enter Correct Value"),        InputRequired() ])
    BMI = DecimalField('Body Mass Index', validators=[NumberRange(min=10,max=50,message="Enter Correct Value"), InputRequired()])
    LVEDD = DecimalField('Left Ventricular End Diastolic Diameter LV ( mm )', validators=[NumberRange(min=5,max=200,message="Enter Correct Value"),        InputRequired()])
    BNP2 = DecimalField('Brain Natriuretic Peptide ( pg/ml )', validators=[ NumberRange(min=1,max=8001,message="Enter Correct Value"),        InputRequired()])
    CreatnineKinase = DecimalField('Creatnine Kinase ( U/L )', validators=[NumberRange(min=10,max=300,message="Enter Correct Value"),         InputRequired()])
    Cholestrol = DecimalField('Cholestrol ( mmol/L )', validators=[  NumberRange(min=0,max=10,message="Enter Correct Value"),     InputRequired()])
    CEM = DecimalField('Creatinine Enzymetic Method ( umol/L )', validators=[ NumberRange(min=30,max=300,message="Enter Correct Value"), InputRequired()])
    Potassium2 = DecimalField('Potassium ( mmol/L )', validators=[ NumberRange(min=0,max=10,message="Enter Correct Value"),  InputRequired()])

