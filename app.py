from flask import Flask,render_template,request,redirect, url_for,session
from flask_mysqldb import MySQL




app = Flask(__name__)
app.secret_key = 'supersecretkey'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flaskapp'

mysql = MySQL(app)

@app.route("/index")
def index():
    return render_template('index.html')

@app.route("/admin")
def admin():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM admin")
    fetchdata = cur.fetchall()
    cur.close()
    return render_template('admin.html',data = fetchdata)

@app.route("/",methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM admin WHERE username = %s and password = %s",(username,password))
        user = cur.fetchone()
        if user:
            session['username'] = username
            return redirect(url_for('admin'))


        
    return render_template('login.html')



if __name__== "__main__":
    app.run(debug=True)