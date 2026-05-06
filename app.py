from flask import Flask, render_template, request, redirect, url_for, flash
import os
import psycopg2
import bcrypt # For secure password storage

app = Flask(__name__)

# Matches home.html
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db_con = create_database_connection()
        cur = db_con.cursor()

        # VULNERABLE: Look for the user in the database
        sql = f"SELECT * FROM \"USER\" WHERE username = '{username}' AND password = '{password}'"
        cur.execute(sql)
        user = cur.fetchone() # This tries to find one matching row

        cur.close()
        db_con.close()

        if user:
            # SUCCESS: The user exists and password matches
            flash('Welcome back!', 'success')
            return redirect(url_for('dashboard')) # THIS is how they get to the dashboard
        else:
            # FAILURE: Wrong username or password
            flash('Invalid credentials!', 'danger')
            return render_template('login.html')

    return render_template('login.html')

@app.route('/secure_login')
def secure_login():
    return render_template('secure_login.html')

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']

        db_con=create_database_connection()
        cur=db_con.cursor()

        sql_query = "INSERT INTO \"USER\" (username, password) VALUES ('" + username + "', '" + password + "')"

        try:
            cur.execute(sql_query)
            db_con.commit()

        except Exception as e:
            flash(f"Registeration faied: {e}",'danger')
            return render_template('/register.html')
        
        finally:
            cur.close()
            db_con.close()

        flash('Account created successfully!','success')
        return redirect(url_for('login'))
    return render_template('/register.html')

@app.route('/secure_register')
def secure_register():
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


def create_database_connection():
    return psycopg2.connect(os.environ.get('DATABASE_URL'))

#--------------vulnerable register----------


if __name__ == '__main__':
    app.run(debug=True)