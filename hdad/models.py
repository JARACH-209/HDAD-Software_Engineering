from datetime import datetime
from hdad import db
from flask_login import UserMixin
from pytz import timezone

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
    PatientDate = db.Column(db.DateTime, nullable=False,  default=datetime.now(timezone('Asia/Kolkata')))

class PatientDiagnostics(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    PatientId = db.Column(db.String(50))
    PatientDocId = db.Column(db.String(50) )
    DiagnosticsDate = db.Column(db.DateTime, nullable=False,  default=datetime.now(timezone('Asia/Kolkata')))
    DiagnosticsFor = db.Column(db.Integer, nullable=False)

class TokenTable(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    DocId = db.Column(db.String(50),nullable=False )
    Token = db.Column(db.String(10),nullable=False)
    TokenTime = db.Column(db.DateTime,nullable=False, default=datetime.now(timezone('Asia/Kolkata')))
    

class CHF(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    PatientId = db.Column(db.String(50))
    PatientDocId = db.Column(db.String(50) )
    DiagnosticsId = db.Column(db.Integer, nullable=False , unique=True)
    Pulse = db.Column(db.String,nullable=False)
    NYHA = db.Column(db.String,nullable=False)
    Killip = db.Column(db.String,nullable=False)
    BNP = db.Column(db.String,nullable=False)
    Cystatin = db.Column(db.String,nullable=False)
    Potassium = db.Column(db.String,nullable=False)
    DiagnosticsDate = db.Column(db.DateTime, nullable=False,default=datetime.now(timezone('Asia/Kolkata')))
    Result=db.Column(db.String(100), nullable=False)

class HF(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    PatientId = db.Column(db.String(50), nullable=False)
    PatientDocId = db.Column(db.String(50), nullable=False )
    DiagnosticsId = db.Column(db.Integer, nullable=False , unique=True)
    Pulse = db.Column(db.String,nullable=False)
    SystolicBP = db.Column(db.String,nullable=False)
    BMI = db.Column(db.String,nullable=False)
    LVEDD = db.Column(db.String,nullable=False)
    BNP = db.Column(db.String,nullable=False)
    CreatnineKinase = db.Column(db.String,nullable=False)
    Cholestrol = db.Column(db.String,nullable=False)
    CEM = db.Column(db.String,nullable=False)
    Potassium = db.Column(db.String,nullable=False)
    DiagnosticsDate = db.Column(db.DateTime, nullable=False,default=datetime.now(timezone('Asia/Kolkata')))
    Result=db.Column(db.String(100), nullable=False)

  
class HeartDisease(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    PatientId = db.Column(db.String(50), nullable=False)
    PatientDocId = db.Column(db.String(50), nullable=False )
    DiagnosticsId = db.Column(db.Integer, nullable=False , unique=True)
    Age = db.Column(db.String,nullable=False)
    Sex = db.Column(db.String,nullable=False)
    CP = db.Column(db.String,nullable=False)
    BP = db.Column(db.String,nullable=False)
    Cholestrol = db.Column(db.String,nullable=False)
    FBS = db.Column(db.String,nullable=False)
    ECG = db.Column(db.String,nullable=False)
    Thalach = db.Column(db.String,nullable=False)
    Exang = db.Column(db.String,nullable=False)
    OldPeak = db.Column(db.String,nullable=False)
    Slope = db.Column(db.String,nullable=False)
    ca = db.Column(db.String,nullable=False)
    Thal = db.Column(db.String,nullable=False)
    DiagnosticsDate = db.Column(db.DateTime, nullable=False,default=datetime.now(timezone('Asia/Kolkata')))
    Result=db.Column(db.String(100), nullable=False)
