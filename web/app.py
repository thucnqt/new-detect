from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort
import os
from flaskext.mysql import MySQL
import mysql.connector
from mysql.connector import Error
import json
 

app = Flask(__name__)
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'anhthuc1996'
app.config['MYSQL_DATABASE_DB'] = 'object_detection'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template("login2.html")
    else:
        return display()
 
@app.route('/login', methods=['POST'])
def do_admin_login():
    if request.form['password'] == 'admin' and request.form['username'] == 'admin':
        return display()
    else:
        flash('wrong password!')
        return home()
@app.route('/login', methods= ['GET'])     
def display():
    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute("SELECT * from detect")
    rv = cur.fetchall()
    conn.close()
    return render_template('data.html', data = rv)
if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True,host='0.0.0.0', port=5000)
