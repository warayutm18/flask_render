from flask import Flask,render_template,request,redirect, url_for,session





app = Flask(__name__)

@app.route("/admin")
def admin():
    return render_template('admin.html')

@app.route("/",methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == "warayut" and password == "1234":
            return redirect(url_for('admin'))


        
    return render_template('login.html')



if __name__== "__main__":
    app.run(debug=True)