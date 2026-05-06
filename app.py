from flask import Flask, render_template, request, redirect, url_for, flash
import os
import psycopg2
import bcrypt # For secure password storage
import hashlib

app = Flask(__name__)
app.secret_key = 'hvjgi' # Add this line

def create_database_connection():
    return psycopg2.connect(os.environ.get('DATABASE_URL'))

@app.route('/') # ايمان: مهمتها تعلم السيرفر ايش الفنكشن اللي يشغلها في حال رابطنا ملحق ب '/' انفتح
def home():
    return render_template('home.html') # تحمل الملف المراد على براوزر اليوزر

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        md5hash_password= hashlib.md5(password.encode()).hexdigest() #هذا التشفير الضعيف MD5 first convert password text into byte by encode() then feed it into hash algo then convert the output into hexadicimal

        #ايمان: الاتصال بالداتابيس  
        db_con = create_database_connection()
        cur = db_con.cursor()
        
        sql = f"SELECT * FROM \"USER\" WHERE username = '{username}' AND password = '{md5hash_password}'"
        cur.execute(sql)
        user = cur.fetchone() 
        
        #نسكر الاتصال بالداتابيس
        cur.close()
        db_con.close()

        if user:  
            flash('Welcome back!', 'success') #  رسالة المفروض تظهر لليوزر في البراوزر لكن اعتقد لازم يكون في كود اضافي في ملف اتش  تي ام ال
            return redirect(url_for('dashboard')) # if user exist move to url in func dashboard()
        else:
            flash('Invalid username or password!', 'danger')
            return render_template('login.html') #اذا اليوزر نل معناه يا الباسورد او اليوزرنيم خطا لذلك اجلس على نفس صفحة ريجستريشن

    return render_template('login.html')

#ايمان :تعبت من كتابة الكومنتات لباقي الكود، بكمل بكرة
#معليش بعض الكومنتات بالعربي وبعضها بالانجليزي حسب اللي الاسهل علي
@app.route('/secure_login',methods=['POST','GET'])
def secure_login():
    if request.method=='POST':
        username=request.form["username"]
        password=request.form["password"]    

        sql="SELECT password FROM \"USER\" WHERE username= %s"
        #info=(username,hashed_password)

        db_con=create_database_connection()
        cur=db_con.cursor()
        cur.execute(sql,(username,))
        hash_password_db=cur.fetchone()

        cur.close()
        db_con.close()

        if hash_password_db and bcrypt.checkpw(password.encode('utf-8'), hash_password_db[0].encode('utf-8')):
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!','danger')
            return render_template('secure_login.html')
    
    return render_template('secure_login.html')

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        md5hash_password= hashlib.md5(password.encode()).hexdigest()

        db_con=create_database_connection()
        cur=db_con.cursor()

        sql_query = f"INSERT INTO \"USER\" (username, password) VALUES ('{username}', '{md5hash_password}')"

        try:
            cur.execute(sql_query)
            db_con.commit()

        except Exception as e:
            flash(f"Registeration faied: {e}",'danger')
            return render_template('register.html')
        
        finally:
            cur.close()
            db_con.close()

        flash('Account created successfully!','success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/secure_register',methods=['GET','POST'])
def secure_register():
    if request.method=='POST':
        username=request.form["username"]
        password=request.form["password"]   
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        sql="INSERT INTO \"USER\" (username,password) VALUES  (%s,%s)"
        info=(username,hashed_password)

        db_con=create_database_connection()
        cur=db_con.cursor()
        try:
            cur.execute(sql,info)
            db_con.commit()
            return redirect(url_for('secure_login'))
        except Exception as e:
            flash(f'Registration failed!\nerror:{e}','danger')
            return render_template('secure_register.html')
        finally:
            cur.close()
            db_con.close()

    return render_template('secure_register.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/secure_admin')
def secure_admin():
    return render_template('secure_admin.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')




if __name__ == '__main__':
    app.run(debug=True)