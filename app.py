from flask import Flask, render_template, request, redirect, url_for, flash, session , make_response
import os
import psycopg2
import bcrypt  # For secure password storage
import hashlib
from functools import wraps
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv() # Load environment variables from .env file

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

# 1. Secure Session Cookies
app.config['SESSION_COOKIE_SECURE'] = True    # Ensures the session cookie is ONLY sent over HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevents JavaScript from reading the token (Mitigates XSS)
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax' # Prevents the token from being sent in cross-site requests (Mitigates CSRF)


# 2. HTTPS/TLS was enabled through the hosting provider to encrypt communication between the client and server since site URL begins with: "https://" then TLS is already active. 

# 3. ProxyFix is used to ensure that Flask correctly identifies the original request's protocol and host when behind a reverse proxy (like Gunicorn or Nginx), which is essential for enforcing HTTPS and generating correct URLs.
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

def create_database_connection():
    return psycopg2.connect(os.environ.get('DATABASE_URL'))

# 4. Enforce HTTPS for all routes
@app.before_request
def enforce_https():
    # Redirect HTTP requests to HTTPS
    if not request.is_secure:
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)
    
# Leena: RBAC Decorator Definition
def requires_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if 'username' not in session:
                flash('Please log in to access this page.', 'danger')
                return redirect(url_for('home'))

            if session.get('role') not in roles:
                # This triggers the message
                flash(f'Access denied: {", ".join(roles)} permissions required.', 'danger')
                # Redirect to dashboard so the user can see the popup
                return redirect(url_for('dashboard'))

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

                session.clear() #prevents session fixation attacks

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
@requires_roles('admin')
def secure_admin():
    db_con = create_database_connection()
    cur = db_con.cursor()
    # Fetching ID and Content so we know which one to delete
    cur.execute('SELECT comment_id, content FROM "COMMENT"')
    comments = cur.fetchall()
    cur.close()
    db_con.close()
    return render_template('secure_admin.html', comments=comments)

@app.route('/delete_comment/<int:comment_id>', methods=['POST'])
@requires_roles('admin')
def delete_comment(comment_id):
    db_con = create_database_connection()
    cur = db_con.cursor()
    try:
        # Parameterized query to prevent SQL injection
        cur.execute('DELETE FROM "COMMENT" WHERE comment_id = %s', (comment_id,))
        db_con.commit()
        flash('Comment deleted successfully.', 'success')
    except Exception as e:
        flash(f'Error deleting comment: {e}', 'danger')
    finally:
        cur.close()
        db_con.close()
    return redirect(url_for('secure_admin'))

@app.route('/edit_comment/<int:comment_id>', methods=['POST'])
@requires_roles('admin')
def edit_comment(comment_id):
    new_content = request.form.get('content')
    db_con = create_database_connection()
    cur = db_con.cursor()
    try:
        cur.execute('UPDATE "COMMENT" SET content = %s WHERE comment_id = %s', (new_content, comment_id))
        db_con.commit()
        flash('Comment updated successfully.', 'success')
    except Exception as e:
        flash(f'Error updating comment: {e}', 'danger')
    finally:
        cur.close()
        db_con.close()
    return redirect(url_for('secure_admin'))
# Added a logout route to help you test different users easily, Leena
@app.route('/logout')
def logout():
    session.clear()
  
    response = make_response(redirect(url_for('home')))
    
    # 3. Explicitly tell the browser to delete the session cookie
    # This 'closes' the session at the browser level
    response.set_cookie('session', '', expires=0)
    
    flash('You have been logged out and your session cookie destroyed.', 'success')
    return response


#Shahad's edits
@app.route('/dashboard')
@requires_roles('admin', 'user')
def dashboard():
    try:
        db_con = create_database_connection()
        cur = db_con.cursor()
        
        # JOIN the COMMENT table with the USER table to get the author's name
        cur.execute('''
            SELECT c.content, u.username, c.is_secure, c.timestamp
            FROM "COMMENT" c 
            JOIN "USER" u ON c.user_id = u.user_id
            ORDER BY c.timestamp
        ''')
        comments = cur.fetchall()
        
        cur.close()
        db_con.close()
        
        return render_template('dashboard.html', 
                               user=session.get('username'), 
                               role=session.get('role'),
                               comments=comments,
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
        secure= session.get('is_secure')
        
        db_con = create_database_connection()
        cur = db_con.cursor()
        
        # Fetch the actual user_id of the logged-in user
        cur.execute("SELECT user_id FROM \"USER\" WHERE username = %s", (username,))
        user_data = cur.fetchone()
        
        if user_data:
            user_id = user_data[0]
            
            # Insert the comment with the correct user_id
            sql = 'INSERT INTO "COMMENT" (content, user_id, is_secure, timestamp) VALUES (%s, %s, %s, CURRENT_TIMESTAMP)'
            cur.execute(sql, (content, user_id, secure))
            db_con.commit()
        
        cur.close()
        db_con.close()
        
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        return f"<h1>Add Comment Crash Report:</h1><p>{e}</p>"
        
if __name__ == '__main__':
    app.run(debug=False)
