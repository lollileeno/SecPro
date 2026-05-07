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
# Leena: RBAC Decorator Definition
def requires_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Check if user is logged in
            if 'username' not in session:
                flash('Please log in to access this page.', 'danger')
                return redirect(url_for('home'))

            # Check if user has the correct role
            if session.get('role') not in roles:
                flash('Access denied: You do not have permission to view this page.', 'danger')
                # Bounces the user back to the page they just came from (or dashboard as a backup)
                return redirect(request.referrer or url_for('dashboard'))

            return f(*args, **kwargs)

        return wrapped

    return wrapper


@app.route('/')  # ايمان: مهمتها تعلم السيرفر ايش الفنكشن اللي يشغلها في حال رابطنا ملحق ب '/' انفتح
def home():
    return render_template('home.html')  # تحمل الملف المراد على براوزر اليوزر


@app.route('/login', methods=['GET', 'POST']) #the updated func!
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        md5hash_password = hashlib.md5(password.encode()).hexdigest()

        db_con = create_database_connection()
        cur = db_con.cursor()

        # Vulnerable to SQL Injection + Fetching role
        sql = f"SELECT username, role FROM \"USER\" WHERE username = '{username}' AND password = '{md5hash_password}'"
        cur.execute(sql)
        user = cur.fetchone()

        cur.close()
        db_con.close()

        if user:
            # Hand the user their session data so the dashboard works
            session['username'] = user[0]
            session['role'] = user[1] 
            session['is_secure'] = False
            
            flash('Welcome back!', 'success')
            return redirect(url_for('dashboard')) 
        else:
            flash('Invalid username or password!', 'danger')
            return render_template('login.html') 

    return render_template('login.html')


# ايمان :تعبت من كتابة الكومنتات لباقي الكود، بكمل بكرة
# معليش بعض الكومنتات بالعربي وبعضها بالانجليزي حسب اللي الاسهل علي
@app.route('/secure_login', methods=['POST', 'GET'])
def secure_login():
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]

        # Secure query (Parameterized) to fetch password and role, Leena
        sql = "SELECT password, role FROM \"USER\" WHERE username= %s"

        db_con = create_database_connection()
        cur = db_con.cursor()
        cur.execute(sql, (username,))
        user_data = cur.fetchone()

        cur.close()
        db_con.close()

        # user_data[0] is password, user_data[1] is role
        try:
            if user_data and bcrypt.checkpw(password.encode('utf-8'), user_data[0].encode('utf-8')):
                # Set the session variables upon successful login
                session['username'] = username
                session['role'] = user_data[1]
                session['is_secure'] = True
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password!', 'danger')
                return render_template('secure_login.html')
        except ValueError:
            # Prevent crash if MD5 hash is checked by Bcrypt
            flash('Invalid username or password! (Hash mismatch)', 'danger')
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

        # Vulnerable SQL Injection + default 'user' role
        sql_query = f"INSERT INTO \"USER\" (username, password) VALUES ('{username}', '{md5hash_password}')"

        try:
            cur.execute(sql_query)
            db_con.commit()
            flash('Account created successfully!', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            print(e)
            flash(f"Registeration failed: {e}", 'danger')
            return render_template('register.html')
        finally:
            cur.close()
            db_con.close()

    return render_template('register.html')


@app.route('/secure_register', methods=['GET', 'POST'])
def secure_register():
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Parameterized Query + default 'user' role, Leena
        sql = "INSERT INTO \"USER\" (username, password, role) VALUES (%s, %s, %s)"
        info = (username, hashed_password, 'user')

        db_con = create_database_connection()
        cur = db_con.cursor()
        try:
            cur.execute(sql, info)
            db_con.commit()
            flash('Account created securely!', 'success')
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
    # Vulnerable route: No access control here!
    return render_template('admin.html')


@app.route('/secure_admin')
@requires_roles('admin')  # Protect this route for admins only, Leena
def secure_admin():
    return render_template('secure_admin.html')


# Added a logout route to help you test different users easily, Leena
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))


#Shahad's edits
@app.route('/dashboard')
@requires_roles('admin', 'user')  # Keep Leena's protection!
def dashboard():
    try:
        db_con = create_database_connection()
        cur = db_con.cursor()
        
        cur.execute('SELECT content FROM "COMMENT"')
        comments = cur.fetchall()
        
        cur.close()
        db_con.close()
        
        # Pass the username, role, and security flag so the HTML works
        return render_template('dashboard.html', 
                               user=session.get('username'), 
                               role=session.get('role'),
                               comments=comments
                               is_secure=session.get('is_secure') 
                              )
        
    except Exception as e:
        return f"<h1>Dashboard Crash Report:</h1><p>{e}</p>"


@app.route('/add_comment', methods=['POST'])
@requires_roles('admin', 'user') # Protect this route!
def add_comment():
    try:
        content = request.form['content']
        username = session.get('username')
        
        db_con = create_database_connection()
        cur = db_con.cursor()
        
        # Fetch the actual user_id of the logged-in user
        cur.execute("SELECT user_id FROM \"USER\" WHERE username = %s", (username,))
        user_data = cur.fetchone()
        
        if user_data:
            user_id = user_data[0]
            
            # Insert the comment with the correct user_id
            sql = 'INSERT INTO "COMMENT" (content, user_id) VALUES (%s, %s)'
            cur.execute(sql, (content, user_id))
            db_con.commit()
        
        cur.close()
        db_con.close()
        
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        return f"<h1>Add Comment Crash Report:</h1><p>{e}</p>"
        
if __name__ == '__main__':
    app.run(debug=True)
