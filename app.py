from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import psycopg2
import bcrypt  # For secure password storage
import hashlib
from functools import wraps

app = Flask(__name__)
app.secret_key = 'hvjgi'  # Add this line


def create_database_connection():
    return psycopg2.connect(os.environ.get('DATABASE_URL'))


# Leena: RBAC Decorator Definition
def requires_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Check if user is logged in
            if 'username' not in session:
                flash('Please log in to access this page.', 'danger')
                return redirect(url_for('secure_login'))

            # Check if user has the correct role
            if session.get('role') not in roles:
                flash('Access denied: You do not have permission to view this page.', 'danger')
                return redirect(url_for('dashboard'))

            return f(*args, **kwargs)

        return wrapped

    return wrapper



@app.route('/')  # ايمان: مهمتها تعلم السيرفر ايش الفنكشن اللي يشغلها في حال رابطنا ملحق ب '/' انفتح
def home():
    return render_template('home.html')  # تحمل الملف المراد على براوزر اليوزر


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        md5hash_password = hashlib.md5(
            password.encode()).hexdigest()  # هذا التشفير الضعيف MD5 first convert password text into byte by encode() then feed it into hash algo then convert the output into hexadicimal

        # ايمان: الاتصال بالداتابيس
        db_con = create_database_connection()
        cur = db_con.cursor()

        sql = f"SELECT * FROM \"USER\" WHERE username = '{username}' AND password = '{md5hash_password}'"
        cur.execute(sql)
        user = cur.fetchone()

        # نسكر الاتصال بالداتابيس
        cur.close()
        db_con.close()

        if user:
            flash('Welcome back!',
                  'success')  # رسالة المفروض تظهر لليوزر في البراوزر لكن اعتقد لازم يكون في كود اضافي في ملف اتش  تي ام ال
            return redirect(url_for('dashboard'))  # if user exist move to url in func dashboard()
        else:
            flash('Invalid username or password!', 'danger')
            return render_template(
                'login.html')  # اذا اليوزر نل معناه يا الباسورد او اليوزرنيم خطا لذلك اجلس على نفس صفحة ريجستريشن

    return render_template('login.html')


# ايمان :تعبت من كتابة الكومنتات لباقي الكود، بكمل بكرة
# معليش بعض الكومنتات بالعربي وبعضها بالانجليزي حسب اللي الاسهل علي
@app.route('/secure_login', methods=['POST', 'GET'])
def secure_login():
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]

        # Modified to fetch the role as well , Leena
        sql = "SELECT password, role FROM \"USER\" WHERE username= %s"

        db_con = create_database_connection()
        cur = db_con.cursor()
        cur.execute(sql, (username,))
        user_data = cur.fetchone()

        cur.close()
        db_con.close()

        # user_data[0] is password, user_data[1] is role
        if user_data and bcrypt.checkpw(password.encode('utf-8'), user_data[0].encode('utf-8')):
            # Set the session variables upon successful login
            session['username'] = username
            session['role'] = user_data[1]
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'danger')
            return render_template('secure_login.html')

    return render_template('secure_login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        md5hash_password = hashlib.md5(password.encode()).hexdigest()

        db_con = create_database_connection()
        cur = db_con.cursor()

        sql_query = f"INSERT INTO \"USER\" (username, password) VALUES ('{username}', '{md5hash_password}')"

        try:
            cur.execute(sql_query)
            db_con.commit()

        except Exception as e:
            flash(f"Registeration faied: {e}", 'danger')
            return render_template('register.html')

        finally:
            cur.close()
            db_con.close()

        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/secure_register', methods=['GET', 'POST'])
def secure_register():
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Modified to insert a default 'user' role , Leena
        sql = "INSERT INTO \"USER\" (username,password, role) VALUES  (%s,%s,%s)"
        info = (username, hashed_password, 'user')

        db_con = create_database_connection()
        cur = db_con.cursor()
        try:
            cur.execute(sql, info)
            db_con.commit()
            return redirect(url_for('secure_login'))
        except Exception as e:
            flash(f'Registration failed!\nerror:{e}', 'danger')
            return render_template('secure_register.html')
        finally:
            cur.close()
            db_con.close()

    return render_template('secure_register.html')


@app.route('/admin')
def admin():
    return render_template('admin.html')


@app.route('/secure_admin')
@requires_roles('admin')  # Protect this route for admins only, Leena
def secure_admin():
    return render_template('secure_admin.html')


@app.route('/dashboard')
@requires_roles('admin', 'user')  # Require login to see the dashboard , Leena
def dashboard():
    return render_template('dashboard.html')


# Added a logout route to help you test different users easily, Leena
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

#Shahad's edits
@app.route('/add_comment', methods=['POST'])
def add_comment():
    content = request.form['content']
    
    # hardcode the user_id as 1 just to make the comment work
    user_id = 1 
    
    db_con = create_database_connection()
    cur = db_con.cursor()
    
    # Insert the comment into the COMMENT table
    sql = "INSERT INTO comment (content, user_id) VALUES (%s, %s)"
    cur.execute(sql, (content, user_id))
    db_con.commit()
    
    cur.close()
    db_con.close()
    
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.run(debug=True)
