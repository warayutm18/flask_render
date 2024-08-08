from flask import Flask,render_template,request,redirect, url_for,session,flash
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

@app.route("/index")
def index():
    return render_template ("index.html")

@app.route("/admin")
def admin():
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM admin")
    fetchdata = mycursor.fetchall()
    mycursor.close()

    return render_template('admin.html',data = fetchdata)

@app.route("/exambank",methods=['POST','GET'])
def exambank():
    if request.method == 'POST':
        questions = request.form['question']
        option_a = request.form['option_a']
        option_b = request.form['option_b']
        option_c = request.form['option_c']
        option_d = request.form['option_d']
        difficultys = request.form['difficulty']
        answer = request.form['answer']
        mycursor = mydb.cursor()
        query = "INSERT INTO examQ (question,option_a,option_b,option_c,option_d,difficulty,answer) VALUES (%s,%s,%s,%s,%s,%s,%s)"
        values = (questions,option_a,option_b,option_c,option_d,difficultys,answer)
        try:
            mycursor.execute(query, values)
            mydb.commit()
            flash("Add questions successfully")
            print("Data inserted successfully.")
        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))
        
       
    
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM examQ")
    fetchdata = mycursor.fetchall()
    return render_template('m_exam.html', q_data=fetchdata)

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
        else:
            mycursor.execute("SELECT * FROM students WHERE username = %s and password = %s",(username,password))
            user2 = mycursor.fetchone()
            if user2:
                session['username'] = username
                return redirect(url_for('index'))
    return render_template('login.html')

@app.route("/deleteQ/<int:id_data>", methods = ['GET'])
def deleteQ(id_data):
    if request.method == 'GET':
        mycursor = mydb.cursor()
        query = "DELETE FROM examQ WHERE id=%s"
        try:
            mycursor.execute(query, (id_data,))
            mydb.commit()
            print("Data inserted successfully.")
        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))
    
    return redirect(url_for("exambank"))

@app.route("/engskill")
def engskill():
    return render_template("engskill.html")


@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM examQ")
    fetchdata = mycursor.fetchall()
    return render_template('quiz.html', q_data=fetchdata)

    
if __name__== "__main__":
    app.run(debug=True)