from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, IntegerField , SubmitField, RadioField, SelectField
from wtforms.validators import InputRequired, Email, Length
from wtforms.fields.html5 import EmailField
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
import pickle
import os
import os.path
from os import path
from wtforms.widgets import TextArea
import sys
from datetime import datetime
# import model
import create_graphs
import seaborn as sns
import matplotlib.pyplot as plt, mpld3
import numpy as np
import sqlite3
from flask import g
app = Flask(__name__)
mail = Mail(app)

# configuration of mail 
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'ashishmishrajune2000@gmail.com'
app.config['MAIL_PASSWORD'] = 'zgyhqvfcichqxfig'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('database.db')
    return db

# import seaborn as sns
# import matplotlib.pyplot as plt, mpld3
# import numpy as np
# def create_graphs(patient_id, feature_name, feature_data, date_data, single_feature=True,feature_name2 = None):
#     '''
#     patient_id = number or string
#     feature_data = Primary featuredata
#     date_data = Dates if single_feature=True (default)
#         otherwise enter data of feature2
#     if single_feature = True then provide feature_name2
#     '''
#     plt.style.use("seaborn")
#     # plt.tick_params(axis='both',labelsize=20)
#     figure,ax = plt.subplots()
    
#     # ax.yaxis.set_tick_params(labelsize=20)
#     ax.grid(False)
#     ax.autoscale(enable=True)

#     if single_feature:
#         if len(feature_data)!= len(date_data):
#             raise Exception("The date and data have different lengths")
#         line1 = ax.plot(date_data,feature_data,marker='o',markerfacecolor= 'black',ls="--",lw=3,)
        
#         ax.set_xlabel("Date-Time Stamp",fontsize=14)
#         ax.set_ylabel(feature_name,fontsize=14)
#         title = feature_name+" data for "+str(patient_id)
#         ax.set_xticklabels(date_data, fontsize=15)
#         ax.tick_params(axis='x', labelrotation=45)



#         ax.set_title(title,fontsize=16)
#     else:
#         line1 = ax.plot(date_data,feature_data,c='black',marker="o",ls='-')
#         ax.set_xlabel(feature_name2,fontsize=12)
#         ax.set_ylabel(feature_name,fontsize=12)
#         title = feature_name+" vs "+ feature_name2 + " data for "+str(patient_id)
#         ax.set_title(title,fontsize=16)
#         if len(feature_data)!= len(data_data):
#             raise Exception("The feature 1 and 2 have different lengths")
#     html_graph = mpld3.fig_to_html(figure)
#     return html_graph

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv



class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    DocName = db.Column(db.String(100))
    DocId = db.Column(db.String(50), unique=True)
    DocHospital = db.Column(db.String(100))
    Email = db.Column(db.String(100))
    password = db.Column(db.String(80))


class Patient(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    PatientName = db.Column(db.String(100))
    PatientId = db.Column(db.String(50), unique=True)
    PatientDocId = db.Column(db.String(50))
    PatientDate = db.Column(db.DateTime, nullable=False,
                            default=datetime.utcnow)

class PatientDiagnostics(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    PatientId = db.Column(db.String(50))
    PatientDocId = db.Column(db.String(50) )
    DiagnosticsDate = db.Column(db.DateTime, nullable=False,
                            default=datetime.utcnow)
    DiagnosticsFor = db.Column(db.Integer, nullable=False)

class TokenTable(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    DocId = db.Column(db.String(50),nullable=False )
    Token = db.Column(db.String(10),nullable=False)
    TokenTime = db.Column(db.DateTime,nullable=False, default=datetime.utcnow)
    

class CHF(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    PatientId = db.Column(db.String(50))
    PatientDocId = db.Column(db.String(50) )
    DiagnosticsId = db.Column(db.Integer, nullable=False , unique=True)
    Pulse = db.Column(db.String(100),nullable=False)
    NYHA = db.Column(db.String(100),nullable=False)
    Killip = db.Column(db.String(100),nullable=False)
    BNP = db.Column(db.String(100),nullable=False)
    Cystatin = db.Column(db.String(100),nullable=False)
    Potassium = db.Column(db.String(100),nullable=False)
    DiagnosticsDate = db.Column(db.DateTime, nullable=False,default=datetime.utcnow)
    Result=db.Column(db.String(100), nullable=False)

class HF(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    PatientId = db.Column(db.String(50))
    PatientDocId = db.Column(db.String(50) ),
    DiagnosticsId = db.Column(db.Integer, nullable=False , unique=True)
    Pulse = db.Column(db.String(100),nullable=False)
    SystolicBP = db.Column(db.String(100),nullable=False)
    LVEDD = db.Column(db.String(100),nullable=False)
    BNP = db.Column(db.String(100),nullable=False)
    CreatnineKinase = db.Column(db.String(100),nullable=False)
    Cholestrol = db.Column(db.String(100),nullable=False)
    CEM = db.Column(db.String(100),nullable=False)
    Potassium = db.Column(db.String(100),nullable=False)
    DiagnosticsDate = db.Column(db.DateTime, nullable=False,default=datetime.utcnow)
    Result=db.Column(db.String(100), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class LoginForm(FlaskForm):
    username = StringField('username', validators=[
                           InputRequired(), Length(min=1, max=15)])
    password = PasswordField('password', validators=[
                             InputRequired(), Length(min=1, max=80)])
    remember = BooleanField('remember me')


class UsernameForm(FlaskForm):

    Email = EmailField('Email', validators=[
                          InputRequired(), Length(max=100)])


class RegisterForm(FlaskForm):
    DocName = StringField('Name', validators=[
                          InputRequired(), Length(max=100)])
    DocHospital = StringField('Hospital', validators=[
                              InputRequired(), Length(max=100)])
    Email = EmailField('Email', validators=[
                          InputRequired(), Length(max=100)])
    password = PasswordField('password', validators=[
                             InputRequired(), Length(min=8, max=80)])


class PatientForm(FlaskForm):
    PatientName = StringField('Patient Name', validators=[
        InputRequired(), Length(max=100)])
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
    message = StringField('message', widget=TextArea())
    
class StatsSelector(FlaskForm):
    Feature1 = SelectField('Label1', choices=[('BNP','Brain Natriuretic Peptide'),('Cholestrol','Cholestrol'),('CEM','Creatnine Enzymetic Method'),('CreatnineKinase','Creatnine Kinase'),('Cystatin','Cystatin'),('Killip','Killip Grade'),('LVEDD','left ventricular end diastolic diameter LV'),('NYHA','NYHA Cardiac Function Classification'),('Potassium','Potassium'),('Pulse','Pulse'),('SystolicBP','Systolic Blood Presure')])
    Feature2 = SelectField('Label2', choices=[('Date','Date'),('BNP','Brain Natriuretic Peptide'),('Cholestrol','Cholestrol'),('CEM','Creatnine Enzymetic Method'),('CreatnineKinase','Creatnine Kinase'),('Cystatin','Cystatin'),('Killip','Killip Grade'),('LVEDD','left ventricular end diastolic diameter LV'),('NYHA','NYHA Cardiac Function Classification'),('Potassium','Potassium'),('Pulse','Pulse'),('SystolicBP','Systolic Blood Presure')])



class CHFDiagnostics(FlaskForm):
    Pulse = StringField('Pulse', validators=[
        InputRequired() , Length(max=100)])
    NYHA = StringField('NYHA cardiac function classification', validators=[
        InputRequired(), Length(max=100)])
    Killip = StringField('Killip Grade', validators=[
        InputRequired(), Length(max=100)])
    BNP = StringField('Brain Natriuretic Peptide', validators=[
        InputRequired(), Length(max=100)])
    Cystatin = StringField('Cystatin', validators=[
        InputRequired(), Length(max=100)])
    Potassium = StringField('Potassium', validators=[
        InputRequired(), Length(max=100)])
    CHFsubmit = SubmitField('Submit')



class HFDiagnostics(FlaskForm):
    Pulse2 = StringField('Pulse', validators=[
        InputRequired(), Length(max=100) ])
    SystolicBP = StringField('Systolic Blood Presure', validators=[
        InputRequired(), Length(max=100) ])
    LVEDD = StringField('left ventricular end diastolic diameter LV', validators=[
        InputRequired(), Length(max=100)])
    BNP2 = StringField('Brain Natriuretic Peptide', validators=[
        InputRequired(), Length(max=100)])
    CreatnineKinase = StringField('Creatnine Kinase', validators=[
        InputRequired(), Length(max=100)])
    Cholestrol = StringField('Cholestrol', validators=[
        InputRequired(), Length(max=100)])
    CEM = StringField('Creatinine Enzymetic Method', validators=[
        InputRequired(), Length(max=100)])
    Potassium2 = StringField('Potassium', validators=[
        InputRequired(), Length(max=100)])
    HFsubmit = SubmitField('Submit')

@app.route('/')
def index():

    if os.path.exists("Patient-Counter.txt")==False :
        f = open("Patient-Counter.txt", "w+")
        f.write("0")
        f.close()
    if os.path.exists("Doctor-Counter.txt")==False :
        f = open("Doctor-Counter.txt", "w+")
        f.write("0")
        f.close()
    if os.path.exists("Diagnostics-Counter.txt")==False :
        f = open("Diagnostics-Counter.txt", "w+")
        f.write("0")
        f.close()
    if os.path.exists("database.db")==False :
        os.system('python database.py')
    form = PatientForm()
    path = os.getcwd()+'/Patient-Counter.txt'
    f = open(path, 'r')
    PatientNum = int(f.read())
    path = os.getcwd()+'/Doctor-Counter.txt'
    f = open(path, 'r')
    DocNum = int(f.read())
    path = os.getcwd()+'/Diagnostics-Counter.txt'
    f = open(path, 'r')
    DiagNum = int(f.read())
    if current_user.is_authenticated :
        return redirect(url_for('dashboard'))
    else:
        return render_template('index.html',patient=PatientNum,doc=DocNum,diag=DiagNum)

import math, random 
  

def GenerateToken() : 
  
    
    string = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    Token = "" 
    length = len(string) 
    for i in range(6) : 
        Token += string[math.floor(random.random() * length)] 
  
    return Token 
  


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form=TokenForm()
    form_password =NewPassword()
    if request.method == 'POST':
        if request.form.get("changepassword"):
            
            token = GenerateToken()
            email = query_db("select Email from User where DocId ='"+current_user.DocId+"' ;")
            
            TokenTable.query.filter_by(DocId=current_user.DocId).delete()

            
            new_record = TokenTable(   DocId=current_user.DocId,Token=token)
            db.session.add(new_record)
            db.session.commit()
            
            email=np.array(email)
            email=email[0,0]
            email=str(email)
            msg = Message( 
                'Security Key For HDAD', 
                sender ='ashishmishrajune2000@gmail.com', 
                recipients = [email] 
               ) 
            msg.body = "Your request to change your password has been processed.\nYour security key:"+token+"\n\nNote: It is valid only for 10 minutes"
            mail.send(msg)
           
            return render_template('profile-password.html', name=current_user.DocName,message="password",form=form)
        elif request.form.get("email"):
            return render_template('profile.html', name=current_user.DocName,message="email")
        elif request.form.get("token"):
            if form.validate_on_submit():
                security_key=form.Token.data
                creation_time = query_db("select TokenTime from token_table where DocId ='"+current_user.DocId+"' ;")
                creation_time =np.array(creation_time)
                creation_time=creation_time[0,0]

                print(creation_time)
                creation_time=datetime.strptime(str(creation_time), '%Y-%m-%d %H:%M:%S.%f')
                stored_token=query_db("select Token from token_table where DocId ='"+current_user.DocId+"' ;")
                stored_token = np.array(stored_token)
                stored_token=str(stored_token[0,0])
                print(stored_token)
                stored_token = str(stored_token)
                current_time=datetime.utcnow()
                time_taken = current_time - creation_time
                minutes = time_taken.seconds / 60
                if minutes > 10:
                    # query_db("delete from token_table where DocId ='"+current_user.DocId+"' ;")
                    return render_template('profile.html', name=current_user.DocName,message="Security Key Expired ")
                else :
                    
                    if stored_token == security_key:
                        return render_template('profile-password-input.html', name=current_user.DocName,message=minutes,form_password=form_password)
                    else :
                        return render_template('profile-password.html', name=current_user.DocName,message="TRY AGAIN",form_password=form)
            else :
                redirect(url_for('profile'))

            if form_password.validate_on_submit():
            
                if form_password.password.data == form_password.Confirmpassword.data :
                    hashed_password = generate_password_hash(
                    form_password.password.data, method='sha256')
                    admin = User.query.filter_by(DocId=current_user.DocId).first()
                    admin.password = hashed_password
                    db.session.commit()
                    logout()
                    return redirect(url_for('dashboard'))
                else :                    
                    return render_template('profile-password-input.html', name=current_user.DocName,message="Those passwords didn’t match. Try again.",form_password=form_password)
            else:
                return render_template('profile-password-input.html', name=current_user.DocName,message="Password must be minimum 8 and maximum 80 character long.",form_password=form_password)
        else :
            redirect(url_for('profile'))
    else:   
        return render_template('profile.html', name=current_user.DocName,message="")


@app.route('/username', methods=['GET', 'POST'])
def usernamerecovery():
    form = UsernameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(Email=form.Email.data).first()
        if user:
            msg = Message( 
                'HDAD Username', 
                sender ='ashishmishrajune2000@gmail.com', 
                recipients = [form.Email.data] 
               ) 
            msg.body = "Hello "+user.DocName+" your HDAD username is "+user.DocId+" ."
            mail.send(msg)
            return render_template("DocId.html",message="Your username has been sent to your email")
        else :
            return render_template('username.html', form=form,message="No account associated with the email address")
         
    return render_template('username.html', form=form,message="")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(DocId=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('dashboard'))

        return render_template('login.html', form=form,message="Invalid username or password")

    return render_template('login.html', form=form,message="")


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = PatientForm()
    chfform = CHFDiagnostics()
    hfform = HFDiagnostics()
    data = Patient.query.filter_by(PatientDocId=current_user.DocId).order_by(Patient.id.desc()).all()
    Diagdata = PatientDiagnostics.query.filter_by(PatientDocId=current_user.DocId).order_by(PatientDiagnostics.id.desc()).all()
    chf = CHF.query.filter_by(PatientDocId=current_user.DocId).order_by(CHF.id.desc()).all()
    hf1 = HF.query.filter_by(PatientDocId=current_user.DocId).order_by(HF.id.desc()).all()
    if request.method == 'POST':

        if form.validate_on_submit():
            path = os.getcwd()+'/Patient-Counter.txt'
            f = open(path, 'r')
            PatientNum = str(f.read())
            f.close()
            if int(PatientNum) < 10:
                ID = 'PA000' + PatientNum
            elif int(PatientNum) < 100:
                ID = 'PA00' + PatientNum
            elif int(PatientNum) < 1000:
                ID = 'PA0' + PatientNum
            elif int(PatientNum) < 10000:
                ID = 'PA' + PatientNum

            new_user = Patient(
                PatientName=form.PatientName.data,
                PatientId=ID, PatientDocId=current_user.DocId)
            db.session.add(new_user)
            db.session.commit()
            f = open(path, 'w')
            f.write(str(int(PatientNum)+1))
            f.close()
            return redirect(url_for('dashboard'))
            # return render_template('PatientId.html', ID=ID, name=current_user.DocName,data=data)
            # return '<h1>New user has been created! Your Username is : ' + ID + '</h1>'
        elif chfform.validate_on_submit() and  request.form.get("submitchf"):
            pulse = chfform.Pulse.data
            nyha = chfform.NYHA.data
            killip = chfform.Killip.data
            bnp = chfform.BNP.data
            cystatin = chfform.Cystatin.data
            potassium = chfform.Potassium.data

            pulse = int(pulse)
            nyha = int(nyha)
            killip = int(killip)
            bnp = int(bnp)
            cystatin = int(cystatin)
            potassium = int(potassium)
            Xdata = [ [pulse,nyha,killip,bnp,cystatin,potassium ] ]
            with open('CHF_Detection_Model.pkl', 'rb') as f:
                clf = pickle.load(f)
            x=clf.predict(Xdata)

            if x == 1:
               message="Patient Have Congestive Heart Failure"
            elif x == 0:
                message="Patient Does Not Have Congestive Heart Failure"
            else:
                message="error"
            path = os.getcwd()+'/Diagnostics-Counter.txt'
            f = open(path, 'r')
            DiagnosticsCounter = int(f.read())
            f.close()
            f = open(path, 'w')
            f.write(str(DiagnosticsCounter+1))
            f.close()
            return render_template('dashboard.html', name=current_user.DocName, form=form,data=data,diagdata=Diagdata,chf=chf,hf=hf1,formnum=2,chfform=chfform, hfform=hfform,message=message,message2="")
        elif hfform.validate_on_submit() and  request.form.get("submithf"):
            pulse = hfform.Pulse2.data
            systolicbp = hfform.SystolicBP.data
            lvedd = hfform.LVEDD.data
            bnp = hfform.BNP2.data
            creatnine=hfform.CreatnineKinase.data
            cholestrol = hfform.Cholestrol.data
            cem = hfform.CEM.data
            potassium = hfform.Potassium2.data

            pulse = int(pulse)      
            systolicbp = int(systolicbp)
            lvedd = int(lvedd)
            bnp = int(bnp)
            creatnine = int(creatnine)
            cholestrol = int(cholestrol)
            cem = int(cem)
            potassium = int(potassium)
            Xdata = [ [pulse,systolicbp,lvedd,bnp,creatnine,cholestrol,cem,potassium ] ]
            with open('HF_Classification_Model.pkl', 'rb') as f:
                clf = pickle.load(f)
            x=clf.predict(Xdata)
            
            if x == 1:
               message2="Patient Have HFpEF"
            elif x == 0:
                message2="Patient Have HFrEF"
            else:
                message2="error"
            path = os.getcwd()+'/Diagnostics-Counter.txt'
            f = open(path, 'r')
            DiagnosticsCounter = int(f.read())
            f.close()
            f = open(path, 'w')
            f.write(str(DiagnosticsCounter+1))
            f.close()
            return render_template('dashboard.html', name=current_user.DocName, form=form,data=data,diagdata=Diagdata,chf=chf,hf=hf1,formnum=3,chfform=chfform,hfform=hfform,message2=message2,message="")
    else:
        return render_template('dashboard.html', name=current_user.DocName, form=form,data=data,diagdata=Diagdata,chf=chf,hf=hf1,chfform=chfform,hfform=hfform,fornnum=0,message="",message2="")

@app.route('/diagnostics', methods=['GET', 'POST'])
@login_required
def diagnostics():
    return render_template('diagnostics.html')

# @app.route('/images', methods=['GET', 'POST'])
# def image():
#     pid = "4520"
#     fname = "feature"
#     fdata = [10,12,14]
#     date = ["1","2","3"]
    
#     image = create_graphs(pid,fname,fdata,date)
#     return render_template("image.html",img=image)

@app.route('/chf-diagnostics', methods=['GET', 'POST'])
@login_required
def chfDiagnostics():
    form = CHFDiagnostics()
    if request.method == 'POST':

        if form.validate_on_submit():
            PatientId = form.PatientId.data
            pulse = form.Pulse.data
            respiration = form.Respiration.data
            nyha = form.NYHA.data
            killip = form.Killip.data
            fio2 = form.Fio2.data
            lvedd = form.LVEDD.data
            bnp = form.BNP.data
            cystatin = form.Cystatin.data
            hst = form.HST.data
            
            new_record = PatientDiagnostics(PatientId=PatientId, PatientDocId=current_user.DocId, DiagnosticsFor=2)
            db.session.add(new_record)
            db.session.commit()
            DiagnosticsId = PatientDiagnostics.query.filter_by(PatientId=form.PatientId.data).order_by(PatientDiagnostics.id.desc()).first()
            if DiagnosticsId:
                chf = CHF(DiagnosticsId=DiagnosticsId.id, Pulse=pulse, Respiration=respiration, NYHA=nyha, Killip=killip,Fio2=fio2,LVEDD=lvedd,BNP=bnp,Cystatin=cystatin,HST=hst)
                db.session.add(chf)
                db.session.commit()

            pulse = int(pulse)
            respiration = int(respiration)
            nyha = int(nyha)
            killip = int(killip)
            fio2 = int(fio2)
            lvedd = int(lvedd)
            bnp = int(bnp)
            cystatin = int(cystatin)
            hst = int(hst)

            data = [ [pulse,respiration,nyha,killip,fio2,lvedd,bnp,cystatin,hst ] ]
            x=model(data)

            if x == 1:
                return render_template('message.html',message="Patient Have Congestive Heart Failure")
            elif x == 0:
                return render_template('message.html',message="Patient Does Not Have Congestive Heart Failure")
            else:
                return '<h1>error</h1>'
            # return '<h1>New user has been created! Your Username is : ' + ID + '</h1>'
    else:
        return render_template('chf-diagnostics.html', form=form)


@app.route('/<pid>',methods=['GET', 'POST'])
@login_required
def showpatient(pid):
    featureform = StatsSelector()
    chfform = CHFDiagnostics()
    hfform = HFDiagnostics()
    alert = MailForm()
    Patientdata = Patient.query.filter_by(PatientId=pid).first()
    Diagnostics = PatientDiagnostics.query.filter_by(PatientId=pid).order_by(PatientDiagnostics.id.desc()).first()
    chf = CHF.query.filter_by(PatientId=pid).order_by(CHF.id.desc()).all()
    hf = HF.query.filter_by(PatientId=pid).order_by(HF.id.desc()).all()
    diag = PatientDiagnostics.query.filter_by(PatientId=pid).order_by(PatientDiagnostics.id.desc()).all()
    if Diagnostics:
        lastDiagDate = Diagnostics.DiagnosticsDate.strftime("%d/%m/%Y")
    else :
        lastDiagDate = "---"
    if request.method == 'POST':
        if chfform.validate_on_submit() and  request.form.get("save"):
            pulse = chfform.Pulse.data
            nyha = chfform.NYHA.data
            killip = chfform.Killip.data
            bnp = chfform.BNP.data
            cystatin = chfform.Cystatin.data
            potassium = chfform.Potassium.data

            pulse = int(pulse)      
            nyha = int(nyha)
            killip = int(killip)
            bnp = int(bnp)
            cystatin = int(cystatin)
            potassium = int(potassium)
            Xdata = [ [pulse,nyha,killip,bnp,cystatin,potassium ] ]
            with open('CHF_Detection_Model.pkl', 'rb') as f:
                clf = pickle.load(f)
            x=clf.predict(Xdata)
            
            if x == 1:
               result="yes"
            elif x == 0:
                result="no"
            else:
                result="error"

            new_record = PatientDiagnostics(PatientId=Patientdata.PatientId, PatientDocId=current_user.DocId, DiagnosticsFor=2)
            db.session.add(new_record)
            db.session.commit()
            DiagnosticsId = PatientDiagnostics.query.filter_by(PatientId=Patientdata.PatientId).order_by(PatientDiagnostics.id.desc()).first()
            if DiagnosticsId:
                chf = CHF(DiagnosticsId=DiagnosticsId.id,PatientId=pid,PatientDocId=current_user.DocId, Pulse=pulse, NYHA=nyha, Killip=killip,BNP=bnp,Cystatin=cystatin,Potassium=potassium,Result=result)
                db.session.add(chf)
                db.session.commit()
            path = os.getcwd()+'/Diagnostics-Counter.txt'
            f = open(path, 'r')
            DiagnosticsCounter = int(f.read())
            f.close()
            f = open(path, 'w')
            f.write(str(DiagnosticsCounter+1))
            f.close()
            return redirect(url_for('showpatient',pid=pid))
            
            
        elif chfform.validate_on_submit() and  request.form.get("submitchf"):
            pulse = chfform.Pulse.data
            nyha = chfform.NYHA.data
            killip = chfform.Killip.data
            bnp = chfform.BNP.data
            cystatin = chfform.Cystatin.data
            potassium = chfform.Potassium.data

            pulse = int(pulse)
            nyha = int(nyha)
            killip = int(killip)
            bnp = int(bnp)
            cystatin = int(cystatin)
            potassium = int(potassium)
            Xdata = [ [pulse,nyha,killip,bnp,cystatin,potassium ] ]
            with open('CHF_Detection_Model.pkl', 'rb') as f:
                clf = pickle.load(f)
            x=clf.predict(Xdata)

            if x == 1:
               message="Patient Have Congestive Heart Failure"
            elif x == 0:
                message="Patient Does Not Have Congestive Heart Failure"
            else:
                message="error"
            path = os.getcwd()+'/Diagnostics-Counter.txt'
            f = open(path, 'r')
            DiagnosticsCounter = int(f.read())
            f.close()
            f = open(path, 'w')
            f.write(str(DiagnosticsCounter+1))
            f.close()
            return render_template('patientdetails.html',name=current_user.DocName,data=Patientdata,diagdata=diag,dd=lastDiagDate,chfform=chfform, hfform=hfform,form=2, message=message,message2="",alert=alert,chf=chf,hf=hf,featureform=featureform)
        elif alert.validate_on_submit() and  request.form.get("alert"):
            email = alert.email.data
            message = alert.message.data
            msg = Message( 
                'Alert', 
                sender ='ashishmishrajune2000@gmail.com', 
                recipients = [email] 
               ) 
            msg.body = message
            mail.send(msg)
            return redirect(url_for('showpatient',pid=pid))
        elif hfform.validate_on_submit() and  request.form.get("save"):
            pulse = hfform.Pulse2.data
            systolicbp = hfform.SystolicBP.data
            lvedd = hfform.LVEDD.data
            bnp = hfform.BNP2.data
            creatnine=hfform.CreatnineKinase.data
            cholestrol = hfform.Cholestrol.data
            cem = hfform.CEM.data
            potassium = hfform.Potassium2.data

            pulse = int(pulse)      
            systolicbp = int(systolicbp)
            lvedd = int(lvedd)
            bnp = int(bnp)
            creatnine = int(creatnine)
            cholestrol = int(cholestrol)
            cem = int(cem)
            potassium = int(potassium)
            Xdata = [ [pulse,systolicbp,lvedd,bnp,creatnine,cholestrol,cem,potassium ] ]
            with open('HF_Classification_Model.pkl', 'rb') as f:
                clf = pickle.load(f)
            x=clf.predict(Xdata)
            
            if x == 1:
               result="HFpEF"
            elif x == 0:
                result="HFrEF"
            else:
                result="error"

            new_record = PatientDiagnostics(PatientId=Patientdata.PatientId, PatientDocId=current_user.DocId, DiagnosticsFor=3)
            db.session.add(new_record)
            db.session.commit()
            DiagnosticsId = PatientDiagnostics.query.filter_by(PatientId=Patientdata.PatientId).order_by(PatientDiagnostics.id.desc()).first()
            if DiagnosticsId:
                hf = HF(DiagnosticsId=DiagnosticsId.id,PatientId=pid,PatientDocId=current_user.DocId, Pulse=pulse, SystolicBP=systolicbp,LVEDD=lvedd,BNP=bnp,CreatnineKinase=creatnine,Cholestrol=cholestrol,CEM=cem,Potassium=potassium,Result=result)
                db.session.add(hf)
                db.session.commit()
            path = os.getcwd()+'/Diagnostics-Counter.txt'
            f = open(path, 'r')
            DiagnosticsCounter = int(f.read())
            f.close()
            f = open(path, 'w')
            f.write(str(DiagnosticsCounter+1))
            f.close()
            return redirect(url_for('showpatient',pid=pid))
        elif hfform.validate_on_submit() and  request.form.get("submithf"):
            pulse = hfform.Pulse2.data
            systolicbp = hfform.SystolicBP.data
            lvedd = hfform.LVEDD.data
            bnp = hfform.BNP2.data
            creatnine=hfform.CreatnineKinase.data
            cholestrol = hfform.Cholestrol.data
            cem = hfform.CEM.data
            potassium = hfform.Potassium2.data

            pulse = int(pulse)      
            systolicbp = int(systolicbp)
            lvedd = int(lvedd)
            bnp = int(bnp)
            creatnine = int(creatnine)
            cholestrol = int(cholestrol)
            cem = int(cem)
            potassium = int(potassium)
            Xdata = [ [pulse,systolicbp,lvedd,bnp,creatnine,cholestrol,cem,potassium ] ]
            with open('HF_Classification_Model.pkl', 'rb') as f:
                clf = pickle.load(f)
            x=clf.predict(Xdata)
            
            if x == 1:
               message2="Patient Have HFpEF"
            elif x == 0:
                message2="Patient Have HFrEF"
            else:
                message2="error"
            path = os.getcwd()+'/Diagnostics-Counter.txt'
            f = open(path, 'r')
            DiagnosticsCounter = int(f.read())
            f.close()
            f = open(path, 'w')
            f.write(str(DiagnosticsCounter+1))
            f.close()
            return render_template('patientdetails.html',name=current_user.DocName,data=Patientdata,diagdata=diag,dd=lastDiagDate,chfform=chfform, hfform=hfform,form=3, message="",message2=message2,alert=alert,hf=hf,chf=chf,featureform=featureform)
        
        elif featureform.validate_on_submit and request.form.get("featureform"):
            common_feature = ["Pulse","BNP","Potassium"]
            chf_feature = ["NYHA","Killip","Cystatin"]
            hf_feature = ["SystolicBP","LVEDD","CreatnineKinase","Cholestrol","CEM"]
            if featureform.Feature2.data=='Date':
                try:
                    feature_data_hf =  query_db('select '+ featureform.Feature1.data+", DiagnosticsDate from HF where PatientId='"+pid+"';")
                except:
                    feature_data_hf =[]
                try:
                    feature_data_chf = query_db('select '+ featureform.Feature1.data+", DiagnosticsDate from CHF where PatientId='"+pid+"';") 
                except :
                    feature_data_chf = []
                
                feature_data = feature_data_hf+feature_data_chf
                    
                fname = featureform.Feature1.data
                feature_data=np.array(feature_data)
                print(feature_data)
                # feature_data=feature_data.flatten()
                fdata = feature_data[:,0]
                date = feature_data[:,1]
                print(feature_data)
                print(fdata)
                print(date)
                print(pid)
                print("------------")
                image = create_graphs(pid,fname,fdata,date)
                print("\n")
            else :
                
                try:
                    feature1_data_hf =  query_db('select '+ featureform.Feature1.data+", DiagnosticsId from HF where PatientId='"+pid+"';")
                except:
                    feature1_data_hf =[]
                try:
                    feature1_data_chf = query_db('select '+ featureform.Feature1.data+", DiagnosticsId from CHF where PatientId='"+pid+"';") 
                except :
                    feature1_data_chf = []
                
                feature1_data = feature1_data_hf+feature1_data_chf
                try:
                    feature2_data_hf =  query_db('select '+ featureform.Feature2.data+", DiagnosticsId from HF where PatientId='"+pid+"';")
                except:
                    feature2_data_hf =[]
                try:
                    feature2_data_chf = query_db('select '+ featureform.Feature2.data+", DiagnosticsId from CHF where PatientId='"+pid+"';") 
                except :
                    feature2_data_chf = []
                
                feature2_data = feature2_data_hf+feature2_data_chf

                
                f1name = featureform.Feature1.data
                f2name=featureform.Feature2.data
                feature1_data=np.array(feature1_data)
                feature2_data=np.array(feature2_data)
                print(feature2_data)
                print(feature1_data) 
                feature1_data = sorted(feature1_data,key=lambda x:(x[1]))
                feature1_data=np.array(feature1_data)
                feature2_data = sorted(feature2_data,key=lambda x:(x[1]))
                feature2_data=np.array(feature2_data)
                print(feature2_data)
                print(feature1_data)
                # feature_data=feature_data.flatten()
                fdata = feature1_data[:,0]
                date = feature2_data[:,0]

                print(fdata.shape)
                print(date.shape)
                if fdata.shape[0]>date.shape[0]:
                    fdata = fdata[0:date.shape[0]]
                elif fdata.shape[0]<date.shape[0]:
                    date = date[0:fdata.shape[0]]

                print(pid)
                print("------------")
                image = create_graphs(pid,f1name,fdata,date,False,f2name)
                print("\n")
            
            return render_template('patientdetails.html',name=current_user.DocName,data=Patientdata,diagdata=diag,dd=lastDiagDate,chfform=chfform, hfform=hfform, form=4, message="",message2="",alert=alert,chf=chf,hf=hf,image=image,featureform=featureform)
    return render_template('patientdetails.html',name=current_user.DocName,data=Patientdata,diagdata=diag,dd=lastDiagDate,chfform=chfform, hfform=hfform, form=0, message="",message2="",alert=alert,chf=chf,hf=hf,featureform=featureform)
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST':
        
        if form.validate_on_submit():
            path = os.getcwd()+'/Doctor-Counter.txt'
            f = open(path, 'r')
            DocNum = str(f.read())
            f.close()
            if int(DocNum) < 10:
                ID = 'Doc000' + DocNum
            elif int(DocNum) < 100:
                ID = 'Doc00' + DocNum
            elif int(DocNum) < 1000:
                ID = 'Doc0' + DocNum
            elif int(DocNum) < 10000:
                ID = 'Doc' + DocNum
            try:
                Email=query_db("select Email from User where Email='"+ form.Email.data +"';")
                print(Email)
                
            except:
                Email=[]
            if Email:
                return render_template('register.html', form=form,message='Accout with the entered Email already exists') 
            try:
                msg = Message( 
                    'HDAD Login Id ', 
                    sender ='ashishmishrajune2000@gmail.com', 
                    recipients = [form.Email.data] 
                ) 
                msg.body = 'Hello '+form.DocName.data+' your account has been created. \nYour Id is '+ID
                mail.send(msg)
            except:
                return render_template('register.html', form=form,message='Try Again')
               
            hashed_password = generate_password_hash(form.password.data, method='sha256')
            new_user = User(DocName=form.DocName.data, DocId=ID,DocHospital=form.DocHospital.data,Email= form.Email.data,password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            f = open(path, 'w')
            f.write(str(int(DocNum)+1))
            f.close()
                

            return render_template('DocId.html',message="Your Id has been sent to your mail")
            # return '<h1>New user has been created! Your Username is : ' + ID + '</h1>'
        else:
            return render_template('register.html', form=form,message='Password must be minimum 8 and maximum 80 character long')
    else:
        return render_template('register.html', form=form,message='')


# @app.route('/temp')
# @login_required
# def dashboard():
#     return render_template('dashboard.html', name=current_user.DocName)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
