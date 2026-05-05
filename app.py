from flask import Flask, render_template

app = Flask(__name__)

# Matches home.html
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/secure_login_page')
def secure_login():
    return render_template('secure_login.html')

@app.route('/register')
def register():
    return render_template('register.html')

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