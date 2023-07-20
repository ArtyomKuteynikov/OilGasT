# models.py

from flask_login import UserMixin
from . import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    photo = db.Column(db.String(1000))
    phone = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(1000))
    name = db.Column(db.String(100))
    surname = db.Column(db.String(100))
    second_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    born = db.Column(db.DateTime(timezone=True))
    gender = db.Column(db.String(10))
    org_name = db.Column(db.String(100))
    inn = db.Column(db.String(100))
    ogrn = db.Column(db.String(100))
    kpp = db.Column(db.String(100))
    bank = db.Column(db.String(100))
    bik = db.Column(db.String(100))
    kor_account = db.Column(db.String(100))
    account = db.Column(db.String(100))
    address = db.Column(db.String(1000))
    status = db.Column(db.String(100), default="inactive")
    org = db.Column(db.Integer, default=0)
    points = db.Column(db.Integer)
    token = db.Column(db.String(256))
    registered = db.Column(db.Integer)
    last_updated = db.Column(db.Integer)
    os = db.Column(db.String(10))
    deviceId = db.Column(db.String(100))
    email_notes = db.Column(db.Integer)
    sms_notes = db.Column(db.Integer)
    email_res = db.Column(db.Integer)
    referer = db.Column(db.Integer)


class Cars(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    user_id = db.Column(db.Integer)
    model = db.Column(db.String(100))
    num = db.Column(db.String(10))
    vin = db.Column(db.String(20))
    color = db.Column(db.Integer)
    oil = db.Column(db.Integer)
    petrol_type = db.Column(db.Integer)
    GSM_type = db.Column(db.Integer)
    ensurance = db.Column(db.DateTime(timezone=True))
    additional = db.Column(db.String(10000))


class Colors(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    name = db.Column(db.String(100))
    code = db.Column(db.String(10))


class Oils(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    name = db.Column(db.String(100))


class Petrol(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    name = db.Column(db.String(100))


class Codes(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    phone = db.Column(db.String(100))
    code = db.Column(db.String(10))


class Invitations(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    inviter = db.Column(db.Integer)
    code = db.Column(db.String(10))
    org = db.Column(db.Integer)


class Shares(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    from_ = db.Column(db.Integer)
    to_ = db.Column(db.Integer)
    petrol = db.Column(db.Integer)
    amount = inviter = db.Column(db.REAL)


class Stations(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
