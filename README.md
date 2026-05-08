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

## 2. Vulnerabilities Identified

### Misconfigured Proxy Trust
Although HTTPS is enforced by the cloud provider, the Flask backend was not configured to trust reverse proxy headers.

**Impact:**
* Application may incorrectly assume an insecure HTTP environment.
* Improper handling of request security metadata.
* Potential misinterpretation of HTTPS status.

### Insecure Session Cookies
**Issues Identified:**
* Session cookies lacked the `Secure` attribute.
* Session cookies lacked the `SameSite` attribute.
* Increased risk of CSRF and session interception.

**Impact:**
* Session tokens could be exposed over insecure connections.
* Cookies could be used in cross-site requests.
* Increased vulnerability to session hijacking.

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
