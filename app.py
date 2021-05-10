from flask import Flask, render_template,request,redirect, url_for,session,flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import numpy as np
import pandas as pd

app = Flask(__name__)
app.secret_key = 'wdjrfbhibjksdsdzcx'
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] =False
app.permanent_session_lifetime = timedelta(hours=1)

db = SQLAlchemy(app)

class User(db.Model,UserMixin):
    _id = db.Column('id',db.Integer,primary_key=True)
    username = db.Column('username',db.String(200))
    password = db.Column('password',db.String(200))

    def __init__(self,username,password):
        self.username = username
        self.password = password


@app.route("/",methods = ['POST','GET'])
def home():
    if request.method == 'POST':
        return redirect(url_for('login'))
    else:
        return render_template('home.html')

@app.route("/login",methods = ['POST','GET'])
def login():
    if request.method == 'POST':
        session.permanent = True
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        passed = User.query.filter_by(username=password).first()
        
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in')
            else:
                flash('Tncorrect password')
        else:
            flash('Username does not exist')

        session['username'] = username
        session['password'] = password
        return redirect(url_for('cfp'))
    else:
        if ('username' in session) and ('password' in session):
            return redirect(url_for('cfp'))
        return render_template('login.html')

@app.route("/register",methods=['POST','GET'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password1= request.form.get('password1')
        password2 = request.form.get('password2')
        user = User.query.filter_by(username=username).first()
        print(password1)
        print(password2)
        if user:
            flash('User already exists')
        elif password1 != password2:
            flash('Password don\'t match')
        elif(username == None)or( password1 == None)or (password2==None):
            flash('Password cannot be empty')
        else:
            new_user = User(username=username, password = generate_password_hash(password1, method = 'sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash('Account created', category='success')
            return redirect(url_for('cfp'))

    return render_template('register.html')

@app.route('/cfp',methods=['POST','GET'])
def cfp():
    if ('username' in session) and ('password' in session):
        if request.method == 'POST':
            elec = request.form.get('elec')
            km = request.form.get('km')
            oil =request.form.get('oil')
            natgas = request.form.get('natgas')

            elec_emission_factor = 201  #this is in t Co2e/Gwh
            heating_oil_emission_factor = 10.18409 #this is in kg Co2e per gallon of heating oil
            heating_natural_gas_emission_factor = 54.49555 #this is in g Co2e per scf of natural gas
            car_emissions_factor = 404


            elec_emissions = (elec_emission_factor * 1016.04691) * (int(elec) / 1000000) #includes unit conversions to end up with kg co2e
            heating_emissions = (heating_oil_emission_factor*int(oil)) + ((heating_natural_gas_emission_factor*int(natgas)*35.3146667)/1000) #includes unit conversions to end up with kg co2e
            car_emissions = (car_emissions_factor*int(km)*0.62137119)/1000 #includes unit conversions to end up with kg co2e

            ee = str(round(elec_emissions))
            he = str(round(heating_emissions))#in grams per mile 
            ce = str(round(car_emissions)) 
            flash('Scroll down',category='size')  
            return render_template('cfp.html', ee = ee, he=he,ce = ce)
        else:
            return render_template('cfp.html')
    else:
        flash('Login First','error')
        return redirect(url_for('login'))



@app.route('/logout')
def logout():
    session.pop('username',None)    
    session.pop('password',None)
    flash('You have been logged out','info')
    return redirect(url_for('login'))

if __name__ == "__main__":
    db.create_all()
    app.run(debug = False)
