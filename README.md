# 🔐 A Security Demonstration Application

## 1. Introduction

This project is a Security Demonstration Application built with Flask and PostgreSQL. It is designed to showcase common web vulnerabilities and the modern defensive programming techniques used to mitigate them. The app features two distinct paths: a Vulnerable Version (demonstrating weak security) and a Secure Version (demonstrating hardened defenses).

Features

* Authentication: Contrast between weak MD5 hashing and secure Bcrypt salting.

* Database Security: Demonstration of SQL Injection vs. Parameterized Queries.

* Access Control: Implementation of Role-Based Access Control (RBAC) using custom decorators.

* Session Management: Hardened session cookies (HttpOnly, Secure, SameSite) and session fixation protection.

* XSS Protection: Controlled demonstration of reflected XSS vs. automatic template escaping.

---

## 2. How to Run 

# Get Started! - To access the live application, open your browser and navigate to:
https://security-project-g5.onrender.com

# Exploring the Two Paths

The application is divided into two distinct versions to demonstrate the "Before and After" of security implementation.

# A. The Vulnerable Path (Red Labels)

Vulnerable Login/Register: Uses insecure MD5 hashing and is susceptible to SQL Injection.

Vulnerable Admin: A page with no access control; anyone can view it if they know the URL.

Vulnerable Dashboard: Displays comments using the | safe filter, allowing for Reflected XSS attacks.

# B. The Secure Path (Green Labels)

Secure Login/Register: Uses Bcrypt for password salting and Parameterized Queries to block SQL Injection.

Secure Admin: Protected by Role-Based Access Control (RBAC); only accounts with the 'admin' role can enter.

Secure Dashboard: Automatically escapes HTML tags in comments to prevent XSS.

---

## 3. Mitigation Steps

### Enforcing Reverse Proxy Trust
To ensure Flask correctly processes the secure HTTPS headers forwarded by the proxy, the `ProxyFix` middleware from Werkzeug was implemented:

```python
from werkzeug.middleware.proxy_fix import ProxyFix

app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,
    x_proto=1,
    x_host=1,
    x_prefix=1
)
```

### Secure Session Cookie Configuration
Strict security configurations were explicitly defined to enforce defense-in-depth for the session cookies:

```python
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
```

---

## 4. Admin Login (Testing Only)

Use the following credentials to log in as admin to verify the secure configuration:

* **Username:** `Lama`
* **Password:** `123`

## 5. Conclusion

The identified issues were mitigated by enforcing reverse proxy trust and hardening session cookie security. These changes significantly improve the application's resilience against session hijacking, CSRF, and transport-layer misconfigurations.
