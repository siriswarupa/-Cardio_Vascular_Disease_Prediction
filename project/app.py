from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import joblib
import numpy as np
import pandas as pd
app = Flask(__name__,static_url_path='/static')
app.secret_key = 'xyzsdfg'
  
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'user-system'

mysql = MySQL(app)
model = joblib.load(open('ensemble.pkl', 'rb'))
@app.route('/')
def index():
    return render_template("index.html")
@app.route('/about')
def about():
    return render_template("about.html")
@app.route('/heartinfo')
def heartinfo():
    return render_template("heartinfo.html")
@app.route('/modelsummary')
def modelsummary():
    return render_template("modelsummary.html")
@app.route('/index')
def home():
    return render_template("index.html")
@app.route('/help')
def help():
    return render_template("help.html")
@app.route('/bmi')
def bmi():
    return render_template("bmi.html")
@app.route('/map')
def map():
    return render_template("map.html")
@app.route('/heart')
def heart():
    return render_template("heart.html")
@app.route('/login', methods =['GET', 'POST'])
def login():
    mesage = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = % s AND password = % s', (email, password, ))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['userid'] = user['userid']
            session['name'] = user['name']
            session['email'] = user['email']
            mesage = 'Logged in successfully !'
            return render_template('heart.html', mesage = mesage)
        else:
            mesage = 'Please enter correct email / password !'
    return render_template('login.html', mesage = mesage)
  
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    return redirect(url_for('login'))
  
@app.route('/register', methods =['GET', 'POST'])
def register():
    mesage = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form :
        userName = request.form['name']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = % s', (email, ))
        account = cursor.fetchone()
        if account:
            mesage = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            mesage = 'Invalid email address !'
        elif not userName or not password or not email:
            mesage = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO user VALUES (NULL, % s, % s, % s)', (userName, email, password, ))
            mysql.connection.commit()
            mesage = 'You have successfully registered !'
    elif request.method == 'POST':
        mesage = 'Please fill out the form !'
    return render_template('register.html', mesage = mesage)
@app.route('/calculate_bmi', methods=['POST'])
def calculate_bmi():
    # Get user inputs from the form
    weight = float(request.form['weight'])
    height = float(request.form['height'])

    # Calculate BMI
    bmi = weight / ((height / 100) ** 2)
    bmi = round(bmi, 1)


    # Return the calculated BMI
    return render_template('bmi.html', bmi=bmi)
@app.route('/calculate_map', methods=['POST'])
def calculate_map():
    # Get user inputs from form
    SystolicPressure = float(request.form['SystolicPressure'])
    DiastolicPressure = float(request.form['DiastolicPressure'])

    # Calculate MAP
    map_value = (DiastolicPressure + 2 * SystolicPressure) / 3
    map_value=round( map_value,1)
    
    return render_template('map.html', map_value=map_value)

@app.route('/predictheart', methods=['POST'])
def predictheart():
    input_features = [float(x) for x in request.form.values()]
    features_value = [np.array(input_features)]

    features_name = ['clusters','cholesterol','gluc','age_group','bmi','map']

    df = pd.DataFrame(features_value, columns=features_name)
    output = model.predict(df)

    if output == 1:
        res_val = "a high risk of Heart Disease"
    else:
        res_val = "a low risk of Heart Disease"

    return render_template('heart_result.html', prediction_text='Patient has {}'.format(res_val))
if __name__ == "__main__":
    app.run(port=5002)