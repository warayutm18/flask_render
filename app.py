from flask import Flask,render_template,request,redirect, url_for,session,flash,jsonify
import mysql.connector
import os
import requests
import csv
import pandas as pd
from datetime import datetime, timedelta
import certifi

app = Flask(__name__)
app.secret_key = os.urandom(24)

app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg', 'gif', 'mp3', 'wav'])
mydb = mysql.connector.connect(
    host="bkmrzjuc0txca2pggcfn-mysql.services.clever-cloud.com",
    user="uaxbdpnfmiwngrxc",
    password="wmrvJFQd69gb7FOGZnMy",
    database="bkmrzjuc0txca2pggcfn"
)



@app.route('/logout')
def logout():
    session.pop('user', None)
    response = (redirect(url_for('login')))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

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

@app.route("/m_admin", methods=["GET", "POST"])
def m_admin():
    mycursor = mydb.cursor()
    
    # ตรวจสอบว่ามีการส่งข้อมูลเพื่อเพิ่มแอดมินใหม่หรือไม่
    if request.method == "POST":
        if "add_admin" in request.form:
            admin_username = request.form["admin_username"]
            admin_password = request.form["admin_password"]
            sql = "INSERT INTO admin (username, password) VALUES (%s, %s)"
            val = (admin_username, admin_password)
            mycursor.execute(sql, val)
            mydb.commit()
        elif "edit_admin" in request.form:
            admin_id = request.form["admin_id"]
            admin_username = request.form["admin_username"]
            admin_password = request.form["admin_password"]
            sql = "UPDATE admin SET username = %s, password = %s WHERE id = %s"
            val = (admin_username, admin_password, admin_id)
            mycursor.execute(sql, val)
            mydb.commit()
        elif "delete_admin" in request.form:
            admin_id = request.form["admin_id"]
            sql = "DELETE FROM admin WHERE id = %s"
            mycursor.execute(sql, (admin_id,))
            mydb.commit()
    
    # ดึงข้อมูลแอดมินทั้งหมดจากฐานข้อมูล
    mycursor.execute("SELECT * FROM admin")
    fetchdata = mycursor.fetchall()
    mycursor.close()

    return render_template('m_admin.html', data=fetchdata)

@app.route("/m_student", methods=["GET", "POST"])
def m_student():
    with mydb.cursor() as cursor:
        if request.method == "POST":
            action = request.form.get("action")
            std_id = request.form.get("std_id")
            username = request.form.get("username")
            password = request.form.get("password")
            firstname = request.form.get("firstname")
            lastname = request.form.get("lastname")
            faculty = request.form.get("faculty")
            major = request.form.get("major")

            if action == "add":
                sql = "INSERT INTO students (std_id, username, password, firstname, lastname, faculty, major) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(sql, (std_id, username, password, firstname, lastname, faculty, major))
                mydb.commit()

            elif action == "edit":
                sql = "UPDATE students SET username=%s, password=%s, firstname=%s, lastname=%s, faculty=%s, major=%s WHERE std_id=%s"
                cursor.execute(sql, (username, password, firstname, lastname, faculty, major, std_id))
                mydb.commit()

            elif action == "delete":
                sql = "DELETE FROM students WHERE std_id=%s"
                cursor.execute(sql, (std_id,))
                mydb.commit()

        cursor.execute("SELECT * FROM students")
        students = cursor.fetchall()

    return render_template("m_student.html", students=students)
         





@app.route("/exambank", methods=['POST', 'GET'])
def exambank():
    if request.method == 'POST':
        questions = request.form['question']
        option_a = request.form['option_a']
        option_b = request.form['option_b']
        option_c = request.form['option_c']
        option_d = request.form['option_d']
        difficultys = request.form['difficulty']
        answer = request.form['answer']

        # การจัดการอัปโหลดรูปภาพ
        image_file = request.files['image']
        image_filename = ''
        if image_file:
            image_filename = image_file.filename
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image_file.save(image_path)

        # การจัดการอัปโหลดเสียง
        audio_file = request.files['audio']
        audio_filename = ''
        if audio_file:
            audio_filename = audio_file.filename
            audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_filename)
            audio_file.save(audio_path)

        mycursor = mydb.cursor()
        query = """
        INSERT INTO examQ (question, option_a, option_b, option_c, option_d, difficulty, answer, image_path, audio_path)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (questions, option_a, option_b, option_c, option_d, difficultys, answer, image_filename, audio_filename)

        try:
            mycursor.execute(query, values)
            mydb.commit()
            flash("เพิ่มคำถามสำเร็จ")
            print("บันทึกข้อมูลสำเร็จ")
        except mysql.connector.Error as err:
            print(f"มีข้อผิดพลาด: {err}")

    # ดึงข้อมูลคำถาม
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

@app.route("/updateQ", methods=['POST', 'GET'])
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

        # การจัดการอัปโหลดรูปภาพ
        image_file = request.files['image']
        image_filename = ''
        if image_file:
            image_filename = image_file.filename
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image_file.save(image_path)

        # การจัดการอัปโหลดเสียง
        audio_file = request.files['audio']
        audio_filename = ''
        if audio_file:
            audio_filename = audio_file.filename
            audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_filename)
            audio_file.save(audio_path)

        mycursor = mydb.cursor()
        query = """
        UPDATE examQ
        SET question=%s, option_a=%s, option_b=%s, option_c=%s, option_d=%s, difficulty=%s, answer=%s, image_path=%s, audio_path=%s
        WHERE id=%s
        """
        values = (questions, option_a, option_b, option_c, option_d, difficultys, answer, image_filename, audio_filename, question_id)

        try:
            mycursor.execute(query, values)
            mydb.commit()
            flash("อัปเดตคำถามสำเร็จ")
            print("อัปเดตข้อมูลสำเร็จ")
        except mysql.connector.Error as err:
            print(f"มีข้อผิดพลาด: {err}")

        return redirect(url_for("exambank"))
    
@app.route("/edt_skill")
def edt_skill():
    return render_template("edt_skill.html")    

@app.route("/edt_result")
def edt_result():
    return render_template("edt_result.html")   

@app.route("/engskill")
def engskill():
    return render_template("engskill.html")

@app.route("/eng_data")
def eng_data():
    # ดึงข้อมูลจาก API
    url = 'https://db.snru.ac.th/api-mysql/ept_get_data_all.php'
    #cert_path = r"C:\certificate_flask\New folder\_.snru.ac.th.crt"
    response = requests.get(url, verify=False)

    # ตรวจสอบสถานะการร้องขอ
    if response.status_code == 200:
        data = response.json()  # เปลี่ยนข้อมูลที่ได้เป็น JSON

        def filter_group_data(data, year, group):
            """ฟังก์ชันกรองข้อมูลตามปีและกลุ่ม"""
            return [item for item in data if str(item['student_id']).startswith(str(year)) and item['group_'] == group]

        # สร้างพจนานุกรมเก็บจำนวนข้อมูลของแต่ละกลุ่ม
        group_counts = {}
        years = ['64', '65','66','67']
        groups = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']

        for year in years:
            for group in groups:
                key = f"count{year}_{group}"
                group_counts[key] = len(filter_group_data(data, year, group))
        # สร้างผลรวมของแต่ละกลุ่ม
        group_sums = {}
        target_groups = ['A1', 'A2', 'B1','B2','C1','C2']  # กลุ่มที่ต้องการหาผลรวม

        for group in target_groups:
            group_sums[f'sum_{group}'] = sum(group_counts[f'count{year}_{group}'] for year in years)

        sumall_64 = sum(group_counts[f'count64_{group}'] for group in groups)
        sumall_65 = sum(group_counts[f'count65_{group}'] for group in groups)
        sumall_66 = sum(group_counts[f'count66_{group}'] for group in groups)
        sumall_67 = sum(group_counts[f'count67_{group}'] for group in groups)
        sumall = group_sums['sum_A1']+group_sums['sum_A2']+group_sums['sum_B1']+group_sums['sum_B2']+group_sums['sum_C1']+group_sums['sum_C2']
        return render_template('eng_data.html', data=data, group_counts=group_counts,group_sums = group_sums,sumall_64 = sumall_64,sumall_65= sumall_65,sumall_66 = sumall_66,sumall_67 =sumall_67,sumall = sumall)
    else:
        print('การร้องขอไม่สำเร็จ: ', response.status_code)
        return jsonify({'error': 'ไม่สามารถดึงข้อมูลจาก API ได้'}), 500



@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))

    # เก็บเวลาเริ่มทำข้อสอบใน session
    if 'start_time' not in session:
        session['start_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # ตรวจสอบสถานะการสอบของผู้ใช้
    mycursor = mydb.cursor()
    mycursor.execute("SELECT has_taken_test FROM students WHERE username = %s", (username,))
    has_taken_test = mycursor.fetchone()[0]

    if has_taken_test:
        return redirect(url_for('exam_result'))

    # ตรวจสอบว่ามีการเริ่มทำข้อสอบแล้วหรือยัง ถ้าไม่ให้ไปยังหน้าที่มีปุ่มเริ่มทำข้อสอบ
    if 'start_time' not in session:
        return redirect(url_for('start'))

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

    # เก็บคำตอบที่เลือกไว้ใน session
    if request.method == 'POST':
        for question in paginated_questions:
            question_id = str(question[0])
            selected_answer = request.form.get(f'q_{question_id}')
            if selected_answer:
                # เก็บคำตอบที่เลือกไว้ใน session
                session[f'answer_{question_id}'] = selected_answer

        action = request.form.get('action')

        if action == 'next':
            next_page = page + 1 if end < question_count else None
            if next_page:
                return redirect(url_for('quiz', page=next_page))

        elif action == 'prev':
            prev_page = page - 1 if page > 1 else None
            if prev_page:
                return redirect(url_for('quiz', page=prev_page))

        elif action == 'submit':
            return redirect(url_for('result'))

    # กำหนดระยะเวลา (ตัวอย่าง 10 นาที)
    total_time = timedelta(minutes=2)

    # คำนวณเวลาที่เหลือ
    start_time = datetime.strptime(session['start_time'], '%Y-%m-%d %H:%M:%S')
    elapsed_time = datetime.now() - start_time
    remaining_time = total_time - elapsed_time

    # หากเวลาเกินที่กำหนดให้ย้ายไปยังหน้าผลลัพธ์
    if remaining_time.total_seconds() <= 0:
        return redirect(url_for('result'))

    # คำนวณหน้าถัดไปและหน้าก่อนหน้า
    next_page = page + 1 if end < question_count else None
    prev_page = page - 1 if page > 1 else None

    return render_template(
        'quiz.html',
        q_data=paginated_questions,
        total_questions=question_count,
        current_page=page,
        next_page=next_page,
        prev_page=prev_page,
        remaining_time=remaining_time,
        session=session
    )

@app.route('/start')
def start():
    return render_template('start.html')

@app.route('/result')
def result():
    mycursor = mydb.cursor()

    username = session.get('username')
    if not username:
        return redirect(url_for('login'))

    # ดึงข้อมูลผู้ใช้
    mycursor.execute("SELECT std_id FROM students WHERE username = %s", (username,))
    user_id = mycursor.fetchone()[0]

    # บันทึกสถานะการสอบ
    mycursor.execute("UPDATE students SET has_taken_test = TRUE WHERE std_id = %s", (user_id,))
    mydb.commit()

    # ดึงข้อมูลคำถามทั้งหมด
    mycursor.execute("SELECT * FROM examQ")
    fetchdata = mycursor.fetchall()

    # คำนวณคะแนน
    score = 0
    total_questions = len(fetchdata)

    for question in fetchdata:
        question_id = str(question[0])
        correct_answer = question[7]  # สมมติว่า column ที่ 7 คือคำตอบที่ถูกต้อง
        user_answer = session.get(f'answer_{question_id}')

        if user_answer == correct_answer:
            score += 1

    # ดึงข้อมูลชื่อและนามสกุลของผู้ใช้จากฐานข้อมูล
    username = session['username']
    mycursor.execute("SELECT std_id, firstname, lastname, faculty, major FROM students WHERE username = %s", (username,))
    user_info = mycursor.fetchone()

    if user_info:
        std_id, firstname, lastname, faculty, major = user_info

        # บันทึกคะแนนลงในตารางใหม่ (เช่น exam_results)
        mycursor.execute(
            "INSERT INTO exam_results (std_id, score, exam_date) VALUES (%s, %s, NOW())",
            (std_id, score)
        )
        mydb.commit()
        
    # แสดงผลคะแนน
    return render_template('result.html', score=score, total_questions=total_questions, firstname=firstname, lastname=lastname, faculty=faculty, major=major, std_id=std_id)

@app.route('/exam_result')
def exam_result():
    
    mycursor = mydb.cursor()

    username = session.get('username')
    if not username:
        return redirect(url_for('login'))

    

     # ดึงข้อมูลชื่อและนามสกุลของผู้ใช้จากฐานข้อมูล
    username = session['username']
    mycursor.execute("SELECT std_id, firstname, lastname, faculty, major FROM students WHERE username = %s", (username,))
    user_info = mycursor.fetchone()

    # ดึงข้อมูลคำถามทั้งหมด
    mycursor.execute("SELECT * FROM examQ")
    fetchdata = mycursor.fetchall()

    mycursor.execute("SELECT score FROM exam_results WHERE std_id = %s", (username,))
    score = mycursor.fetchone()[0]
    
    if score >= 10 :
        cefr = 'C2'
        guidelines = '-'
    elif score >= 8:
        cefr = 'C1'
        guidelines = 'นักศึกษาสามารถพัฒนาการใช้ภาษาให้เป็นมาตรฐานได้อย่างสละสลวย ถูกต้องตามจุดประสงค์ที่จะสื่อสารได้ดีสามารถอ่าน บทความที่เป็นภาษาต้นฉบับ (โดยเฉพาะอย่างยิ่งด้านวรรณกรรม) ได้เข้าใจ สามารถ และเลือกใช้ภาษาสำหรับพูดและเขียนได้อย่างเหมาะสม'
    elif score >=6:
        cefr = 'B2'
        guidelines = 'นักศึกษาสามารถศึกษาการใช้ภาษาทางด้านสังคมการทำงาน หรือด้านการศึกษา เพื่อพัฒนาความสามารถด้านการพูดและเขียนข้อความที่ขับซ้อนได้อย่างชัดเจนและถูกต้องตามโครงสร้างไวยากรณ์ พร้อมทั้งสามารถใช้คำเชื่อมประโยคได้อย่างถูกต้อง'
    elif score >=4:
        cefr = 'B1'
        guidelines = 'นักศึกษาสามารถศึกษาการอ่านและทำความเข้าใจบทความที่มีเนื้อหายากขึ้นและฝึกฟังภาษาอังกฤษเป็นประจำจากแหล่งข้อมูลต่าง ๆ เช่นข่าวภาษาอังกฤษ จัดสภาพแวดล้อมที่เอื้อต่อการเรียนรู้และพัฒนาภาษาอังกฤษ เช่น เปลี่ยนจากการฟังเพลงภาษาไทยเป็นเพลงภาษาอังกฤษ'
    elif score >=2:
        cefr = 'A2'
        guidelines = 'นักศึกษาสามารถศึกษาการพูด เขียน และอ่านจับใจความสำคัญของข้อความทั่ว ๆ ไปเพิ่มเติม เช่น การทำงาน โรงเรียน เวลาว่าง ฯลฯ สามารถจัดการกับสถานการณ์ต่าง ๆ ที่เกิดขึ้นระหว่างการเดินทางในประเทศที่ใช้ภาษาได้ ฝึกบรรยายประสบการณ์ความฝัน ความหวัง พร้อมให้เหตุผลสั้นๆได้'
    else:
        cefr = 'A1'
        guidelines = 'นักศึกษาสามารถศึกษาประโยคในชีวิตประจำวันในระดับกลางเพิ่ม เช่น ข้อมูลเกี่ยวกับครอบครัว การจับจ่ายใช้สอย สถานที่ ภูมิศาสตร์ การทำงาน และสามารถสื่อสารในประโยคในการแลกเปลี่ยนข้อมูลทั่วไปและการใช้ชีวิตประจำวันสามารถบรรยายความฝัน ความคาดหวัง ประวัติ สิ่งแวดล้อม และสิ่งอื่นๆ ที่จำเป็นต้องใช้'
    
    total_questions = len(fetchdata)
    if user_info:
        std_id, firstname, lastname, faculty, major = user_info
    return render_template('exam_result.html', score=score, total_questions=total_questions, firstname=firstname, 
                           lastname=lastname, faculty=faculty, major=major, std_id=std_id,guidelines= guidelines,cefr= cefr)

@app.route('/edt_data')
def edt_data():
    # อ่านข้อมูลจากไฟล์ CSV
    df = pd.read_csv('data/data.csv')

    # ดึงข้อมูลจากคอลัมน์ที่ต้องการ เช่น 'ปีการศึกษา', 'คณะ', 'นักศึกษาทั้งหมด'
    column1_data = df['ปีการศึกษา'].tolist()  # แปลงคอลัมน์เป็น list
    column2_data = df['คณะ'].tolist()

    rows = df.iterrows()

    # แปลงข้อมูลแถวเป็นลิสต์ของแถวที่เป็นลิสต์หรือดิกชันนารี
    row_data = [row[1].to_dict() for row in rows]

    # ฟังก์ชันสำหรับคำนวณค่าผลรวม
    def get_totals(df, year, faculty):
        total_students = df[(df['ปีการศึกษา'] == year) & (df['คณะ'] == faculty)]['นักศึกษาทั้งหมด'].sum()
        total_regis = df[(df['ปีการศึกษา'] == year) & (df['คณะ'] == faculty)]['ลงทะเบียน'].sum()
        total_passed = df[(df['ปีการศึกษา'] == year) & (df['คณะ'] == faculty)]['สอบผ่าน'].sum()
        return total_students, total_regis, total_passed

    # คำนวณค่าผลรวมสำหรับแต่ละคณะในปี 2565 และ 2566
    faculties = ['วิทยาศาสตร์และเทคโนโลยี', 'ครุศาสตร์', 'วิทยาการจัดการ', 'เทคโนโลยีการเกษตร', 'เทคโนโลยีอุตสาหกรรม']
    faculty_totals = {faculty: {'2565': get_totals(df, 2565, faculty), '2566': get_totals(df, 2566, faculty)} for faculty in faculties}

    

    # ส่งข้อมูลไปยังหน้า HTML
    return render_template('edt_data.html', 
                           column1=column1_data,
                           column2=column2_data, 
                           rows=row_data, 
                           faculty_totals=faculty_totals)

    

if __name__== "__main__":
    app.run()