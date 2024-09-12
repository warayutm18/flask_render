from flask import Flask,render_template,request,redirect, url_for,session,flash,jsonify
import mysql.connector
import os
import requests


app = Flask(__name__)
app.secret_key = os.urandom(24)

app.config['UPLOAD_FOLDER'] = 'static/uploads'
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

        # การจัดการรูปภาพ
        image_file = request.files['image']
        image_filename = ''
        if image_file:
            image_filename = image_file.filename
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image_file.save(image_path)  # บันทึกรูปภาพลงโฟลเดอร์

        mycursor = mydb.cursor()
        query = "INSERT INTO examQ (question,option_a,option_b,option_c,option_d,difficulty,answer,image_path) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
        values = (questions,option_a,option_b,option_c,option_d,difficultys,answer,image_filename)
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

    mycursor.execute("SELECT COUNT(*) FROM examQ")
    question_count = mycursor.fetchone()[0]
    return render_template('m_exam.html', q_data=fetchdata, total_questions=question_count)

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

@app.route("/updateQ", methods = ['POST','GET'])
def updateQ():
    if request.method == 'POST':
        question_id = request.form['id']
        questions = request.form['question']
        option_a = request.form['option_a']
        option_b = request.form['option_b']
        option_c = request.form['option_c']
        option_d = request.form['option_d']
        difficultys = request.form['difficulty']
        answer = request.form['answer']
        # การจัดการรูปภาพ
        image_file = request.files['image']
        image_filename = ''
        if image_file:
            image_filename = image_file.filename
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image_file.save(image_path)  # บันทึกรูปภาพลงโฟลเดอร์

        mycursor = mydb.cursor()
        query = """
        UPDATE examQ 
        SET question=%s, option_a=%s, option_b=%s, option_c=%s, option_d=%s, difficulty=%s, answer=%s, image_path=%s 
        WHERE id=%s
        """
        values = (questions, option_a, option_b, option_c, option_d, difficultys, answer, image_filename, question_id)
        
        try:
            mycursor.execute(query, values)
            mydb.commit()
            flash("Update questions successfully")
            print("Data updated successfully.")
        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))    
    
        return redirect(url_for("exambank"))


@app.route("/engskill")
def engskill():
    return render_template("engskill.html")

@app.route("/eng_data")
def eng_data():
    # ดึงข้อมูลจาก API
    api_url = "https://db.snru.ac.th/api-mysql/ept_get_data_all.php"
    response = requests.get(api_url,verify=False)
    
    # ตรวจสอบสถานะการร้องขอ
    if response.status_code == 200:
        data = response.json()  # เปลี่ยนข้อมูลที่ได้เป็น JSON
        return render_template('eng_data.html', data = data) 
    else:
        print('การร้องขอไม่สำเร็จ: ', response.status_code)
        return jsonify({'error': 'ไม่สามารถดึงข้อมูลจาก API ได้'}), 500


@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    # กำหนดจำนวนคำถามที่จะแสดงต่อหน้า
    questions_per_page = 5
    
    # รับค่า page จาก query string ถ้าไม่มีให้เริ่มที่หน้า 1
    page = int(request.args.get('page', 1))

    # คำนวณค่าการเริ่มต้นและสิ้นสุดในการดึงคำถาม
    start = (page - 1) * questions_per_page
    end = start + questions_per_page

    mycursor = mydb.cursor()
    
    # ดึงข้อมูลคำถามทั้งหมด
    mycursor.execute("SELECT * FROM examQ")
    fetchdata = mycursor.fetchall()

    # ดึงจำนวนคำถามทั้งหมด
    mycursor.execute("SELECT COUNT(*) FROM examQ")
    question_count = mycursor.fetchone()[0]

    # ดึงเฉพาะคำถามในหน้าปัจจุบัน
    paginated_questions = fetchdata[start:end]

    # คำนวณหน้าถัดไปและหน้าก่อนหน้า
    next_page = page + 1 if end < question_count else None
    prev_page = page - 1 if page > 1 else None

    return render_template(
        'quiz.html',
        q_data=paginated_questions,
        total_questions=question_count,
        current_page=page,
        next_page=next_page,
        prev_page=prev_page
    )

    
if __name__== "__main__":
    app.run(debug=True)