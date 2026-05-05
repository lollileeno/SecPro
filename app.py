from flask import Flask, render_template

app = Flask(__name__)

# This route handles the main link 
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login.html')
def login():
    return render_template('login.html')

@app.route('/secure_login.html')
def secure_login():
    return render_template('secure_login.html')

@app.route('/register.html')
def register():
    return render_template('register.html')

@app.route('/secure_register.html')
def register():
    return render_template('secure_register.html')

@app.route('/dashboard.html')
def register():
    return render_template('dashboard.html')

@app.route('/admid.html')
def register():
    return render_template('admid.html')

@app.route('/secure_admin.html')
def register():
    return render_template('secure_admin.html')

if __name__ == '__main__':
    app.run(debug=True)