
---

# **CSC429 - Security Vulnerabilities and Mitigation Report**

## **1. Introduction of the Project**

This project is a Flask-based web application designed to demonstrate both vulnerable and secure implementations of common web security mechanisms. The system includes user authentication, registration, session handling, role-based access control (RBAC), and a comment management system.

The main objective of the project is to intentionally implement several common security vulnerabilities and then demonstrate how they can be mitigated using industry-standard security practices such as parameterized queries, secure password hashing, input sanitization, and encryption over HTTPS.

---

## **2. Identified Vulnerabilities and Mitigation Steps**

### **1. SQL Injection**

**Vulnerability:**
The login and registration pages were initially vulnerable to SQL injection because user input was directly inserted into SQL queries using string formatting.

Example from code:

```python
sql = f"SELECT username, role FROM \"USER\" WHERE username = '{username}' AND password = '{md5hash_password}'"
```

**Mitigation Steps:**

* Replaced raw SQL queries with **parameterized queries**
* Used placeholders (`%s`) to safely pass user input

Example fix:

```python
sql = "SELECT password, role FROM \"USER\" WHERE username= %s"
cur.execute(sql, (username,))
```

---

### **2. Weak Password Storage**

**Vulnerability:**
Passwords were initially stored using **MD5 hashing**, which is insecure and vulnerable to brute-force and rainbow table attacks.

Example:

```python
md5hash_password = hashlib.md5(password.encode()).hexdigest()
```

**Mitigation Steps:**

* Replaced MD5 with **bcrypt**, a strong adaptive hashing algorithm
* Added automatic salt generation and secure verification

Example fix:

```python
hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
bcrypt.checkpw(password.encode('utf-8'), user_data[0].encode('utf-8'))
```

---

### **3. Cross-Site Scripting (XSS)**

**Vulnerability:**
User-generated content (comments) could be rendered without proper sanitization, allowing malicious scripts to execute in the browser.

**Mitigation Steps:**

* Relied on secure templating practices in Flask (Jinja2 auto-escaping)
* Ensured input is not directly executed as HTML/JavaScript
* Enforced safe rendering of comments in templates

---

### **4. Access Control (RBAC)**

**Vulnerability:**
Users were initially able to access restricted pages like the admin panel without proper authorization.

Example:

```python
@app.route('/admin')
def admin():
    return render_template('admin.html')
```

**Mitigation Steps:**

* Implemented **Role-Based Access Control (RBAC)**
* Created a decorator `requires_roles()` to restrict access based on user role
* Protected sensitive routes like `/secure_admin`

Example:

```python
@app.route('/secure_admin')
@requires_roles('admin')
def secure_admin():
```

---

### **5. Encryption & Secure Communication**

**Vulnerability:**
Sensitive data (sessions and authentication data) could be exposed if transmitted over insecure HTTP.

**Mitigation Steps:**

* Enforced **HTTPS/TLS communication**
* Enabled secure session cookies:

```python
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
```

* Used `ProxyFix` to ensure correct HTTPS detection behind reverse proxies
* Stored sensitive session data securely and cleared sessions on logout

---

## **3. Challenges and Solutions**

We faced an issue where sessions stayed active even after switching users.
Fix: Used session.clear() and manually deleted cookies on logout to fully reset sessions.

---

## **4. Code Explanation**
* bcrypt: chosen for secure password hashing with salting
* Parameterized queries: prevent SQL injection
* RBAC decorator: controls access based on user roles
* Secure cookies: protect sessions from XSS and CSRF
* HTTPS enforcement: ensures encrypted communication
---


## **5. Steps to Run the Application**

To run and access the application, follow these steps:

1. Open the given website link https://security-project-g5.onrender.com in your browser.
2. You will be given two login paths:

   * **Secure Login**
   * **Vulnerable Login**
3. You can log in using different types of users:

   * **Admin (Secure Path) Test Credentials:**

     * Username: **Lama**
     * Password: **1234567**
   * Alternatively, you can create a new account using the **“Create Account”** option.
4. After logging in:

   * Regular users will be directed to the dashboard.
   * Admin users will gain access to the control panel if logged in through the secure path.

**Important Note:**
Each login path (secure or vulnerable) uses separate authentication logic and session handling. This means that an account created or used in one path will not automatically work in the other. Additionally, logging in as an admin grants access to the secure control panel where administrative actions are available.

---

## **6. Instructions to Test Security Features**

### **1. SQL Injection Testing**

To test SQL Injection vulnerability in the **vulnerable login path**:

* **Username:**

```sql
' OR '1'='1' ORDER BY role --
```

* **Password:**

```
anything
```

This bypasses authentication and logs the user in as an admin.

---

### **2. Cross-Site Scripting (XSS) Testing**

##### The comments section is always protected from sql injection but in vulnerable edition is proned to XSS threat

To test XSS:

1. Log in using the vulnerable login path
2. Go to the comments section 
3. Enter:

```html
<script>alert('XSS Test')</script>
```

If vulnerable, a popup alert will appear.

---

### **3. Access Control Testing**

* **Admin users:**

  * Can access `/secure_admin`
  * Can delete and edit comments

* **Normal/vulnerable users:**

  * Can access comment system freely
  * Cannot access secure admin panel

This demonstrates RBAC enforcement.

---

## **Conclusion**

This project demonstrates how common web vulnerabilities can be intentionally introduced and then effectively mitigated using secure coding practices. The final implementation follows industry standards for authentication, authorization, encryption, and input handling, significantly improving the overall security of the application.

---

## **Contributors:**

**Leena Alonayq - Ghaida Alzaidan - Almaha Alaiban - Shahad Aldamegh - Eman Ameen**


