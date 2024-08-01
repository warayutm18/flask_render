from flask import Flask,render_template,request,redirect, url_for,session
import mysql.connector
import os





app = Flask(__name__)
app.secret_key = os.urandom(24)

mydb = mysql.connector.connect(
    host="bkmrzjuc0txca2pggcfn-mysql.services.clever-cloud.com",
    user="uaxbdpnfmiwngrxc",
    password="wmrvJFQd69gb7FOGZnMy",
    database="bkmrzjuc0txca2pggcfn"
)

@app.route("/admin")
def admin():
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM admin")
    fetchdata = mycursor.fetchall()
    mycursor.close()

    return render_template('admin.html',data = fetchdata)

@app.route("/",methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM admin WHERE username = %s and password = %s",(username,password))
        user = mycursor.fetchone()

        if user:
            session['username'] = username
            return redirect(url_for('admin'))


        
    return render_template('login.html')



if __name__== "__main__":
    app.run()