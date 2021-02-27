import os
import secrets
from PIL import Image
from sqlalchemy.sql.expression import update
from sqlalchemy.sql.functions import count, user
from werkzeug.utils import secure_filename
from application import app, db, login_manager
from flask import render_template, request, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, ForeignKey, func, delete, DateTime,desc, and_
from sqlalchemy.orm import query, sessionmaker, relationship
from datetime import datetime, date, time, timedelta
from flask_login import login_user, current_user, logout_user, login_required
import datetime
import re
import sqlite3



class Userstore(db.Model):
  __tablename__ = 'Userstore'
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(20))
  phone=db.Column(db.String(20))
  password = db.Column(db.String(20))
  profileimage = db.Column(db.String(20), nullable=False, default='default.jpg')

  def __repr__(self) -> str:
    return f"Userstore('{self.id}','{self.username}', '{self.phone}', '{self.password}', '{self.profileimage}' )"

class Patient(db.Model):
  __tablename__ = 'Patient'
  id = db.Column(db.Integer, primary_key=True)
  pname = db.Column(db.String(20))
  age= db.Column(db.String(20))
  phone=db.Column(db.String(20))
  gender=db.Column(db.String(10))
  bgroup=db.Column(db.String(5))
  state=db.Column(db.String(15))
  address=db.Column(db.String(100))
  mstatus=db.Column(db.String(10))
  complaint=db.Column(db.String(5000))
  improvement=db.Column(db.String(5000))
  medicine_suggested=db.Column(db.String(5000))
  pat_image = db.Column(db.String(20), nullable=False, default='default.jpg')
  
  def __repr__(self) -> str:
    return f"Patient('{self.id}','{self.pname}', '{self.age}', '{self.phone}', '{self.gender}', '{self.bgroup}', '{self.state}', '{self.address}', '{self.mstatus}', '{self.complaint}', '{self.improvement}', '{self.medicine_suggested}','{self.pat_image}' )"
  
class Doctor(db.Model):
  __tablename__ = 'Doctor'
  id = db.Column(db.Integer, primary_key=True)
  dname = db.Column(db.String(20))
  dphone = db.Column(db.String(20))
  dqual = db.Column(db.String(100))
  profileimage = db.Column(db.String(20), nullable=False, default='default.jpg')

  def __repr__(self) -> str:
    return f"Doctor('{self.id}','{self.dname}', '{self.dphone}', '{self.dqual}', '{self.profileimage}' )"

class Appointments(db.Model):
  __tablename__ = 'Appointments'
  id = db.Column(db.Integer, primary_key=True)
  pname=db.Column(db.String(100))
  examinedby = db.Column(db.String(100))
  complaint = db.Column(db.String(5000))
  medicine_suggested = db.Column(db.String(5000))
  improvements = db.Column(db.String(5000))
  date= db.Column(db.String(50))
  time= db.Column(db.String(50))

  def __repr__(self) -> str:
    return f"Appointments('{self.id}','{self.pname}','{self.examinedby}','{self.complaint}', '{self.medicine_suggested}', '{self.improvements}', '{self.date}', '{self.time}' )"
    
@login_manager.user_loader
def load_user(user_id):
  return Userstore.query.get(int(user_id))

@app.route('/home')
def home():
  pat=db.session.query(Patient).count()
  app=db.session.query(Appointments).count()
  today= datetime.date.today()
  seven_days_ago = datetime.date.today() - timedelta(days = 7)
  allapp = Appointments.query.filter(Appointments.date<=today, Appointments.date >=seven_days_ago).all()
  count=0
  for i in allapp:
    print(i)
    count+=1


  return render_template('home.html', pat=pat, app=app, count=count)
  
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
  if 'username' in session:                # Checking for session login
    return redirect( url_for('home') )

  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']

    usr = Userstore.query.filter_by(username = username).first()
    if usr == None:
      flash('User Not Found', category='error')
      return redirect( url_for('login') )

    elif username == usr.username and password == usr.password:
      session['username'] = username  # saving session for login
      return redirect(url_for('home') )

    else:
      flash('Wrong Credentials. Check Username and Password Again', 'danger')

  return render_template("login.html")

@app.route('/logout')
def logout():
  session.pop('username', None)
  flash('Logged out Successfully','success')
  return redirect( url_for('login') )

@app.route('/editaccount/<id>', methods=['GET', 'POST'])
def editaccount(id):
  if 'username' in session:
    editaccount = Userstore.query.filter_by( id = id ).first()

    if request.method == 'POST':  
      username = request.form['nusername']      
      phone = request.form['nphone']
      password = request.form['npass']

      row_update = Userstore.query.filter_by( id = id ).update(dict(username=username, phone=phone, password=password))
      db.session.commit()

      flash('Account Updated Successfully')
      return render_template('updateaccount.html', editaccount = editaccount)

    return render_template('updateaccount.html', editaccount = editaccount)
  else:
    return redirect(url_for('login'))


@app.route('/newpatient', methods=['GET', 'POST'])
def newpatient():
  if 'username' in session:                
    if request.method == 'POST':           
      pname = request.form['pname']      
      age = request.form['age']
      phone = request.form['phone']
      gender = request.form['gender']
      bgroup = request.form['bgroup']
      state = request.form['state']
      address = request.form['address']
      mstatus = request.form['mstatus']
      complaint = request.form['complaint']
      

      patient= Patient(pname=pname, age=age, phone=phone, gender=gender, bgroup=bgroup, state=state, address=address, mstatus=mstatus, complaint=complaint)

      db.session.add(patient)
      db.session.commit()
      flash('Patient Added Successfully')
      return redirect( url_for('patientrecord') )
      
    return render_template("newpatient.html")
  else:
    flash('You are Logged out. Please login again to continue')
    return redirect( url_for('login') )

  
@app.route('/patientrecord', methods = ['GET','POST'])
def patientrecord():
  if 'username' in session:
    if request.method == 'GET':
      page= request.args.get('page', 1, type=int)
      patrcd= Patient.query.paginate(page=page, per_page=10)
      return render_template("patientrecord.html",patrcd=patrcd)
    
    elif request.method == 'POST':
      pname = request.form['pname']
      
      if pname != "":
        search="%{}%".format(pname)
        patient = Patient.query.filter(Patient.pname.ilike(search))
        if patient == None:
          flash('No Patients with  this Name exists', 'danger')
          return redirect( url_for('patientrecord') )
        else:
          flash('Patient Found','success')
          return render_template('patientrecord.html', patient = patient)
      
      if pname == "":
        flash('Enter Name to Search')
        return redirect( url_for('patientrecord') )
    
    return render_template('patientrecord.html')
  else:
    return redirect( url_for('login') )
  
  return render_template('patientrecord.html')


@app.route('/editpatientdetail/<id>', methods=['GET', 'POST'])
def editpatientdetail(id):
  if 'username' in session:
    editpat = Patient.query.filter_by( id = id )

    if request.method == 'POST':  
      pname = request.form['npname']      
      age = request.form['nage']
      phone = request.form['nphone']
      gender = request.form['ngender']
      bgroup = request.form['nbgroup']
      state = request.form['nstate']
      address = request.form['naddress']
      mstatus = request.form['nmstatus']
      complaint = request.form['ncomplaint']
      improvement=request.form['nimprovement']
      row_update = Patient.query.filter_by( id = id ).update(dict(pname=pname, age=age, phone=phone,gender=gender,bgroup=bgroup, state=state,address=address,mstatus = mstatus,complaint=complaint,improvement=improvement))
      db.session.commit()

      if row_update == None:
        flash('Something Went Wrong')
        return redirect( url_for('patientrecord') )
      else:
        flash('Patient Updated Successfully')
        return redirect( url_for('patientrecord') )

    return render_template('editpatientdetail.html', editpat = editpat)

@app.route('/deletepatientdetail/<id>')
def deletepatientdetail(id):
  if 'username' in session:
    delpat = Patient.query.filter_by(id = id).delete()
    db.session.commit()

    if delpat == None:
      flash('Something Went Wrong')
      return redirect( url_for('patientrecord') )
    else:
      flash('Patient Deleted Successfully')
      return redirect( url_for('patientrecord') )

  return render_template('patientrecord.html')


@app.route('/adddoctor', methods=['POST','GET'])
def adddoctor():
  if 'username' in session:
    if request.method=='POST':
      dname=request.form['dname']
      dphone=request.form['dphone']
      dqual=request.form['dqual']

      doctor=Doctor(dname=dname,dphone=dphone,dqual=dqual)
      db.session.add(doctor)
      db.session.commit()
      flash("Doctor added successfully",'success')
      return redirect(url_for('alldoctor'))
      

  return render_template('adddoctor.html')

@app.route('/alldoctor',methods=['POST','GET'])
def alldoctor():
  if 'username' in session:
    if request.method=='GET':
      alldoctor=Doctor.query.all()
      return render_template('alldoctor.html',alldoctor=alldoctor)

@app.route('/deletedoctor/<id>')
def deletedoctor(id):
  if 'username' in session:
    deldoc = Doctor.query.filter_by(id = id).delete()
    db.session.commit()

    if deldoc == None:
      flash('Something Went Wrong')
      return redirect( url_for('alldoctor') )
    else:
      flash('Doctor deletion initiated successfully')
      return redirect( url_for('alldoctor') )

  return render_template('alldoctor.html')

@app.route('/editdoctor/<id>', methods=['GET', 'POST'])
def editdoctor(id):
  if 'username' in session:
    editdoc = Doctor.query.filter_by( id = id )

    if request.method == 'POST':  
      dname=request.form['ndname']
      dphone=request.form['ndphone']
      dqual=request.form['ndqual']
      row_update = Doctor.query.filter_by( id = id ).update(dict(dname=dname,dphone=dphone,dqual=dqual))
      db.session.commit()

      if row_update == None:
        flash('Something Went Wrong')
        return redirect( url_for('alldoctor') )
      else:
        flash('Doctor updated successfully')
        return redirect( url_for('alldoctor') )

    return render_template('editdoctor.html', editdoc=editdoc)

@app.route('/appointment',methods=['POST','GET'])
def appointment():
  if 'username' in session:
    if request.method=='POST':
      pname = request.form['pname']
      if pname != "":
        search="%{}%".format(pname)
        patient = Patient.query.filter(Patient.pname.ilike(search))
        if patient == "":
          flash('No Patients with  this Name exists', 'danger')
          return redirect( url_for('appointment') )
        else:
          flash('Patient Found','success')
          return render_template('appointment.html', patient = patient)
      
      if pname == "":
        flash('Enter Name to search')
        return redirect( url_for('appointment') )
  return render_template('appointment.html')

@app.route('/addappointment/<id>',methods=['POST','GET'])
def addappointment(id):
  if 'username' in session:
    addapp = Patient.query.filter_by(id=id).first()
    docdetail= Doctor.query.all()
    if request.method=='POST':
      pat=Patient.query.filter_by(id=id).first()
      pname=pat.pname
      examinedby=request.form['examinedby']
      complaint=request.form['complaint']
      improvements=request.form['improvements']
      medicine_suggested=request.form['medicine_suggested']
      date=request.form['date']
      time=request.form['time']

      appointment= Appointments(pname=pname,examinedby=examinedby, complaint=complaint,improvements=improvements, medicine_suggested=medicine_suggested, date=date, time=time)
      db.session.add(appointment)
      db.session.commit()

      row_update = Patient.query.filter_by( id = id ).update(dict(complaint=complaint,improvement=improvements, medicine_suggested=medicine_suggested))
      db.session.commit()

      flash('Appointment added successfully')
      return redirect( url_for('appointment') )

  return render_template('addappointment.html',addapp=addapp, docdetail=docdetail)

@app.route('/viewapp/<id>',methods=['POST','GET'])
def viewapp(id):
  if 'username' in session:
    pat=Patient.query.filter_by(id=id).first()
    pname=pat.pname
    page= request.args.get('page', 1, type=int)
    appointment= Appointments.query.filter_by(pname=pname).order_by(Appointments.date).paginate(page=page, per_page=15)
    if request.method=='GET':
      return render_template('viewapp.html',appointment=appointment, pat=pat)

    return render_template('viewapp.html',appointment=appointment, pat=pat, app=app)

@app.route('/deleteapp/<id>', methods=['POST', 'GET'])
def deleteapp(id):
  if 'username' in session:
    pat=Patient.query.filter_by(id=id).first()
    delpat = Appointments.query.filter_by(id=id).delete()
    db.session.commit()

    if delpat == None:
      flash('Something Went Wrong')
      return redirect(url_for('appointment'))
    else:
      flash('Appointment Deleted Successfully')
      return redirect(url_for('appointment'))

  return render_template('viewapp.html/<id>')

@app.route('/allapp', methods=['POST', 'GET'])
def allapp():
  if 'username' in session:
    today= datetime.date.today()
    seven_days_ago = datetime.date.today() - timedelta(days = 7)
    page= request.args.get('page', 1, type=int)
    allapp = Appointments.query.filter(Appointments.date<=today, Appointments.date >=seven_days_ago).paginate(page=page, per_page=5)
    return render_template('allappointment.html', allapp=allapp)
  
  # return render_template('allappointments.html', allapp=allapp)