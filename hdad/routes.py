from flask import render_template, redirect, url_for, request
from hdad.forms import LoginForm , UsernameForm , RegisterForm , PatientForm , TokenForm , NewPassword , MailForm , StatsSelector , CHFDiagnostics, CompleteDiagnostics , HFDiagnostics , ConfirmDelete , UploadCSV , UsernameRecoveryForm, PasswordRecoveryForm , HeartDiseaseDiagnostics
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import  Message
import pickle
import os
import os.path
from os import path
import sys
from flask import send_file, send_from_directory, safe_join, abort
import hdad.create_graphs as create_graphs
import seaborn as sns
import matplotlib.pyplot as plt, mpld3
import numpy as np
from flask import g
from io import TextIOWrapper
import pandas as pd
from hdad.models import User , Patient , PatientDiagnostics , TokenTable , CHF , HF ,HeartDisease
from hdad import mail , db , app , login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    if os.path.exists("hdad/Diagnostics-Counter.txt")==False :
        f = open("hdad/Diagnostics-Counter.txt", "w+")
        f.write("0")
        f.close()
    path = os.getcwd()+'/hdad/Diagnostics-Counter.txt'
    f = open(path, 'r')
    DiagNum = int(f.read())
    if current_user.is_authenticated :
        return redirect(url_for('dashboard'))
    else:
        return render_template('index.html',diag=DiagNum)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated :
        return redirect(url_for('dashboard'))
    form = LoginForm()

    if form.validate_on_submit():
        try :
            user = User.query.filter_by(DocId=form.username.data).first()
            if user:
                if check_password_hash(user.password, form.password.data):
                    login_user(user, remember=form.remember.data)
                    return redirect(url_for('dashboard'))

            return render_template('login.html', form=form,message="Invalid username or password")
        except :
            return render_template('login.html', form=form,message="Try Again")
 
        # return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'
    if current_user.is_authenticated :
        return redirect(url_for('dashboard'))
    else:
        return render_template('login.html', form=form,message="")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated :
        return redirect(url_for('dashboard'))
    form = RegisterForm()
    if request.method == 'POST':
        
        if form.validate_on_submit():
            
            try :    
                user = User.query.filter_by(Email=form.Email.data).first()
                Email = user.Email
            except :
                Email = 0
            try :
                  
                user = User.query.order_by(User.id.desc()).first()
                DocNum = user.DocId
                print(DocNum)
                DocNum = DocNum[3:]
                DocNum = int(DocNum)
                print(DocNum)
                if int(DocNum) < 10:
                    ID = 'Doc000' + str(DocNum+1)
                elif int(DocNum) < 100:
                    ID = 'Doc00' + str(DocNum+1)
                elif int(DocNum) < 1000:
                    ID = 'Doc0' + str(DocNum+1)
                elif int(DocNum) < 10000:
                    ID = 'Doc' + str(DocNum+1)
                print(ID)
            except :
               ID = 'Doc0000'
            print("here")
            if Email:
                return render_template('register.html', form=form,message='Account with this Email already exists') 
            try:
                msg = Message( 
                    'HDAD Login Id ', 
                    sender ='ashishmishrajune2000@gmail.com', 
                    recipients = [form.Email.data] 
                ) 
                msg.body = 'Hello '+form.DocName.data+' your account has been created. \nYour Id is '+ID
                mail.send(msg)
            except:
                return render_template('register.html', form=form,message='Message Cannot Be Sent. Try Again')
            
            try :
                hashed_password = generate_password_hash(form.password.data, method='sha256')
                new_user = User(DocName=form.DocName.data, DocId=ID,DocHospital=form.DocHospital.data,Email= form.Email.data,password=hashed_password)
                db.session.add(new_user)
                db.session.commit()
                
                    
                logout_user()
                return render_template('DocId.html',message="Your Id has been sent to your mail")
            except : 
                return render_template('register.html', form=form,message='Try Again')
        
            return render_template('register.html', form=form,message='Try Again')
        else:
            return render_template('register.html', form=form,message='')
    else:
        return render_template('register.html', form=form,message='')


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    csvform=UploadCSV()
    form = PatientForm()
    chfform = CHFDiagnostics()
    heartform = HeartDiseaseDiagnostics()
    completeform = CompleteDiagnostics()
    hfform = HFDiagnostics()
    try :
        data = Patient.query.filter_by(PatientDocId=current_user.DocId).order_by(Patient.id.desc()).all()
        Diagdata = PatientDiagnostics.query.filter_by(PatientDocId=current_user.DocId).order_by(PatientDiagnostics.id.desc()).all()
        chf = CHF.query.filter_by(PatientDocId=current_user.DocId).order_by(CHF.id.desc()).all()
        hf1 = HF.query.filter_by(PatientDocId=current_user.DocId).order_by(HF.id.desc()).all()
        heartlist = HeartDisease.query.filter_by(PatientDocId=current_user.DocId).order_by(HeartDisease.id.desc()).all()
    except :
        return render_template('error.html')

    if request.method == 'POST':
        # Patient Creation
        if form.validate_on_submit():
            try :
                patient = Patient.query.order_by(Patient.id.desc()).first()
                PaNum = patient.PatientId
                print(PaNum)
                PaNum = PaNum[2:]
                PaNum = int(PaNum)
                print(PaNum)
                if int(PaNum) < 10:
                    ID = 'PA000' + str(PaNum+1)
                elif int(PaNum) < 100:
                    ID = 'PA00' + str(PaNum+1)
                elif int(PaNum) < 1000:
                    ID = 'PA0' + str(PaNum+1)
                elif int(PaNum) < 10000:
                    ID = 'PA' + str(PaNum+1)
            except:
                ID="PA0000"
            try :
                new_user = Patient(PatientName=form.PatientName.data, PatientId=ID, PatientDocId=current_user.DocId)
                db.session.add(new_user)
                db.session.commit()
            except:
                return render_template('error.html')
            return redirect(url_for('dashboard'))
        # Upload CSV
        elif request.form.get("csvu"):
            patientCounter=0
            diagnosticsDetectionCounter=0
            diagnosticsExecutionCounter=0
            try:
                with open('hdad/CHF_Detection_Model.pkl', 'rb') as f:
                    clfchf = pickle.load(f)
            except :
                print("Cannot Import CHF Pickle")
            try :
                with open('hdad/HF_Classification_Model.pkl', 'rb') as f:
                    clfhf = pickle.load(f)
            except :
                print("Cannot Import HF Pickle")
            try:
                with open('hdad/Heart_disease_CatBoost_Model.pkl', 'rb') as f:
                    clfheart = pickle.load(f)
            except :
                print("Cannot Import Heart Pickle")
            try :
                csv_file = request.files['file']
                df = pd.read_csv(csv_file,encoding='latin1')
                df2 = df.copy()
                df = df[df['Name'].notna()]
                df.dropna()
                for X, y  in df.iterrows():
                    print(X)
                    DiagnosticsId=0
                    try :
                        patient = Patient.query.order_by(Patient.id.desc()).first()
                        PaNum = patient.PatientId
                        
                        PaNum = PaNum[2:]
                        PaNum = int(PaNum)
                        
                        if int(PaNum) < 10:
                            ID = 'PA000' + str(PaNum+1)
                        elif int(PaNum) < 100:
                            ID = 'PA00' + str(PaNum+1)
                        elif int(PaNum) < 1000:
                            ID = 'PA0' + str(PaNum+1)
                        elif int(PaNum) < 10000:
                            ID = 'PA' + str(PaNum+1)
                    except:
                        ID="PA0000"
                    new_user = Patient(
                        PatientName=y['Name'],
                        PatientId=ID, PatientDocId=current_user.DocId)
                    db.session.add(new_user)
                    db.session.commit()
                    patientCounter = patientCounter+1
                   
                    try:
                        chfflag=0
                        if y['Pulse'] and y['NYHA-Cardiac-Function-Classification'] and y['Killip-Grade'] and y['Brain-Natriuretic-Peptide'] and y['Cystatin'] and y['Potassium']:
                            diagnosticsDetectionCounter=diagnosticsDetectionCounter+1
                            print(f" Diagnostics Counter (CHF): {diagnosticsDetectionCounter}")
                            pulse = int(y['Pulse'])
                            nyha = int(y['NYHA-Cardiac-Function-Classification'])
                            killip = int(y['Killip-Grade'])
                            bnp = float(y['Brain-Natriuretic-Peptide'])
                            cystatin =  float(y['Cystatin'])
                            potassium = float(y['Potassium'])
                            if pulse <= 30 or pulse >= 300 or nyha not in [1,2,3,4] or killip not in [1,2,3,4] or bnp <1 or bnp>8001 or cystatin <=0 or cystatin >7 or potassium <=0 or potassium >10 :
                                chfflag = 1
                            
                            if chfflag == 0 :        
                                Xdata = [ [pulse,nyha,killip,bnp,cystatin,potassium ] ]
                                print(x)
                                if clfchf :
                                    x=clfchf.predict(Xdata)
                                    
                                    if x == 1:
                                        resultchf="Yes"
                                    elif x == 0:
                                        resultchf="No"
                                    else:
                                        resultchf="error"
                                    print("chf debug")
                                    new_record = PatientDiagnostics(PatientId=ID, PatientDocId=current_user.DocId, DiagnosticsFor=4)
                                    db.session.add(new_record)
                                    db.session.commit()
                                    DiagnosticsId = PatientDiagnostics.query.filter_by(PatientId=ID).order_by(PatientDiagnostics.id.desc()).first()
                                    if DiagnosticsId:
                                        chfNew = CHF(DiagnosticsId=DiagnosticsId.id,PatientId=ID,PatientDocId=current_user.DocId, Pulse=pulse, NYHA=nyha, Killip=killip,BNP=bnp,Cystatin=cystatin,Potassium=potassium,Result=resultchf)
                                        db.session.add(chfNew)
                                        db.session.commit()
                                        diagnosticsExecutionCounter=diagnosticsExecutionCounter+1
                    except :
                        print("Problem Running CHF ")
                    try :
                        hfflag= 0             
                        if y['Pulse'] and y['SystolicBP'] and y['BMI'] and y['left-ventricular-end-diastolic-diameter-LV'] and y['Brain-Natriuretic-Peptide'] and y['Creatnine-Enzymetic-Method'] and y['Potassium'] and y['Cholesterol'] and y['Creatnine-Kinase']:
                            diagnosticsDetectionCounter=diagnosticsDetectionCounter+1
                            print(f" Diagnostics Counter (HF): {diagnosticsDetectionCounter}")
                            pulse = int(y['Pulse'])
                            systolicbp = int(y['SystolicBP'])
                            bmi= float(y['BMI'])
                            lvedd = float(y['left-ventricular-end-diastolic-diameter-LV'])
                            bnp =  float(y['Brain-Natriuretic-Peptide'])
                            creatnine= float(y['Creatnine-Kinase'])
                            cholestrol = float(y['Cholesterol'])
                            cem = float(y['Creatnine-Enzymetic-Method'])
                            potassium = float(y['Potassium'])
                            
                            if pulse <30 or pulse>300 or systolicbp <30 or systolicbp>300 or bmi <10 or bmi > 50 or lvedd<=5 or lvedd >200 or bnp <1 or bnp >8000 or creatnine <30 or creatnine >300 or cem <30 or cem>300 or potassium <=0 or potassium >10 or cholestrol <=0 or cholestrol >7 :
                                hfflag=1
                            
                            if hfflag ==0 :
                                Xdata = [ [pulse,systolicbp,bmi,lvedd,bnp,creatnine,cholestrol,cem,potassium ] ]
                                print(Xdata)
                                if clfhf :
                                    x=clfhf.predict(Xdata)
                                    if x == 1:
                                        resulthf="HFpEF"
                                    elif x == 0:
                                        resulthf="HFrEF"
                                    else:
                                        resulthf="Error"

                                    if DiagnosticsId:
                                        hfNew = HF(DiagnosticsId=DiagnosticsId.id,PatientId=ID,PatientDocId=current_user.DocId, Pulse=pulse, SystolicBP=systolicbp,BMI=bmi,LVEDD=lvedd,BNP=bnp,CreatnineKinase=creatnine,Cholestrol=cholestrol,CEM=cem,Potassium=potassium,Result=resulthf)
                                        db.session.add(hfNew)
                                        db.session.commit()
                                        diagnosticsExecutionCounter=diagnosticsExecutionCounter+1
                                    else :
                                        new_record = PatientDiagnostics(PatientId=ID, PatientDocId=current_user.DocId, DiagnosticsFor=3)
                                        db.session.add(new_record)
                                        db.session.commit()
                                        DiagnosticsId = PatientDiagnostics.query.filter_by(PatientId=ID).order_by(PatientDiagnostics.id.desc()).first()
                                        if DiagnosticsId:
                                            hfNew = HF(DiagnosticsId=DiagnosticsId.id,PatientId=ID,PatientDocId=current_user.DocId, Pulse=pulse, SystolicBP=systolicbp,BMI=bmi,LVEDD=lvedd,BNP=bnp,CreatnineKinase=creatnine,Cholestrol=cholestrol,CEM=cem,Potassium=potassium,Result=resulthf)
                                            db.session.add(hfNew)
                                            db.session.commit()
                                            diagnosticsExecutionCounter=diagnosticsExecutionCounter+1
                    except :
                        print("Problem Running HF")
                    print("------------------Heart----------------")
                    print(f"1{y['Age']}" )
                    print(f"2{y['Sex']}")
                    print(f"3{y['CP']}" )
                    print(f"4{y['BP']}" ) 
                    print(f"5{y['FBS']}" ) 
                    print(f"6{y['ECG']}" ) 
                    print(f"7{y['Thalach']}" ) 
                    print(f"8{y['Exang']}" ) 
                    print(f"9{y['OldPeak']}" ) 
                    print(f"10{y['Slope']}" ) 
                    print(f"11{y['Ca']}" ) 
                    print(f"12{y['Thal']}" ) 
                    print(f"13{y['Cholesterol']}" )
                    try : 
                        if set(['Age','Sex','CP','BP','FBS','ECG','Thalach','Exang','OldPeak','Slope','Ca','Thal','Cholesterol']).issubset(df.columns):
                            diagnosticsDetectionCounter=diagnosticsDetectionCounter+1
                            print(f" Diagnostics Counter (Heart): {diagnosticsDetectionCounter}")
                            age = int(y['Age'] )                           
                            sex = int(y['Sex']  )
                            cp = int(y['CP'])
                            bp = int(y['BP'])
                            cholestrol= float(y['Cholesterol']* 0.02586)
                            fbs = int(y['FBS'] )                           
                            ecg = int(y['ECG'] )
                            thalach = int(y['Thalach'])
                            exang = int(y['Exang'])
                            oldpeak = float(y['OldPeak'])
                            slope = int(y['Slope'])
                            ca = int(y['Ca'])
                            thal = int(y['Thal'])
                            if y['Age']>0 and y['Sex']>=0 and y['Sex']<=1 and y['CP']>=0 and y['BP']>=30 and y['FBS']>=0 and y['ECG']>=0 and y['Thalach']>=30 and y['Exang']>=0 and y['OldPeak']>=0 and y['Slope']>=1 and y['Ca']>=0 and y['Thal']>=0 and  y['Cholesterol']>=0 and y['Age']<=130 and y['CP']<=4 and y['BP']<=300 and y['FBS']<=1 and y['ECG']<=2 and y['Thalach']<=300 and y['Exang']<=1 and y['OldPeak']<=15 and y['Slope']<=30 and y['Ca']<=3 and y['Thal']<=7 and  y['Cholesterol']<=10 :
                                Xdata = [ [age,sex,cp,bp,cholestrol,fbs,ecg,thalach,exang,oldpeak,slope,ca,thal] ]                        
                                if clfheart:
                                    x=clfheart.predict(Xdata)

                                    print("Heart clf Result :",end=" ")
                                    print(x)
                                
                                    if x == 1:
                                        resultheart="Yes"
                                    elif x == 0:
                                        resultheart="No"
                                    else:
                                        resultheart="Error"
                                    
                                    if DiagnosticsId:
                                        heart = HeartDisease(DiagnosticsId=DiagnosticsId.id,PatientId=ID,PatientDocId=current_user.DocId,Age=age,Sex=sex,CP=cp,BP=bp,Cholestrol=cholestrol,FBS=fbs,ECG=ecg,Thalach=thalach,Exang=exang,OldPeak=oldpeak,Slope=slope,ca=ca,Thal=thal,Result=resultheart)
                                        db.session.add(heart)
                                        db.session.commit()
                                        diagnosticsExecutionCounter=diagnosticsExecutionCounter+1
                                    else :
                                        new_record = PatientDiagnostics(PatientId=ID, PatientDocId=current_user.DocId, DiagnosticsFor=1)
                                        db.session.add(new_record)
                                        db.session.commit()
                                        DiagnosticsId = PatientDiagnostics.query.filter_by(PatientId=ID).order_by(PatientDiagnostics.id.desc()).first()
                                        if DiagnosticsId:
                                            heart = HeartDisease(DiagnosticsId=DiagnosticsId.id,PatientId=ID,PatientDocId=current_user.DocId,Age=age,Sex=sex,CP=cp,BP=bp,Cholestrol=cholestrol,FBS=fbs,ECG=ecg,Thalach=thalach,Exang=exang,OldPeak=oldpeak,Slope=slope,ca=ca,Thal=thal,Result=resultheart)
                                            db.session.add(heart)
                                            db.session.commit()
                                            diagnosticsExecutionCounter=diagnosticsExecutionCounter+1

                    except :
                        print("Problem Running Heart")
            except :
                return redirect(url_for('dashboard'))

            print("+")
            print("//")
            print("+")
            print(diagnosticsExecutionCounter,end="/")
            print(diagnosticsDetectionCounter,end="sucessfully executed\n")
            print(patientCounter)
            path = os.getcwd()+'/hdad/Diagnostics-Counter.txt'
            f = open(path, 'r')
            DiagnosticsCounter = int(f.read())
            f.close()
            f = open(path, 'w')
            f.write(str(DiagnosticsCounter+diagnosticsExecutionCounter))
            f.close()
            return render_template('dashboard.html',heartlist=heartlist,heartform = heartform , name=current_user.DocName, form=form,completeform=completeform,data=data,diagdata=Diagdata,chf=chf,hf=hf1,chfform=chfform,hfform=hfform,formnum=6,messagechf="",messageheart="",messagehf="",messagechfcomplete="",messagehfcomplete="",csvform=csvform,patientCounter=patientCounter,diagnosticsDetectionCounter=diagnosticsDetectionCounter,diagnosticsExecutionCounter=diagnosticsExecutionCounter)
        elif request.form.get("download"):
            try:
                return send_from_directory('static', filename='template.zip', as_attachment=True)
            except FileNotFoundError:
                abort(404)
        elif  request.form.get("submitchf"):
            if chfform.validate_on_submit():
                pulse = chfform.Pulse.data
                nyha = chfform.NYHA.data
                killip = chfform.Killip.data
                bnp = chfform.BNP.data
                cystatin = chfform.Cystatin.data
                potassium = chfform.Potassium.data
                
                Xdata = [ [pulse,nyha,killip,bnp,cystatin,potassium ] ]
                print(Xdata)
                try:
                    with open('hdad/CHF_Detection_Model.pkl', 'rb') as f:
                        clf = pickle.load(f)
                    x=clf.predict(Xdata)
                except :
                    x=2

                if x == 1:
                    message="Patient Have Congestive Heart Failure"
                elif x == 0:
                    message="Patient Does Not Have Congestive Heart Failure"
                else:
                    message="error"
                path = os.getcwd()+'/hdad/Diagnostics-Counter.txt'
                f = open(path, 'r')
                DiagnosticsCounter = int(f.read())
                f.close()
                f = open(path, 'w')
                f.write(str(DiagnosticsCounter+1))
                f.close()
                return render_template('dashboard.html',heartlist=heartlist,heartform = heartform , name=current_user.DocName, form=form,data=data,completeform=completeform,diagdata=Diagdata,chf=chf,hf=hf1,formnum=1,chfform=chfform, hfform=hfform,messagechf=message,messageheart="",messagehf="",messagechfcomplete="",messagehfcomplete="",csvform=csvform,patientCounter="",diagnosticsDetectionCounter="",diagnosticsExecutionCounter="")
            else :
                return render_template('dashboard.html',heartlist=heartlist,heartform = heartform,patientCounter="",diagnosticsDetectionCounter="",diagnosticsExecutionCounter="" , name=current_user.DocName, form=form,data=data,completeform=completeform,diagdata=Diagdata,chf=chf,hf=hf1,formnum=1,chfform=chfform, hfform=hfform,messagechf="Check Values And Try again",messageheart="",messagehf="",messagechfcomplete="",messagehfcomplete="",csvform=csvform)
        elif  request.form.get("submitcomplete"):
            print(completeform.validate_on_submit())
            if completeform.validate_on_submit():
                pulse = completeform.Pulse4.data
                nyha = completeform.NYHA4.data
                killip = completeform.Killip4.data
                bnp = completeform.BNP4.data
                cystatin = completeform.Cystatin4.data
                potassium = completeform.Potassium4.data
                systolicbp = completeform.SystolicBP4.data
                bmi=completeform.BMI4.data
                lvedd = completeform.LVEDD4.data
                creatnine=completeform.CreatnineKinase4.data
                cholestrol = completeform.Cholestrol4.data
                cem = completeform.CEM4.data
                age = completeform.Age4.data
                sex = completeform.Sex4.data
                cp = completeform.CP4.data
                bp = completeform.BP4.data
                fbs = completeform.FBS4.data
                ecg = completeform.ECG4.data
                thalach = completeform.Thalach4.data
                exang = completeform.Exang4.data
                oldpeak = completeform.OldPeak4.data
                slope = completeform.Slope4.data
                ca = completeform.Ca4.data
                thal = completeform.Thal4.data
                # try :
                #     pulse = int(pulse)
                #     nyha = int(nyha)
                #     killip = int(killip)
                #     bnp = int(bnp)
                #     cystatin = int(cystatin)
                #     potassium = int(potassium)
                #     systolicbp = int(systolicbp)
                #     bmi = int(bmi)
                #     lvedd = int(lvedd)
                #     creatnine = int(creatnine)
                #     cholestrol = int(cholestrol)
                #     cem = int(cem)
                #     age = int(age)      
                #     sex = int(sex)
                #     cp = int(cp)
                #     bp = int(bp)
                #     fbs = int(fbs)
                #     ecg = int(ecg)
                #     thalach = int(thalach)
                #     exang = int(exang)
                #     oldpeak = int(oldpeak)
                #     slope = int(slope)
                #     ca = int(ca)
                #     thal = int(thal)
                # except :
                #     message="Enter Numerical Values"
                #     return render_template('dashboard.html',heartform = heartform , name=current_user.DocName, form=form,data=data,diagdata=Diagdata,chf=chf,hf=hf1,formnum=2,chfform=chfform,completeform=completeform, hfform=hfform,message=message,message2="",csvform=csvform)
                Xdatachf = [ [pulse,nyha,killip,bnp,cystatin,potassium ] ]
                Xdatahf = [ [pulse,systolicbp,bmi,lvedd,bnp,creatnine,cholestrol,cem,potassium ] ]
                Xdataheart = [ [age,sex,cp,bp,cholestrol,fbs,ecg,thalach,exang,oldpeak,slope,ca,thal] ]
                print(Xdatachf)
                try :
                    with open('hdad/CHF_Detection_Model.pkl', 'rb') as f:
                        clf = pickle.load(f)
                    x=clf.predict(Xdatachf)
                except :
                    x=2

                if x == 1:
                    message="Patient Have Congestive Heart Failure"
                elif x == 0:
                    message="Patient Does Not Have Congestive Heart Failure"
                else:
                    message="error"
                try :
                    with open('hdad/HF_Classification_Model.pkl', 'rb') as f:
                        clf = pickle.load(f)
                    x=clf.predict(Xdatahf)
                except :
                    x=2
                
                if x == 1:
                    message2="Patient Have HFpEF"
                elif x == 0:
                    message2="Patient Have HFrEF"
                else:
                    message2="error"
                
                try:
                    with open('hdad/Heart_disease_CatBoost_Model.pkl', 'rb') as f:
                        clf = pickle.load(f)
                    x=clf.predict(Xdataheart)
                except :
                    x=2
                
                if x == 1:
                    message3="Patient Have Heart Disease"
                elif x == 0:
                    message3="Patient Have Heart Disease"
                else:
                    message3="error"
                path = os.getcwd()+'/hdad/Diagnostics-Counter.txt'
                f = open(path, 'r')
                DiagnosticsCounter = int(f.read())
                f.close()
                f = open(path, 'w')
                f.write(str(DiagnosticsCounter+3))
                f.close()
                
                return render_template('dashboard.html',heartlist=heartlist,heartform = heartform,patientCounter="",diagnosticsDetectionCounter="",diagnosticsExecutionCounter="" , name=current_user.DocName, form=form,data=data,completeform=completeform,diagdata=Diagdata,chf=chf,hf=hf1,formnum=4,chfform=chfform, hfform=hfform,messagechf="",messageheart="",messagehf="",messagechfcomplete=message,messagehfcomplete=message2,messageheartcomplete=message3,csvform=csvform)
            else :
                return render_template('dashboard.html',heartlist=heartlist,heartform = heartform,patientCounter="",diagnosticsDetectionCounter="",diagnosticsExecutionCounter="" , name=current_user.DocName, form=form,data=data,completeform=completeform,diagdata=Diagdata,chf=chf,hf=hf1,formnum=4,chfform=chfform, hfform=hfform,messagechf="",messageheart="",messagehf="",messagechfcomplete="Check Values And Try Again",messagehfcomplete="",messageheartcomplete="",csvform=csvform)
        elif  request.form.get("submithf"):
            if hfform.validate_on_submit():
                pulse = hfform.Pulse2.data
                systolicbp = hfform.SystolicBP.data
                bmi = hfform.BMI.data
                lvedd = hfform.LVEDD.data
                bnp = hfform.BNP2.data
                creatnine=hfform.CreatnineKinase.data
                cholestrol = hfform.Cholestrol.data
                cem = hfform.CEM.data
                potassium = hfform.Potassium2.data

                # pulse = int(pulse)      
                # systolicbp = int(systolicbp)
                # lvedd = int(lvedd)
                # bnp = int(bnp)
                # creatnine = int(creatnine)
                # cholestrol = int(cholestrol)
                # cem = int(cem)
                # potassium = int(potassium)
                Xdata = [ [pulse,systolicbp,bmi,lvedd,bnp,creatnine,cholestrol,cem,potassium ] ]
                
                try:
                    with open('hdad/HF_Classification_Model.pkl', 'rb') as f:
                        clf = pickle.load(f)
                    x=clf.predict(Xdata)
                except :
                    x=2
                
                if x == 1:
                    message2="Patient Have HFpEF"
                elif x == 0:
                    message2="Patient Have HFrEF"
                else:
                    message2="error"
                path = os.getcwd()+'/hdad/Diagnostics-Counter.txt'
                f = open(path, 'r')
                DiagnosticsCounter = int(f.read())
                f.close()
                f = open(path, 'w')
                f.write(str(DiagnosticsCounter+1))
                f.close()
                return render_template('dashboard.html',heartlist=heartlist,heartform = heartform , name=current_user.DocName,patientCounter="",diagnosticsDetectionCounter="",diagnosticsExecutionCounter="", form=form,completeform=completeform,data=data,diagdata=Diagdata,chf=chf,hf=hf1,formnum=2,chfform=chfform,hfform=hfform,messagechf="",messageheart="",messagehf=message2,messagechfcomplete="",messagehfcomplete="",csvform=csvform)
            else :
                return render_template('dashboard.html',heartlist=heartlist,heartform = heartform , name=current_user.DocName,patientCounter="",diagnosticsDetectionCounter="",diagnosticsExecutionCounter="", form=form,completeform=completeform,data=data,diagdata=Diagdata,chf=chf,hf=hf1,formnum=2,chfform=chfform,hfform=hfform,messagechf="",messageheart="",messagehf="Check Values And Try Again",messagechfcomplete="",messagehfcomplete="",csvform=csvform)
        elif request.form.get("submitheart"):
            
            if heartform.validate_on_submit():
                age = heartform.Age.data
                
                sex = heartform.Sex.data
                cp = heartform.CP.data
                bp = heartform.BP.data
                cholestrol=heartform.CholestrolHeart.data
                fbs = heartform.FBS.data
                
                ecg = heartform.ECG.data
                thalach = heartform.Thalach.data
                exang = heartform.Exang.data
                oldpeak = heartform.OldPeak.data
                slope = heartform.Slope.data
                ca = heartform.Ca.data
                thal = heartform.Thal.data
                
                # age = int(age)      
                # sex = int(sex)
                # cp = int(cp)
                # bp = int(bp)
                # fbs = int(fbs)
                # cholestrol = int(cholestrol)
                # ecg = int(ecg)
                # thalach = int(thalach)
                # exang = int(exang)
                # oldpeak = int(oldpeak)
                # slope = int(slope)
                # ca = int(ca)
                # thal = int(thal)
                Xdata = [ [age,sex,cp,bp,cholestrol,fbs,ecg,thalach,exang,oldpeak,slope,ca,thal] ]
                print(Xdata)
                try:
                    with open('hdad/Heart_disease_CatBoost_Model.pkl', 'rb') as f:
                        clf = pickle.load(f)
                    x=clf.predict(Xdata)
                except :
                    x=2
                
                if x == 1:
                    message2="Patient Have Heart Disease"
                elif x == 0:
                    message2="Patient Does Not Have Heart Disease"
                else:
                    message2="error"
                path = os.getcwd()+'/hdad/Diagnostics-Counter.txt'
                f = open(path, 'r')
                DiagnosticsCounter = int(f.read())
                f.close()
                f = open(path, 'w')
                f.write(str(DiagnosticsCounter+1))
                f.close()
                return render_template('dashboard.html',heartlist=heartlist,heartform = heartform,patientCounter="",diagnosticsDetectionCounter="",diagnosticsExecutionCounter="" , name=current_user.DocName, form=form,completeform=completeform,data=data,diagdata=Diagdata,chf=chf,hf=hf1,formnum=3,chfform=chfform,hfform=hfform,messagechf="",messageheart=message2,messagehf="",messagechfcomplete="",messagehfcomplete="",csvform=csvform)
            else :
                return render_template('dashboard.html',heartlist=heartlist,heartform = heartform ,patientCounter="",diagnosticsDetectionCounter="",diagnosticsExecutionCounter="", name=current_user.DocName, form=form,completeform=completeform,data=data,diagdata=Diagdata,chf=chf,hf=hf1,formnum=3,chfform=chfform,hfform=hfform,messagechf="",messageheart="Check Values And Try Again",messagehf="",messagechfcomplete="",messagehfcomplete="",csvform=csvform)
        else :
            return render_template('dashboard.html',heartlist=heartlist,heartform = heartform,patientCounter="",diagnosticsDetectionCounter="",diagnosticsExecutionCounter="" , name=current_user.DocName, form=form,data=data,completeform=completeform,diagdata=Diagdata,chf=chf,hf=hf1,formnum=5,chfform=chfform, hfform=hfform,messagechf="",messageheart="",messagehf="",messagechfcomplete="",messagehfcomplete="",csvform=csvform)
    else:
        return render_template('dashboard.html',heartform = heartform,patientCounter="",name=current_user.DocName, form=form,completeform=completeform,data=data,diagdata=Diagdata,chf=chf,hf=hf1,chfform=chfform,hfform=hfform,fornnum=0,messagechf="",messageheart="",messagehf="",messagechfcomplete="",messagehfcomplete="",heartlist=heartlist,diagnosticsDetectionCounter="",diagnosticsExecutionCounter="" , csvform=csvform)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def UserProfile():
    delete = ConfirmDelete()
    if delete.validate_on_submit():
        if delete.Input.data == 'Delete':
            try :
                delete_q = Patient.__table__.delete().where(Patient.PatientDocId == current_user.DocId)
                db.session.execute(delete_q)
                db.session.commit()
                delete_q = PatientDiagnostics.__table__.delete().where(PatientDiagnostics.PatientDocId == current_user.DocId)
                db.session.execute(delete_q)
                db.session.commit()
                delete_q = CHF.__table__.delete().where(CHF.PatientDocId == current_user.DocId)
                db.session.execute(delete_q)
                db.session.commit()
                delete_q = HF.__table__.delete().where(HF.PatientDocId == current_user.DocId)
                db.session.execute(delete_q)
                db.session.commit()
                delete_q = User.__table__.delete().where(User.DocId == current_user.DocId)
                db.session.execute(delete_q)
                db.session.commit()
                logout_user()
                return render_template("accountdeleted.html")
            except :
                return render_template('error.html')
        else :
            return render_template("profile.html",name=current_user.DocName,delete=delete,message="Try again")
    else :
        return render_template("profile.html",name=current_user.DocName,delete=delete)


@app.route('/recovery', methods=['GET', 'POST'])
def AccountRecovery():
    username=UsernameRecoveryForm()
    password = PasswordRecoveryForm()
    if username.validate_on_submit() and  request.form.get("submitusername"):
        print("ChangeUsername")
    else :
        return render_template("accountrecovery.html",username=username,password=password)


@app.route('/<pid>',methods=['GET', 'POST'])
@login_required
def showpatient(pid):
    csvform=UploadCSV()
    delete = ConfirmDelete()
    featureform = StatsSelector()
    heartform = HeartDiseaseDiagnostics()
    chfform = CHFDiagnostics()
    completeform=CompleteDiagnostics()
    hfform = HFDiagnostics()
    alert = MailForm()
    try :
        Patientdata = Patient.query.filter_by(PatientId=pid).first()
        if Patientdata==None or Patientdata.PatientDocId!=current_user.DocId :
            return render_template("access_denied.html",name=current_user.DocName)
        Diagnostics = PatientDiagnostics.query.filter_by(PatientId=pid).order_by(PatientDiagnostics.id.desc()).first()
        chf = CHF.query.filter_by(PatientId=pid).order_by(CHF.id.desc()).all()
        hf = HF.query.filter_by(PatientId=pid).order_by(HF.id.desc()).all()
        heartlist = HeartDisease.query.filter_by(PatientDocId=current_user.DocId).order_by(HeartDisease.id.desc()).all()

        diag = PatientDiagnostics.query.filter_by(PatientId=pid).order_by(PatientDiagnostics.id.desc()).all()
        if Diagnostics:
            lastDiagDate = Diagnostics.DiagnosticsDate.strftime("%d/%m/%Y")
        else :
            lastDiagDate = "---"
    except :
        return render_template('error.html')
    if request.method == 'POST':
        if  request.form.get("savechf"):
            if chfform.validate_on_submit(): 
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
                pulse = str(pulse)
                nyha = str(nyha)
                killip = str(killip)
                bnp = str(bnp)
                cystatin = str(cystatin)
                potassium = str(potassium)
                try :
                    with open('hdad/CHF_Detection_Model.pkl', 'rb') as f:
                        clf = pickle.load(f)
                    x=clf.predict(Xdata)
                except :
                    x=2
                
                if x == 1:
                    result="Yes"
                elif x == 0:
                    result="No"
                else:
                    result="error"
                try :
                    new_record = PatientDiagnostics(PatientId=Patientdata.PatientId, PatientDocId=current_user.DocId, DiagnosticsFor=2)
                    db.session.add(new_record)
                    db.session.commit()
                    DiagnosticsId = PatientDiagnostics.query.filter_by(PatientId=Patientdata.PatientId).order_by(PatientDiagnostics.id.desc()).first()
                    if DiagnosticsId:
                        chf_new = CHF(DiagnosticsId=DiagnosticsId.id,PatientId=pid,PatientDocId=current_user.DocId, Pulse=pulse, NYHA=nyha, Killip=killip,BNP=bnp,Cystatin=cystatin,Potassium=potassium,Result=result)
                        db.session.add(chf_new)
                        db.session.commit()
                except :
                    db.session.rollback()
                    
                path = os.getcwd()+'/hdad/Diagnostics-Counter.txt'
                f = open(path, 'r')
                DiagnosticsCounter = int(f.read())
                f.close()
                f = open(path, 'w')
                f.write(str(DiagnosticsCounter+1))
                f.close()
                return redirect(url_for('showpatient',pid=pid))
            else :
                messagechf="Enter Decimal Numbers Only"
                return render_template('patientdetails.html',messagechf=messagechf,messageheart="",messagehf="",messagechfcomplete="",messagehfcomplete="",heartlist=heartlist,diagnosticsDetectionCounter="",diagnosticsExecutionCounter="" ,heartform = heartform , name=current_user.DocName,completeform=completeform,data=Patientdata,diagdata=diag,dd=lastDiagDate,chfform=chfform, hfform=hfform,form=2, message=message,message2="",alert=alert,chf=chf,hf=hf,featureform=featureform,delete=delete)
        elif request.form.get("submitchf"):
            if chfform.validate_on_submit():
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
                try :
                    with open('hdad/CHF_Detection_Model.pkl', 'rb') as f:
                        clf = pickle.load(f)
                    x=clf.predict(Xdata)
                except :
                    x=2

                if x == 1:
                    message="Patient Have Congestive Heart Failure"
                elif x == 0:
                    message="Patient Does Not Have Congestive Heart Failure"
                else:
                    message="error"
                path = os.getcwd()+'/hdad/Diagnostics-Counter.txt'
                f = open(path, 'r')
                DiagnosticsCounter = int(f.read())
                f.close()
                f = open(path, 'w')
                f.write(str(DiagnosticsCounter+1))
                f.close()
                return render_template('patientdetails.html',messagechf=message,messageheart="",messagehf="",messagechfcomplete="",messagehfcomplete="",heartlist=heartlist,diagnosticsDetectionCounter="",diagnosticsExecutionCounter="" ,heartform = heartform , name=current_user.DocName,completeform=completeform,data=Patientdata,diagdata=diag,dd=lastDiagDate,chfform=chfform, hfform=hfform,form=2, message=message,message2="",alert=alert,chf=chf,hf=hf,featureform=featureform,delete=delete)
            else :
                message="Enter Decimal Numbers Only"
                return render_template('patientdetails.html',messagechf="",messageheart="",messagehf="",messagechfcomplete="",messagehfcomplete="",heartlist=heartlist,diagnosticsDetectionCounter="",diagnosticsExecutionCounter="" ,heartform = heartform , name=current_user.DocName,completeform=completeform,data=Patientdata,diagdata=diag,dd=lastDiagDate,chfform=chfform, hfform=hfform,form=2, message=message,message2="",alert=alert,chf=chf,hf=hf,featureform=featureform,delete=delete)
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
            bmi = hfform.BMI.data
            lvedd = hfform.LVEDD.data
            bnp = hfform.BNP2.data
            creatnine=hfform.CreatnineKinase.data
            cholestrol = hfform.Cholestrol.data
            cem = hfform.CEM.data
            potassium = hfform.Potassium2.data

            pulse = int(pulse)      
            systolicbp = int(systolicbp)
            bmi = int(bmi)
            lvedd = int(lvedd)
            bnp = int(bnp)
            creatnine = int(creatnine)
            cholestrol = int(cholestrol)
            cem = int(cem)
            potassium = int(potassium)
            Xdata = [ [pulse,systolicbp,bmi,lvedd,bnp,creatnine,cholestrol,cem,potassium ] ]
            pulse = str(pulse)      
            systolicbp = str(systolicbp)
            lvedd = str(lvedd)
            bnp = str(bnp)
            creatnine = str(creatnine)
            cholestrol = str(cholestrol)
            cem = str(cem)
            potassium = str(potassium)
            try :
                with open('hdad/HF_Classification_Model.pkl', 'rb') as f:
                    clf = pickle.load(f)
                x=clf.predict(Xdata)
            except :
                x=2
            print(x)
            if x == 1:
               result="HFpEF"
            elif x == 0:
                result="HFrEF"
            else:
                result="error"
            try :
                new_record = PatientDiagnostics(PatientId=Patientdata.PatientId, PatientDocId=current_user.DocId, DiagnosticsFor=3)
                db.session.add(new_record)
                db.session.commit()
                DiagnosticsId = PatientDiagnostics.query.filter_by(PatientId=Patientdata.PatientId).order_by(PatientDiagnostics.id.desc()).first()
                if DiagnosticsId:
                    hf = HF(DiagnosticsId=DiagnosticsId.id,PatientId=pid,PatientDocId=current_user.DocId, Pulse=pulse, SystolicBP=systolicbp,BMI=bmi,LVEDD=lvedd,BNP=bnp,CreatnineKinase=creatnine,Cholestrol=cholestrol,CEM=cem,Potassium=potassium,Result=result)
                    db.session.add(hf)
                    db.session.commit()
            except :
                db.session.rollback()
            path = os.getcwd()+'/hdad/Diagnostics-Counter.txt'
            f = open(path, 'r')
            DiagnosticsCounter = int(f.read())
            f.close()
            f = open(path, 'w')
            f.write(str(DiagnosticsCounter+1))
            f.close()
            return redirect(url_for('showpatient',pid=pid))
        elif completeform.validate_on_submit() and  request.form.get("save"):
            pulse = completeform.Pulse4.data
            nyha = completeform.NYHA4.data
            killip = completeform.Killip4.data
            bnp = completeform.BNP4.data
            cystatin = completeform.Cystatin4.data
            potassium = completeform.Potassium4.data
            systolicbp = completeform.SystolicBP4.data
            bmi=completeform.BMI4.data
            lvedd = completeform.LVEDD4.data
            creatnine=completeform.CreatnineKinase4.data
            cholestrol = completeform.Cholestrol4.data
            cem = completeform.CEM4.data
            age = heartform.Age4.data
            sex = heartform.Sex4.data
            cp = heartform.CP4.data
            bp = heartform.BP4.data
            fbs = heartform.FBS4.data
            ecg = heartform.ECG4.data
            thalach = heartform.Thalach4.data
            exang = heartform.Exang4.data
            oldpeak = heartform.OldPeak4.data
            slope = heartform.Slope4.data
            ca = heartform.Ca4.data
            thal = heartform.Thal4.data
            try :
                pulse = int(pulse)
                nyha = int(nyha)
                killip = int(killip)
                bnp = int(bnp)
                cystatin = int(cystatin)
                potassium = int(potassium)
                systolicbp = int(systolicbp)
                bmi = int(bmi)
                lvedd = int(lvedd)
                creatnine = int(creatnine)
                cholestrol = int(cholestrol)
                cem = int(cem)
                age = int(age)      
                sex = int(sex)
                cp = int(cp)
                bp = int(bp)
                fbs = int(fbs)
                ecg = int(ecg)
                thalach = int(thalach)
                exang = int(exang)
                oldpeak = int(oldpeak)
                slope = int(slope)
                ca = int(ca)
                thal = int(thal)
            except :
                message="Enter Numerical Values"
                return render_template('patientdetails.html',messagechf=message,messageheart="",messagehf="",messagechfcomplete="",messagehfcomplete="",heartlist=heartlist,diagnosticsDetectionCounter="",diagnosticsExecutionCounter="" ,heartform = heartform ,  name=current_user.DocName,completeform=completeform,data=Patientdata,diagdata=diag,dd=lastDiagDate,chfform=chfform, hfform=hfform,form=2, message=message,message2="",alert=alert,chf=chf,hf=hf,featureform=featureform,delete=delete)
            Xdatachf = [ [pulse,nyha,killip,bnp,cystatin,potassium ] ]
            Xdatahf = [ [pulse,systolicbp,bmi,lvedd,bnp,creatnine,cholestrol,cem,potassium ] ]
            Xdataheart = [ [age,sex,cp,bp,cholestrol,fbs,ecg,thalach,exang,oldpeak,slope,ca,thal] ]
            try :
                with open('hdad/CHF_Detection_Model.pkl', 'rb') as f:
                    clf = pickle.load(f)
                x=clf.predict(Xdatachf)
            except :
                x=2

            if x == 1:
               message="Patient Have Congestive Heart Failure"
               resultchf="Yes"
            elif x == 0:
                message="Patient Does Not Have Congestive Heart Failure"
                resultchf="No"
            else:
                message="error"
            try :
                with open('hdad/HF_Classification_Model.pkl', 'rb') as f:
                    clf = pickle.load(f)
                x=clf.predict(Xdata)
            except :
                x=2
            
            if x == 1:
               message2="Patient Have HFpEF"
               resulthf="HFpEF"
            elif x == 0:
                message2="Patient Have HFrEF"
                resulthf='HFrEf'
            else:
                message2="error"
            
            try:
                with open('hdad/Heart_disease_CatBoost_Model.pkl', 'rb') as f:
                    clf = pickle.load(f)
                x=clf.predict(Xdataheart)
            except :
                x=2
            
            if x == 1:
               message3="Patient Have Heart Disease"
               resultheart="Yes"
            elif x == 0:
                message3="Patient Do not Have Heart Disease"
                resultheart="No"
            else:
                message3="error"
            try :
                new_record = PatientDiagnostics(PatientId=Patientdata.PatientId, PatientDocId=current_user.DocId, DiagnosticsFor=4)
                db.session.add(new_record)
                db.session.commit()
                DiagnosticsId = PatientDiagnostics.query.filter_by(PatientId=Patientdata.PatientId).order_by(PatientDiagnostics.id.desc()).first()
                if DiagnosticsId:
                    heart = HeartDisease(DiagnosticsId=DiagnosticsId.id,PatientId=pid,PatientDocId=current_user.DocId,Age=age,Sex=sex,CP=cp,BP=bp,Cholestrol=cholestrol,FBS=fbs,ECG=ecg,Thalach=thalach,Exang=exang,OldPeak=oldpeak,Slope=slope,ca=ca,Thal=thal,Result=resultheart)
                    db.session.add(heart)
                    db.session.commit()
                    chf = CHF(DiagnosticsId=DiagnosticsId.id,PatientId=pid,PatientDocId=current_user.DocId, Pulse=pulse, NYHA=nyha, Killip=killip,BNP=bnp,Cystatin=cystatin,Potassium=potassium,Result=resultchf)
                    db.session.add(chf)
                    db.session.commit()
                    hf = HF(DiagnosticsId=DiagnosticsId.id,PatientId=pid,PatientDocId=current_user.DocId, Pulse=pulse, SystolicBP=systolicbp,LVEDD=lvedd,BNP=bnp,CreatnineKinase=creatnine,Cholestrol=cholestrol,CEM=cem,Potassium=potassium,Result=resulthf)
                    db.session.add(hf)
                    db.session.commit()
            except :
                return render_template('error.html')
            path = os.getcwd()+'/hdad/Diagnostics-Counter.txt'
            f = open(path, 'r')
            DiagnosticsCounter = int(f.read())
            f.close()
            f = open(path, 'w')
            f.write(str(DiagnosticsCounter+3))
            f.close()
            

            return redirect(url_for('showpatient',pid=pid))
        elif  request.form.get("submitcomplete"):
            if completeform.validate_on_submit():
                pulse = completeform.Pulse4.data
                nyha = completeform.NYHA4.data
                killip = completeform.Killip4.data
                bnp = completeform.BNP4.data
                cystatin = completeform.Cystatin4.data
                potassium = completeform.Potassium4.data
                systolicbp = completeform.SystolicBP4.data
                bmi=completeform.BMI4.data
                lvedd = completeform.LVEDD4.data
                creatnine=completeform.CreatnineKinase4.data
                cholestrol = completeform.Cholestrol4.data
                cem = completeform.CEM4.data
                age = completeform.Age4.data
                sex = completeform.Sex4.data
                cp = completeform.CP4.data
                bp = completeform.BP4.data
                fbs = completeform.FBS4.data
                ecg = completeform.ECG4.data
                thalach = completeform.Thalach4.data
                exang = completeform.Exang4.data
                oldpeak = completeform.OldPeak4.data
                slope = completeform.Slope4.data
                ca = completeform.Ca4.data
                thal = completeform.Thal4.data
                
                pulse = int(pulse)
                nyha = int(nyha)
                killip = int(killip)
                bnp = float(bnp)
                cystatin = float(cystatin)
                potassium = float(potassium)
                systolicbp = int(systolicbp)
                bmi = float(bmi)
                lvedd = float(lvedd)
                creatnine = float(creatnine)
                cholestrol = float(cholestrol)
                cem = float(cem)
                age = int(age)      
                sex = int(sex)
                cp = int(cp)
                bp = int(bp)
                fbs = int(fbs)
                ecg = int(ecg)
                thalach = int(thalach)
                exang = int(exang)
                oldpeak = int(oldpeak)
                slope = int(slope)
                ca = int(ca)
                thal = int(thal)
                Xdatachf = [ [pulse,nyha,killip,bnp,cystatin,potassium ] ]
                Xdatahf = [ [pulse,systolicbp,bmi,lvedd,bnp,creatnine,cholestrol,cem,potassium ] ]
                Xdataheart = [ [age,sex,cp,bp,(cholestrol*0.02586),fbs,ecg,thalach,exang,oldpeak,slope,ca,thal] ]
                print(Xdatachf)
                print(Xdataheart)
                print(Xdatahf)
                try :
                    with open('hdad/CHF_Detection_Model.pkl', 'rb') as f:
                        clf = pickle.load(f)
                    x=clf.predict(Xdatachf)
                except :
                    x=2

                if x == 1:
                    message="Patient Have Congestive Heart Failure"
                elif x == 0:
                    message="Patient Does Not Have Congestive Heart Failure"
                else:
                    message="error"
                try :
                    with open('hdad/HF_Classification_Model.pkl', 'rb') as f:
                        clf = pickle.load(f)
                    x=clf.predict(Xdata)
                except :
                    x=2
                
                if x == 1:
                    message2="Patient Have HFpEF"
                elif x == 0:
                    message2="Patient Have HFrEF"
                else:
                    message2="error"
                
                try:
                    with open('hdad/Heart_disease_CatBoost_Model.pkl', 'rb') as f:
                        clf = pickle.load(f)
                    x=clf.predict(Xdataheart)
                except :
                    x=2
                
                if x == 1:
                    message3="Patient Have Heart Disease"
                elif x == 0:
                    message3="Patient Do Not Have Heart Disease"
                else:
                    message3="error"
                print(message2)
                print(message3)
                print(message)
                path = os.getcwd()+'/hdad/Diagnostics-Counter.txt'
                f = open(path, 'r')
                DiagnosticsCounter = int(f.read())
                f.close()
                f = open(path, 'w')
                f.write(str(DiagnosticsCounter+3))
                f.close()
                return render_template('patientdetails.html',messagechf="",messageheart="",messagehf="",messageheartcomplete=message3,messagechfcomplete=message,messagehfcomplete=message2,heartlist=heartlist,diagnosticsDetectionCounter="",diagnosticsExecutionCounter="" ,heartform = heartform , name=current_user.DocName,completeform=completeform,data=Patientdata,diagdata=diag,dd=lastDiagDate,chfform=chfform, hfform=hfform,form=6, message="",message2="",alert=alert,chf=chf,hf=hf,featureform=featureform,delete=delete)
            else :
                return render_template('patientdetails.html',messagechf="",messageheart="",messagehf="",messageheartcomplete="",messagechfcomplete="",messagehfcomplete="Try Again",heartlist=heartlist,diagnosticsDetectionCounter="",diagnosticsExecutionCounter="" ,heartform = heartform , name=current_user.DocName,completeform=completeform,data=Patientdata,diagdata=diag,dd=lastDiagDate,chfform=chfform, hfform=hfform,form=6, message="",message2="",alert=alert,chf=chf,hf=hf,featureform=featureform,delete=delete)
        elif heartform.validate_on_submit() and  request.form.get("save"):
            age = heartform.Age.data
            sex = heartform.Sex.data
            cp = heartform.CP.data
            bp = heartform.BP.data
            cholestrol=heartform.CholestrolHeart.data
            fbs = heartform.FBS.data
            ecg = heartform.ECG.data
            thalach = heartform.Thalach.data
            exang = heartform.Exang.data
            oldpeak = heartform.OldPeak.data
            slope = heartform.Slope.data
            ca = heartform.Ca.data
            thal = heartform.Thal.data

            age = int(age)      
            sex = int(sex)
            cp = int(cp)
            bp = int(bp)
            fbs = int(fbs)
            cholestrol = int(cholestrol)
            cholestrol=cholestrol*0.02586
            ecg = int(ecg)
            thalach = int(thalach)
            exang = int(exang)
            oldpeak = int(oldpeak)
            slope = int(slope)
            ca = int(ca)
            thal = int(thal)
            Xdata = [ [age,sex,cp,bp,cholestrol,fbs,ecg,thalach,exang,oldpeak,slope,ca,thal] ]
            
            try:
                with open('hdad/Heart_disease_CatBoost_Model.pkl', 'rb') as f:
                    clf = pickle.load(f)
                x=clf.predict(Xdata)
            except :
                x=2
            
            if x == 1:
               message2="Patient Have Heart Disease"
               resultheart="Yes"
            elif x == 0:
                message2="Patient does not Have Heart Disease"
                resultheart="No"
            else:
                message2="error"
            
            try :
                new_record = PatientDiagnostics(PatientId=Patientdata.PatientId, PatientDocId=current_user.DocId, DiagnosticsFor=1)
                db.session.add(new_record)
                db.session.commit()
                DiagnosticsId = PatientDiagnostics.query.filter_by(PatientId=Patientdata.PatientId).order_by(PatientDiagnostics.id.desc()).first()
                if DiagnosticsId:
                    heart = HeartDisease(DiagnosticsId=DiagnosticsId.id,PatientId=pid,PatientDocId=current_user.DocId,Age=age,Sex=sex,CP=cp,BP=bp,Cholestrol=cholestrol,FBS=fbs,ECG=ecg,Thalach=thalach,Exang=exang,OldPeak=oldpeak,Slope=slope,ca=ca,Thal=thal ,Result=resultheart)
                    db.session.add(heart)
                    db.session.commit()
            except :
                db.session.rollback()
            path = os.getcwd()+'/hdad/Diagnostics-Counter.txt'
            f = open(path, 'r')
            DiagnosticsCounter = int(f.read())
            f.close()
            f = open(path, 'w')
            f.write(str(DiagnosticsCounter+1))
            f.close()
            
            return redirect(url_for('showpatient',pid=pid))
        elif heartform.validate_on_submit() and  request.form.get("submitheart"):
            age = heartform.Age.data
            sex = heartform.Sex.data
            cp = heartform.CP.data
            bp = heartform.BP.data
            cholestrol=heartform.CholestrolHeart.data
            fbs = heartform.FBS.data
            ecg = heartform.ECG.data
            thalach = heartform.Thalach.data
            exang = heartform.Exang.data
            oldpeak = heartform.OldPeak.data
            slope = heartform.Slope.data
            ca = heartform.Ca.data
            thal = heartform.Thal.data

            age = int(age)      
            sex = int(sex)
            cp = int(cp)
            bp = int(bp)
            fbs = int(fbs)
            cholestrol = int(cholestrol)
            cholestrol=cholestrol*0.02586
            ecg = int(ecg)
            thalach = int(thalach)
            exang = int(exang)
            oldpeak = int(oldpeak)
            slope = int(slope)
            ca = int(ca)
            thal = int(thal)
            Xdata = [ [age,sex,cp,bp,cholestrol,fbs,ecg,thalach,exang,oldpeak,slope,ca,thal] ]
            
            try:
                with open('hdad/Heart_disease_CatBoost_Model.pkl', 'rb') as f:
                    clf = pickle.load(f)
                x=clf.predict(Xdata)
            except :
                x=2
            
            if x == 1:
               message2="Patient Have Heart Disease"
            elif x == 0:
                message2="Patient Do Not Have Heart Disease"
            else:
                message2="error"
            path = os.getcwd()+'/hdad/Diagnostics-Counter.txt'
            f = open(path, 'r')
            DiagnosticsCounter = int(f.read())
            f.close()
            f = open(path, 'w')
            f.write(str(DiagnosticsCounter+1))
            f.close()
            return render_template('patientdetails.html',messagechf="",messageheart=message2,messagehf="",messagechfcomplete="",messagehfcomplete="",heartlist=heartlist,diagnosticsDetectionCounter="",diagnosticsExecutionCounter="" ,heartform = heartform , name=current_user.DocName,completeform=completeform,data=Patientdata,diagdata=diag,dd=lastDiagDate,chfform=chfform, hfform=hfform,form=5, message="",message2=message2,alert=alert,hf=hf,chf=chf,featureform=featureform,delete=delete)
        elif hfform.validate_on_submit() and  request.form.get("submithf"):
            pulse = hfform.Pulse2.data
            systolicbp = hfform.SystolicBP.data
            bmi = hfform.BMI.data
            lvedd = hfform.LVEDD.data
            bnp = hfform.BNP2.data
            creatnine=hfform.CreatnineKinase.data
            cholestrol = hfform.Cholestrol.data
            cem = hfform.CEM.data
            potassium = hfform.Potassium2.data

            pulse = int(pulse)      
            systolicbp = int(systolicbp)
            bmi = int(bmi)
            lvedd = int(lvedd)
            bnp = int(bnp)
            creatnine = int(creatnine)
            cholestrol = int(cholestrol)
            cem = int(cem)
            potassium = int(potassium)
            Xdata = [ [pulse,systolicbp,bmi,lvedd,bnp,creatnine,cholestrol,cem,potassium ] ]
            
            try:
                with open('hdad/HF_Classification_Model.pkl', 'rb') as f:
                    clf = pickle.load(f)
                x=clf.predict(Xdata)
            except :
                x=2

            if x == 1:
               message2="Patient Have HFpEF"
            elif x == 0:
                message2="Patient Have HFrEF"
            else:
                message2="error"
            path = os.getcwd()+'/hdad/Diagnostics-Counter.txt'
            f = open(path, 'r')
            DiagnosticsCounter = int(f.read())
            f.close()
            f = open(path, 'w')
            f.write(str(DiagnosticsCounter+1))
            f.close()
            return render_template('patientdetails.html',messagechf="",messageheart="",messagehf=message2,messagechfcomplete="",messagehfcomplete="",heartlist=heartlist,diagnosticsDetectionCounter="",diagnosticsExecutionCounter="" ,heartform = heartform , name=current_user.DocName,completeform=completeform,data=Patientdata,diagdata=diag,dd=lastDiagDate,chfform=chfform, hfform=hfform,form=3, message="",message2=message2,alert=alert,hf=hf,chf=chf,featureform=featureform,delete=delete)
        elif request.form.get("deletepatient"):
            if delete.validate_on_submit():
                if delete.Input.data == 'Delete':
                    
                    delete_q = Patient.__table__.delete().where(Patient.PatientId == pid)
                    db.session.execute(delete_q)
                    db.session.commit()
                    delete_q = PatientDiagnostics.__table__.delete().where(PatientDiagnostics.PatientId == pid)
                    db.session.execute(delete_q)
                    db.session.commit()
                    delete_q = CHF.__table__.delete().where(CHF.PatientId == pid)
                    db.session.execute(delete_q)
                    db.session.commit()
                    delete_q = HF.__table__.delete().where(HF.PatientId == pid)
                    db.session.execute(delete_q)
                    db.session.commit()
                    return redirect(url_for('dashboard'))
                else :
                    return redirect(url_for('showpatient',pid=pid))
            else :
                return redirect(url_for('showpatient',pid=pid))
        elif request.form.get("download") :
            try:
                return send_from_directory('static',filename='templateDiagnostics.zip', as_attachment=True)
            except FileNotFoundError:
                abort(404)
        elif request.form.get("csvu"):
            DiagnosticsId = 0
            diagnosticsDetectionCounter=0
            diagnosticsExecutionCounter=0
            try:
                with open('hdad/CHF_Detection_Model.pkl', 'rb') as f:
                    clfchf = pickle.load(f)
            except :
                print("Cannot Import CHF Pickle")
            try :
                with open('hdad/HF_Classification_Model.pkl', 'rb') as f:
                    clfhf = pickle.load(f)
            except :
                print("Cannot Import HF Pickle")
            try:
                with open('hdad/Heart_disease_CatBoost_Model.pkl', 'rb') as f:
                    clfheart = pickle.load(f)
            except :
                print("Cannot Import Heart Pickle")
            
            try :
                csv_file = request.files['file']
                df = pd.read_csv(csv_file,encoding='latin1')
                df2 = df.copy()
                df.dropna()
                for X, y  in df.iterrows():
                    print(X)
                    try :
                        if y['Pulse'] and y['NYHA-Cardiac-Function-Classification'] and y['Killip-Grade'] and y['Brain-Natriuretic-Peptide'] and y['Cystatin'] and y['Potassium'] :
                            diagnosticsDetectionCounter=diagnosticsDetectionCounter+1
                            if y['Pulse'] >=30 and y['NYHA-Cardiac-Function-Classification'] >=1  and y['Killip-Grade']>=1 and y['Brain-Natriuretic-Peptide']>=1 and y['Cystatin']>=0 and y['Potassium']>=0 and y['Pulse']<=300 and y['NYHA-Cardiac-Function-Classification']<=4 and y['Killip-Grade']<=4 and y['Brain-Natriuretic-Peptide']<=8001 and y['Cystatin']<=7 and y['Potassium']<=10 :
                                pulse = y['Pulse']
                                nyha = y['NYHA-Cardiac-Function-Classification']
                                killip = y['Killip-Grade']
                                bnp = y['Brain-Natriuretic-Peptide']
                                cystatin =  y['Cystatin']
                                potassium = y['Potassium']
                                pulse = int(pulse)
                                nyha = int(nyha)
                                killip = int(killip)
                                bnp =   float(bnp)
                                cystatin =  float(cystatin)
                                potassium = float(potassium)
                                Xdata = [ [pulse,nyha,killip,bnp,cystatin,potassium ] ]
                                pulse = str(pulse)
                                nyha = str(nyha)
                                killip = str(killip)
                                bnp = str(bnp)
                                cystatin = str(cystatin)
                                potassium = str(potassium)
                                if clfchf:
                                    x=clfchf.predict(Xdata)
                                    if x == 1:
                                        result="Yes"
                                    elif x == 0:
                                        result="No"
                                    else:
                                        result="error"
                                    new_record = PatientDiagnostics(PatientId=Patientdata.PatientId, PatientDocId=current_user.DocId, DiagnosticsFor=4)
                                    db.session.add(new_record)
                                    db.session.commit()
                                    DiagnosticsId = PatientDiagnostics.query.filter_by(PatientId=Patientdata.PatientId).order_by(PatientDiagnostics.id.desc()).first()
                                    if DiagnosticsId:
                                        chfNew = CHF(DiagnosticsId=DiagnosticsId.id,PatientId=Patientdata.PatientId,PatientDocId=current_user.DocId, Pulse=pulse, NYHA=nyha, Killip=killip,BNP=bnp,Cystatin=cystatin,Potassium=potassium,Result=result)
                                        db.session.add(chfNew)
                                        db.session.commit()
                                        diagnosticsExecutionCounter=diagnosticsExecutionCounter+1
                    except :
                        print("Error Running CHF Diagnostics in Bulk Diagnostics") 
                    try :      
                        if y['Pulse'] and y['SystolicBP'] and y['BMI'] and y['left-ventricular-end-diastolic-diameter-LV'] and y['Brain-Natriuretic-Peptide'] and y['Creatnine-Enzymetic-Method'] and y['Potassium'] and y['Cholesterol'] and y['Creatnine-Kinase']:
                            diagnosticsDetectionCounter=diagnosticsDetectionCounter+1
                            if y['Pulse']>=30 and y['SystolicBP']>=30 and y['BMI']>=10 and y['left-ventricular-end-diastolic-diameter-LV']>=5 and y['Brain-Natriuretic-Peptide']>=1 and y['Creatnine-Enzymetic-Method']>=30 and y['Potassium']>=0 and y['Cholesterol']>=0 and y['Creatnine-Kinase']>=10 and y['Pulse']<=300 and y['SystolicBP']<=300 and y['BMI']<=50 and y['left-ventricular-end-diastolic-diameter-LV']<=200 and y['Brain-Natriuretic-Peptide']<=8001 and y['Creatnine-Enzymetic-Method']<=300 and y['Potassium']<=10 and y['Cholesterol']<=10 and y['Creatnine-Kinase'] <=300 :
                                pulse = y['Pulse']
                                systolicbp = y['SystolicBP']
                                bmi=y['BMI']
                                lvedd = y['left-ventricular-end-diastolic-diameter-LV']
                                bnp =  y['Brain-Natriuretic-Peptide']
                                creatnine=y['Creatnine-Kinase']
                                cholestrol = y['Cholesterol']
                                cem = y['Creatnine-Enzymetic-Method']
                                potassium = y['Potassium']


                                Xdata = [ [pulse,systolicbp,bmi,lvedd,bnp,creatnine,cholestrol,cem,potassium ] ]
                                pulse = int(pulse)
                                nyha = int(nyha)
                                bmi = float(bmi)
                                killip = int(killip)
                                bnp = float(bnp)
                                cystatin = float(cystatin)
                                potassium = float(potassium)
                                Xdata = [ [pulse,systolicbp,bmi,lvedd,bnp,creatnine,cholestrol,cem,potassium ] ]   
                                pulse = str(pulse)
                                nyha = str(nyha)
                                killip = str(killip)
                                bnp = str(bnp)
                                cystatin = str(cystatin)
                                potassium = str(potassium)
                                if clfhf:
                                    x=clfhf.predict(Xdata)
                                    
                                    if x == 1:
                                        result="HFpEF"
                                    elif x == 0:
                                        result="HFrEF"
                                    else:
                                        result="error"

                                    if DiagnosticsId:
                                        hfNew = HF(DiagnosticsId=DiagnosticsId.id,PatientId=Patientdata.PatientId,PatientDocId=current_user.DocId, Pulse=pulse, SystolicBP=systolicbp,BMI=bmi,LVEDD=lvedd,BNP=bnp,CreatnineKinase=creatnine,Cholestrol=cholestrol,CEM=cem,Potassium=potassium,Result=result)
                                        db.session.add(hfNew)
                                        db.session.commit()
                                        diagnosticsExecutionCounter=diagnosticsExecutionCounter+1
                                    else :
                                        new_record = PatientDiagnostics(PatientId=Patientdata.PatientId, PatientDocId=current_user.DocId, DiagnosticsFor=4)
                                        db.session.add(new_record)
                                        db.session.commit()
                                        DiagnosticsId = PatientDiagnostics.query.filter_by(PatientId=Patientdata.PatientId).order_by(PatientDiagnostics.id.desc()).first()
                                        if DiagnosticsId:
                                            hfNew = HF(DiagnosticsId=DiagnosticsId.id,PatientId=Patientdata.PatientId,PatientDocId=current_user.DocId, Pulse=pulse, SystolicBP=systolicbp,BMI=bmi,LVEDD=lvedd,BNP=bnp,CreatnineKinase=creatnine,Cholestrol=cholestrol,CEM=cem,Potassium=potassium,Result=result)
                                            db.session.add(hfNew)
                                            db.session.commit()
                                            diagnosticsExecutionCounter=diagnosticsExecutionCounter+1
                    except :
                        print("Error Running HF Diagnostics in Bulk Diagnostics") 
                    try:      
                        if y['Age'] or y['Sex'] or y['CP'] or y['BP'] or y['FBS'] or y['ECG'] or y['Thalach'] or y['Exang'] or y['OldPeak'] or y['Slope'] or y['Ca'] or y['Thal'] or  y['Cholesterol']:
                            diagnosticsDetectionCounter=diagnosticsDetectionCounter+1
                            if y['Age']>0 and y['Sex']==0 and y['CP']>=1 and y['BP']>=30 and y['FBS']>=0 and y['ECG']>=0 and y['Thalach']>=30 and y['Exang']>=0 and y['OldPeak']>=0 and y['Slope']>=1 and y['Ca']>=0 and y['Thal']>=0 and  y['Cholesterol']>=0 and y['Age']<=130 or y['Sex']<=1 and y['CP']<=4 and y['BP']<=300 and y['FBS']<=1 and y['ECG']<=2 and y['Thalach']<=300 and y['Exang']<=1 and y['OldPeak']<=15 and y['Slope']<=30 and y['Ca']<=3 and y['Thal']<=7 and  y['Cholesterol']<=10 :
                                age = y['Age']                            
                                sex = y['Sex']
                                cp = y['CP']
                                bp = y['BP']
                                cholestrol=y['Cholesterol']* 0.02586
                                fbs = y['FBS']                            
                                ecg = y['ECG']
                                thalach = y['Thalach']
                                exang = y['Exang']
                                oldpeak = y['OldPeak']
                                slope = y['Slope']
                                ca = y['Ca']
                                thal = y['Thal']
                                
                                
                                Xdata = [ [age,sex,cp,bp,cholestrol,fbs,ecg,thalach,exang,oldpeak,slope,ca,thal] ]
                                
                                
                                if clfheart:
                                    x=clfheart.predict(Xdata)
                                    if x == 1:
                                        resultheart="Yes"
                                    elif x == 0:
                                        resultheart="No"
                                    else:
                                        resultheart="Error"
                                    if DiagnosticsId:
                                        heart = HeartDisease(DiagnosticsId=DiagnosticsId.id,PatientId=pid,PatientDocId=current_user.DocId,Age=age,Sex=sex,CP=cp,BP=bp,Cholestrol=cholestrol,FBS=fbs,ECG=ecg,Thalach=thalach,Exang=exang,OldPeak=oldpeak,Slope=slope,ca=ca,Thal=thal ,Result=resultheart)
                                        db.session.add(heart)
                                        db.session.commit()
                                        diagnosticsExecutionCounter=diagnosticsExecutionCounter+1
                                    else :
                                        new_record = PatientDiagnostics(PatientId=Patientdata.PatientId, PatientDocId=current_user.DocId, DiagnosticsFor=4)
                                        db.session.add(new_record)
                                        db.session.commit()
                                        DiagnosticsId = PatientDiagnostics.query.filter_by(PatientId=Patientdata.PatientId).order_by(PatientDiagnostics.id.desc()).first()
                                        if DiagnosticsId:
                                            heart = HeartDisease(DiagnosticsId=DiagnosticsId.id,PatientId=pid,PatientDocId=current_user.DocId,Age=age,Sex=sex,CP=cp,BP=bp,Cholestrol=cholestrol,FBS=fbs,ECG=ecg,Thalach=thalach,Exang=exang,OldPeak=oldpeak,Slope=slope,ca=ca,Thal=thal,Result=resultheart)
                                            db.session.add(heart)
                                            db.session.commit()
                                            diagnosticsExecutionCounter=diagnosticsExecutionCounter+1
                    except :
                        print("Error Running Heart Diagnostics in Bulk Diagnostics")
                    
            except :
                print("Error Running Bulk Diagnostics")
                return render_template('patientdetails.html',messagechf="",messageheart="",messagehf="",messagechfcomplete="",messagehfcomplete="",heartlist=heartlist,diagnosticsDetectionCounter=diagnosticsDetectionCounter,diagnosticsExecutionCounter=diagnosticsExecutionCounter ,heartform = heartform ,  name=current_user.DocName,completeform=completeform,data=Patientdata,diagdata=diag,dd=lastDiagDate,chfform=chfform, hfform=hfform,form=7, message="",message2="",alert=alert,hf=hf,chf=chf,featureform=featureform,delete=delete)

            print("completed bulk diagnostics")       
            path = os.getcwd()+'/hdad/Diagnostics-Counter.txt'
            f = open(path, 'r')
            DiagnosticsCounter = int(f.read())
            f.close()
            f = open(path, 'w')
            f.write(str(DiagnosticsCounter+diagnosticsExecutionCounter))
            f.close()
            return render_template('patientdetails.html',messagechf="",messageheart="",messagehf="",messagechfcomplete="",messagehfcomplete="",heartlist=heartlist,diagnosticsDetectionCounter=diagnosticsDetectionCounter,diagnosticsExecutionCounter=diagnosticsExecutionCounter ,heartform = heartform ,  name=current_user.DocName,completeform=completeform,data=Patientdata,diagdata=diag,dd=lastDiagDate,chfform=chfform, hfform=hfform,form=7, message="",message2="",alert=alert,hf=hf,chf=chf,featureform=featureform,delete=delete)
        elif featureform.validate_on_submit and request.form.get("featureform"):
            common_feature = ["Pulse","BNP","Potassium"]
            chf_feature = ["NYHA","Killip","Cystatin"]
            hf_feature = ["SystolicBP","LVEDD","CreatnineKinase","Cholestrol","CEM"]
            if featureform.Feature2.data=='Date':
                features=[]
                dates=[]
                try:
                    feature = CHF.query.filter_by(PatientId=pid).all()
                    for row in feature:
                        if featureform.Feature1.data == 'BNP' :
                            features = np.append(features,float(row.BNP))
                        elif featureform.Feature1.data == 'Pulse' :
                            features = np.append(features,float(row.Pulse))
                        elif featureform.Feature1.data == 'Age' :
                            features = np.append(features,float(row.Age))
                        elif featureform.Feature1.data == 'Cholestrol' :
                            features = np.append(features,float(row.Cholestrol))
                        elif featureform.Feature1.data == 'CEM' :
                            features = np.append(features,float(row.CEM))
                        elif featureform.Feature1.data == 'CreatnineKinase' :
                            features = np.append(features,float(row.CreatnineKinase))
                        elif featureform.Feature1.data == 'Cystatin' :
                            features = np.append(features,float(row.Cystatin))
                        elif featureform.Feature1.data == 'Killip' :
                            features = np.append(features,float(row.Killip))
                        elif featureform.Feature1.data == 'BMI' :
                            features = np.append(features,float(row.BMI))
                        elif featureform.Feature1.data == 'LVEDD' :
                            features = np.append(features,float(row.LVEDD))
                        elif featureform.Feature1.data == 'NYHA' :
                            features = np.append(features,float(row.NYHA))
                        elif featureform.Feature1.data == 'Potassium' :
                            features = np.append(features,float(row.Potassium))
                        elif featureform.Feature1.data == 'SystolicBP' :
                            features = np.append(features,float(row.SystolicBP))
                        elif featureform.Feature1.data == 'Sex' :
                            features = np.append(features,float(row.Sex))
                        elif featureform.Feature1.data == 'CP' :
                            features = np.append(features,float(row.CP))
                        elif featureform.Feature1.data == 'BP' :
                            features = np.append(features,float(row.BP))
                        elif featureform.Feature1.data == 'CholestrolHeart' :
                            features = np.append(features,float(row.CholestrolHeart))
                        elif featureform.Feature1.data == 'ECG' :
                            features = np.append(features,float(row.ECG))
                        elif featureform.Feature1.data == 'Thalach' :
                            features = np.append(features,float(row.Thalach))
                        elif featureform.Feature1.data == 'Exang' :
                            features = np.append(features,float(row.Exang))
                        elif featureform.Feature1.data == 'OldPeak' :
                            features = np.append(features,float(row.OldPeak))
                        elif featureform.Feature1.data == 'Slope' :
                            features = np.append(features,float(row.Slope))
                        elif featureform.Feature1.data == 'Ca' :
                            features = np.append(features,float(row.Ca))
                        elif featureform.Feature1.data == 'Thal' :
                            features = np.append(features,float(row.Thal))
                        dates = np.append(dates,str(row.DiagnosticsDate))
                        print(features,dates)
                except:
                    print("feature 1 not in chf")
                try:
                    feature = HF.query.filter_by(PatientId=pid).all()
                    for row in feature:
                        if featureform.Feature1.data == 'BNP' :
                            features = np.append(features,float(row.BNP))
                        elif featureform.Feature1.data == 'Pulse' :
                            features = np.append(features,float(row.Pulse))
                        elif featureform.Feature1.data == 'Age' :
                            features = np.append(features,float(row.Age))
                        elif featureform.Feature1.data == 'Cholestrol' :
                            features = np.append(features,float(row.Cholestrol))
                        elif featureform.Feature1.data == 'CEM' :
                            features = np.append(features,float(row.CEM))
                        elif featureform.Feature1.data == 'CreatnineKinase' :
                            features = np.append(features,float(row.CreatnineKinase))
                        elif featureform.Feature1.data == 'Cystatin' :
                            features = np.append(features,float(row.Cystatin))
                        elif featureform.Feature1.data == 'Killip' :
                            features = np.append(features,float(row.Killip))
                        elif featureform.Feature1.data == 'BMI' :
                            features = np.append(features,float(row.BMI))
                        elif featureform.Feature1.data == 'LVEDD' :
                            features = np.append(features,float(row.LVEDD))
                        elif featureform.Feature1.data == 'NYHA' :
                            features = np.append(features,float(row.NYHA))
                        elif featureform.Feature1.data == 'Potassium' :
                            features = np.append(features,float(row.Potassium))
                        elif featureform.Feature1.data == 'SystolicBP' :
                            features = np.append(features,float(row.SystolicBP))
                        elif featureform.Feature1.data == 'Sex' :
                            features = np.append(features,float(row.Sex))
                        elif featureform.Feature1.data == 'CP' :
                            features = np.append(features,float(row.CP))
                        elif featureform.Feature1.data == 'BP' :
                            features = np.append(features,float(row.BP))
                        elif featureform.Feature1.data == 'CholestrolHeart' :
                            features = np.append(features,float(row.CholestrolHeart))
                        elif featureform.Feature1.data == 'ECG' :
                            features = np.append(features,float(row.ECG))
                        elif featureform.Feature1.data == 'Thalach' :
                            features = np.append(features,float(row.Thalach))
                        elif featureform.Feature1.data == 'Exang' :
                            features = np.append(features,float(row.Exang))
                        elif featureform.Feature1.data == 'OldPeak' :
                            features = np.append(features,float(row.OldPeak))
                        elif featureform.Feature1.data == 'Slope' :
                            features = np.append(features,float(row.Slope))
                        elif featureform.Feature1.data == 'Ca' :
                            features = np.append(features,float(row.Ca))
                        elif featureform.Feature1.data == 'Thal' :
                            features = np.append(features,float(row.Thal))
                        dates = np.append(dates,str(row.DiagnosticsDate))
                        print(features,dates)
                except:
                    print("feature 1 not in hf")
                try:
                    feature = HeartDisease.query.filter_by(PatientId=pid).all()
                    for row in feature:
                        if featureform.Feature1.data == 'BNP' :
                            features = np.append(features,float(row.BNP))
                        elif featureform.Feature1.data == 'Pulse' :
                            features = np.append(features,float(row.Pulse))
                        elif featureform.Feature1.data == 'Age' :
                            features = np.append(features,float(row.Age))
                        elif featureform.Feature1.data == 'Cholestrol' :
                            features = np.append(features,float(row.Cholestrol))
                        elif featureform.Feature1.data == 'CEM' :
                            features = np.append(features,float(row.CEM))
                        elif featureform.Feature1.data == 'CreatnineKinase' :
                            features = np.append(features,float(row.CreatnineKinase))
                        elif featureform.Feature1.data == 'Cystatin' :
                            features = np.append(features,float(row.Cystatin))
                        elif featureform.Feature1.data == 'Killip' :
                            features = np.append(features,float(row.Killip))
                        elif featureform.Feature1.data == 'BMI' :
                            features = np.append(features,float(row.BMI))
                        elif featureform.Feature1.data == 'LVEDD' :
                            features = np.append(features,float(row.LVEDD))
                        elif featureform.Feature1.data == 'NYHA' :
                            features = np.append(features,float(row.NYHA))
                        elif featureform.Feature1.data == 'Potassium' :
                            features = np.append(features,float(row.Potassium))
                        elif featureform.Feature1.data == 'SystolicBP' :
                            features = np.append(features,float(row.SystolicBP))
                        elif featureform.Feature1.data == 'Sex' :
                            features = np.append(features,float(row.Sex))
                        elif featureform.Feature1.data == 'CP' :
                            features = np.append(features,float(row.CP))
                        elif featureform.Feature1.data == 'BP' :
                            features = np.append(features,float(row.BP))
                        elif featureform.Feature1.data == 'CholestrolHeart' :
                            features = np.append(features,float(row.CholestrolHeart))
                        elif featureform.Feature1.data == 'ECG' :
                            features = np.append(features,float(row.ECG))
                        elif featureform.Feature1.data == 'Thalach' :
                            features = np.append(features,float(row.Thalach))
                        elif featureform.Feature1.data == 'Exang' :
                            features = np.append(features,float(row.Exang))
                        elif featureform.Feature1.data == 'OldPeak' :
                            features = np.append(features,float(row.OldPeak))
                        elif featureform.Feature1.data == 'Slope' :
                            features = np.append(features,float(row.Slope))
                        elif featureform.Feature1.data == 'Ca' :
                            features = np.append(features,float(row.Ca))
                        elif featureform.Feature1.data == 'Thal' :
                            features = np.append(features,float(row.Thal))
                        dates = np.append(dates,str(row.DiagnosticsDate))
                        print(features,dates)
                except:
                    print("feature 1 not in heart disease")
                
                
                    
                fname = featureform.Feature1.data
                
                image = create_graphs(pid,fname,features,dates)
            else :
                features1=[]
                features2=[]
                features=[]
                try:
                    feature = CHF.query.filter_by(PatientId=pid).all()
                    for row in feature:
                        if featureform.Feature1.data == 'BNP' :
                            features = np.append(features,float(row.BNP))
                        elif featureform.Feature1.data == 'Pulse' :
                            features = np.append(features,float(row.Pulse))
                        elif featureform.Feature1.data == 'Age' :
                            features = np.append(features,float(row.Age))
                        elif featureform.Feature1.data == 'Cholestrol' :
                            features = np.append(features,float(row.Cholestrol))
                        elif featureform.Feature1.data == 'CEM' :
                            features = np.append(features,float(row.CEM))
                        elif featureform.Feature1.data == 'CreatnineKinase' :
                            features = np.append(features,float(row.CreatnineKinase))
                        elif featureform.Feature1.data == 'Cystatin' :
                            features = np.append(features,float(row.Cystatin))
                        elif featureform.Feature1.data == 'Killip' :
                            features = np.append(features,float(row.Killip))
                        elif featureform.Feature1.data == 'BMI' :
                            features = np.append(features,float(row.BMI))
                        elif featureform.Feature1.data == 'LVEDD' :
                            features = np.append(features,float(row.LVEDD))
                        elif featureform.Feature1.data == 'NYHA' :
                            features = np.append(features,float(row.NYHA))
                        elif featureform.Feature1.data == 'Potassium' :
                            features = np.append(features,float(row.Potassium))
                        elif featureform.Feature1.data == 'SystolicBP' :
                            features = np.append(features,float(row.SystolicBP))
                        elif featureform.Feature1.data == 'Sex' :
                            features = np.append(features,float(row.Sex))
                        elif featureform.Feature1.data == 'CP' :
                            features = np.append(features,float(row.CP))
                        elif featureform.Feature1.data == 'BP' :
                            features = np.append(features,float(row.BP))
                        elif featureform.Feature1.data == 'CholestrolHeart' :
                            features = np.append(features,float(row.CholestrolHeart))
                        elif featureform.Feature1.data == 'ECG' :
                            features = np.append(features,float(row.ECG))
                        elif featureform.Feature1.data == 'Thalach' :
                            features = np.append(features,float(row.Thalach))
                        elif featureform.Feature1.data == 'Exang' :
                            features = np.append(features,float(row.Exang))
                        elif featureform.Feature1.data == 'OldPeak' :
                            features = np.append(features,float(row.OldPeak))
                        elif featureform.Feature1.data == 'Slope' :
                            features = np.append(features,float(row.Slope))
                        elif featureform.Feature1.data == 'Ca' :
                            features = np.append(features,float(row.Ca))
                        elif featureform.Feature1.data == 'Thal' :
                            features = np.append(features,float(row.Thal))
                except:
                    print("feature 1 not in chf")
                try:
                    feature = HF.query.filter_by(PatientId=pid).all()
                    for row in feature:
                        if featureform.Feature1.data == 'BNP' :
                            features = np.append(features,float(row.BNP))
                        elif featureform.Feature1.data == 'Pulse' :
                            features = np.append(features,float(row.Pulse))
                        elif featureform.Feature1.data == 'Age' :
                            features = np.append(features,float(row.Age))
                        elif featureform.Feature1.data == 'Cholestrol' :
                            features = np.append(features,float(row.Cholestrol))
                        elif featureform.Feature1.data == 'CEM' :
                            features = np.append(features,float(row.CEM))
                        elif featureform.Feature1.data == 'CreatnineKinase' :
                            features = np.append(features,float(row.CreatnineKinase))
                        elif featureform.Feature1.data == 'Cystatin' :
                            features = np.append(features,float(row.Cystatin))
                        elif featureform.Feature1.data == 'Killip' :
                            features = np.append(features,float(row.Killip))
                        elif featureform.Feature1.data == 'BMI' :
                            features = np.append(features,float(row.BMI))
                        elif featureform.Feature1.data == 'LVEDD' :
                            features = np.append(features,float(row.LVEDD))
                        elif featureform.Feature1.data == 'NYHA' :
                            features = np.append(features,float(row.NYHA))
                        elif featureform.Feature1.data == 'Potassium' :
                            features = np.append(features,float(row.Potassium))
                        elif featureform.Feature1.data == 'SystolicBP' :
                            features = np.append(features,float(row.SystolicBP))
                        elif featureform.Feature1.data == 'Sex' :
                            features = np.append(features,float(row.Sex))
                        elif featureform.Feature1.data == 'CP' :
                            features = np.append(features,float(row.CP))
                        elif featureform.Feature1.data == 'BP' :
                            features = np.append(features,float(row.BP))
                        elif featureform.Feature1.data == 'CholestrolHeart' :
                            features = np.append(features,float(row.CholestrolHeart))
                        elif featureform.Feature1.data == 'ECG' :
                            features = np.append(features,float(row.ECG))
                        elif featureform.Feature1.data == 'Thalach' :
                            features = np.append(features,float(row.Thalach))
                        elif featureform.Feature1.data == 'Exang' :
                            features = np.append(features,float(row.Exang))
                        elif featureform.Feature1.data == 'OldPeak' :
                            features = np.append(features,float(row.OldPeak))
                        elif featureform.Feature1.data == 'Slope' :
                            features = np.append(features,float(row.Slope))
                        elif featureform.Feature1.data == 'Ca' :
                            features = np.append(features,float(row.Ca))
                        elif featureform.Feature1.data == 'Thal' :
                            features = np.append(features,float(row.Thal))
                except:
                    print("feature 1 not in hf")
                try:
                    feature = HeartDisease.query.filter_by(PatientId=pid).all()
                    for row in feature:
                        if featureform.Feature1.data == 'BNP' :
                            features = np.append(features,float(row.BNP))
                        elif featureform.Feature1.data == 'Pulse' :
                            features = np.append(features,float(row.Pulse))
                        elif featureform.Feature1.data == 'Age' :
                            features = np.append(features,float(row.Age))
                        elif featureform.Feature1.data == 'Cholestrol' :
                            features = np.append(features,float(row.Cholestrol))
                        elif featureform.Feature1.data == 'CEM' :
                            features = np.append(features,float(row.CEM))
                        elif featureform.Feature1.data == 'CreatnineKinase' :
                            features = np.append(features,float(row.CreatnineKinase))
                        elif featureform.Feature1.data == 'Cystatin' :
                            features = np.append(features,float(row.Cystatin))
                        elif featureform.Feature1.data == 'Killip' :
                            features = np.append(features,float(row.Killip))
                        elif featureform.Feature1.data == 'BMI' :
                            features = np.append(features,float(row.BMI))
                        elif featureform.Feature1.data == 'LVEDD' :
                            features = np.append(features,float(row.LVEDD))
                        elif featureform.Feature1.data == 'NYHA' :
                            features = np.append(features,float(row.NYHA))
                        elif featureform.Feature1.data == 'Potassium' :
                            features = np.append(features,float(row.Potassium))
                        elif featureform.Feature1.data == 'SystolicBP' :
                            features = np.append(features,float(row.SystolicBP))
                        elif featureform.Feature1.data == 'Sex' :
                            features = np.append(features,float(row.Sex))
                        elif featureform.Feature1.data == 'CP' :
                            features = np.append(features,float(row.CP))
                        elif featureform.Feature1.data == 'BP' :
                            features = np.append(features,float(row.BP))
                        elif featureform.Feature1.data == 'CholestrolHeart' :
                            features = np.append(features,float(row.CholestrolHeart))
                        elif featureform.Feature1.data == 'ECG' :
                            features = np.append(features,float(row.ECG))
                        elif featureform.Feature1.data == 'Thalach' :
                            features = np.append(features,float(row.Thalach))
                        elif featureform.Feature1.data == 'Exang' :
                            features = np.append(features,float(row.Exang))
                        elif featureform.Feature1.data == 'OldPeak' :
                            features = np.append(features,float(row.OldPeak))
                        elif featureform.Feature1.data == 'Slope' :
                            features = np.append(features,float(row.Slope))
                        elif featureform.Feature1.data == 'Ca' :
                            features = np.append(features,float(row.Ca))
                        elif featureform.Feature1.data == 'Thal' :
                            features = np.append(features,float(row.Thal))
                except:
                    print("feature 1 not in heart disease")
                features1 = features
                try:
                    feature = CHF.query.filter_by(PatientId=pid).all()
                    for row in feature:
                        if featureform.Feature2.data == 'BNP' :
                            features = np.append(features,float(row.BNP))
                        elif featureform.Feature2.data == 'Pulse' :
                            features = np.append(features,float(row.Pulse))
                        elif featureform.Feature2.data == 'Age' :
                            features = np.append(features,float(row.Age))
                        elif featureform.Feature2.data == 'Cholestrol' :
                            features = np.append(features,float(row.Cholestrol))
                        elif featureform.Feature2.data == 'CEM' :
                            features = np.append(features,float(row.CEM))
                        elif featureform.Feature2.data == 'CreatnineKinase' :
                            features = np.append(features,float(row.CreatnineKinase))
                        elif featureform.Feature2.data == 'Cystatin' :
                            features = np.append(features,float(row.Cystatin))
                        elif featureform.Feature2.data == 'Killip' :
                            features = np.append(features,float(row.Killip))
                        elif featureform.Feature2.data == 'BMI' :
                            features = np.append(features,float(row.BMI))
                        elif featureform.Feature2.data == 'LVEDD' :
                            features = np.append(features,float(row.LVEDD))
                        elif featureform.Feature2.data == 'NYHA' :
                            features = np.append(features,float(row.NYHA))
                        elif featureform.Feature2.data == 'Potassium' :
                            features = np.append(features,float(row.Potassium))
                        elif featureform.Feature2.data == 'SystolicBP' :
                            features = np.append(features,float(row.SystolicBP))
                        elif featureform.Feature2.data == 'Sex' :
                            features = np.append(features,float(row.Sex))
                        elif featureform.Feature2.data == 'CP' :
                            features = np.append(features,float(row.CP))
                        elif featureform.Feature2.data == 'BP' :
                            features = np.append(features,float(row.BP))
                        elif featureform.Feature2.data == 'CholestrolHeart' :
                            features = np.append(features,float(row.CholestrolHeart))
                        elif featureform.Feature2.data == 'ECG' :
                            features = np.append(features,float(row.ECG))
                        elif featureform.Feature2.data == 'Thalach' :
                            features = np.append(features,float(row.Thalach))
                        elif featureform.Feature2.data == 'Exang' :
                            features = np.append(features,float(row.Exang))
                        elif featureform.Feature2.data == 'OldPeak' :
                            features = np.append(features,float(row.OldPeak))
                        elif featureform.Feature2.data == 'Slope' :
                            features = np.append(features,float(row.Slope))
                        elif featureform.Feature2.data == 'Ca' :
                            features = np.append(features,float(row.Ca))
                        elif featureform.Feature2.data == 'Thal' :
                            features = np.append(features,float(row.Thal))
                except:
                    print("feature 2 not in chf")
                try:
                    feature = HF.query.filter_by(PatientId=pid).all()
                    for row in feature:
                        if featureform.Feature2.data == 'BNP' :
                            features = np.append(features,float(row.BNP))
                        elif featureform.Feature2.data == 'Pulse' :
                            features = np.append(features,float(row.Pulse))
                        elif featureform.Feature2.data == 'Age' :
                            features = np.append(features,float(row.Age))
                        elif featureform.Feature2.data == 'Cholestrol' :
                            features = np.append(features,float(row.Cholestrol))
                        elif featureform.Feature2.data == 'CEM' :
                            features = np.append(features,float(row.CEM))
                        elif featureform.Feature2.data == 'CreatnineKinase' :
                            features = np.append(features,float(row.CreatnineKinase))
                        elif featureform.Feature2.data == 'Cystatin' :
                            features = np.append(features,float(row.Cystatin))
                        elif featureform.Feature2.data == 'Killip' :
                            features = np.append(features,float(row.Killip))
                        elif featureform.Feature2.data == 'BMI' :
                            features = np.append(features,float(row.BMI))
                        elif featureform.Feature2.data == 'LVEDD' :
                            features = np.append(features,float(row.LVEDD))
                        elif featureform.Feature2.data == 'NYHA' :
                            features = np.append(features,float(row.NYHA))
                        elif featureform.Feature2.data == 'Potassium' :
                            features = np.append(features,float(row.Potassium))
                        elif featureform.Feature2.data == 'SystolicBP' :
                            features = np.append(features,float(row.SystolicBP))
                        elif featureform.Feature2.data == 'Sex' :
                            features = np.append(features,float(row.Sex))
                        elif featureform.Feature2.data == 'CP' :
                            features = np.append(features,float(row.CP))
                        elif featureform.Feature2.data == 'BP' :
                            features = np.append(features,float(row.BP))
                        elif featureform.Feature2.data == 'CholestrolHeart' :
                            features = np.append(features,float(row.CholestrolHeart))
                        elif featureform.Feature2.data == 'ECG' :
                            features = np.append(features,float(row.ECG))
                        elif featureform.Feature2.data == 'Thalach' :
                            features = np.append(features,float(row.Thalach))
                        elif featureform.Feature2.data == 'Exang' :
                            features = np.append(features,float(row.Exang))
                        elif featureform.Feature2.data == 'OldPeak' :
                            features = np.append(features,float(row.OldPeak))
                        elif featureform.Feature2.data == 'Slope' :
                            features = np.append(features,float(row.Slope))
                        elif featureform.Feature2.data == 'Ca' :
                            features = np.append(features,float(row.Ca))
                        elif featureform.Feature2.data == 'Thal' :
                            features = np.append(features,float(row.Thal))
                except:
                    print("feature 2 not in hf")
                try:
                    feature = HeartDisease.query.filter_by(PatientId=pid).all()
                    for row in feature:
                        if featureform.Feature2.data == 'BNP' :
                            features = np.append(features,float(row.BNP))
                        elif featureform.Feature2.data == 'Pulse' :
                            features = np.append(features,float(row.Pulse))
                        elif featureform.Feature2.data == 'Age' :
                            features = np.append(features,float(row.Age))
                        elif featureform.Feature2.data == 'Cholestrol' :
                            features = np.append(features,float(row.Cholestrol))
                        elif featureform.Feature2.data == 'CEM' :
                            features = np.append(features,float(row.CEM))
                        elif featureform.Feature2.data == 'CreatnineKinase' :
                            features = np.append(features,float(row.CreatnineKinase))
                        elif featureform.Feature2.data == 'Cystatin' :
                            features = np.append(features,float(row.Cystatin))
                        elif featureform.Feature2.data == 'Killip' :
                            features = np.append(features,float(row.Killip))
                        elif featureform.Feature2.data == 'BMI' :
                            features = np.append(features,float(row.BMI))
                        elif featureform.Feature2.data == 'LVEDD' :
                            features = np.append(features,float(row.LVEDD))
                        elif featureform.Feature2.data == 'NYHA' :
                            features = np.append(features,float(row.NYHA))
                        elif featureform.Feature2.data == 'Potassium' :
                            features = np.append(features,float(row.Potassium))
                        elif featureform.Feature2.data == 'SystolicBP' :
                            features = np.append(features,float(row.SystolicBP))
                        elif featureform.Feature2.data == 'Sex' :
                            features = np.append(features,float(row.Sex))
                        elif featureform.Feature2.data == 'CP' :
                            features = np.append(features,float(row.CP))
                        elif featureform.Feature2.data == 'BP' :
                            features = np.append(features,float(row.BP))
                        elif featureform.Feature2.data == 'CholestrolHeart' :
                            features = np.append(features,float(row.CholestrolHeart))
                        elif featureform.Feature2.data == 'ECG' :
                            features = np.append(features,float(row.ECG))
                        elif featureform.Feature2.data == 'Thalach' :
                            features = np.append(features,float(row.Thalach))
                        elif featureform.Feature2.data == 'Exang' :
                            features = np.append(features,float(row.Exang))
                        elif featureform.Feature2.data == 'OldPeak' :
                            features = np.append(features,float(row.OldPeak))
                        elif featureform.Feature2.data == 'Slope' :
                            features = np.append(features,float(row.Slope))
                        elif featureform.Feature2.data == 'Ca' :
                            features = np.append(features,float(row.Ca))
                        elif featureform.Feature2.data == 'Thal' :
                            features = np.append(features,float(row.Thal))
                except:
                    print("feature 2 not in heart disease")
                features2 = features
                if features1.shape[0]>features2.shape[0]:
                    features1 = features1[0:features2.shape[0]]
                elif features1.shape[0]<features2.shape[0]:
                    features2 = features2[0:features1.shape[0]]

                image = create_graphs(pid,featureform.Feature1.data,features1,features2,False,featureform.Feature2.data)
            
            return render_template('patientdetails.html',heartform = heartform ,  name=current_user.DocName,completeform=completeform,data=Patientdata,diagdata=diag,dd=lastDiagDate,chfform=chfform, hfform=hfform, form=4, message="",message2="",alert=alert,chf=chf,hf=hf,image=image,featureform=featureform,delete=delete)
    return render_template('patientdetails.html',messagechf="",messageheart="",messagehf="",messagechfcomplete="",messagehfcomplete="",heartlist=heartlist,diagnosticsDetectionCounter="",diagnosticsExecutionCounter="" ,heartform = heartform ,  name=current_user.DocName,completeform=completeform,data=Patientdata,diagdata=diag,dd=lastDiagDate,chfform=chfform, hfform=hfform, form=0, message="",message2="",alert=alert,chf=chf,hf=hf,featureform=featureform,delete=delete)



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html')

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html')

@app.errorhandler(403)
def page_forbidden(e):
    return render_template('error.html')