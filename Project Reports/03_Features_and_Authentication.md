# Features and User Authentication Architecture

## 1. Authentication Infrastructure
The system uses Django's core `django.contrib.auth` framework to provide a secure user authentication, session tracking, and access control system.

### 1.1 Architectural Security Components
- **Password Hashing:** Passwords are never stored in plain text. The application uses Django's default PBKDF2 algorithm with a SHA-256 hash and dynamic password salting.
- **Session Store:** User sessions are stored server-side in PostgreSQL (`django_session` table) and linked to client browsers via an encrypted `sessionid` HTTP cookie (`HttpOnly`, `SameSite=Lax`).
- **CSRF Defense:** State-altering operations (such as POST forms for login, registration, and product deletion) require a unique, cryptographically signed `csrftoken` token.

---

## 2. User Registration Workflow

The registration workflow creates both a standard Django authentication user and a linked custom `Customer` domain model within a single server operation.

> **📷 [IMAGE GENERATION PROMPT: USER REGISTRATION & DATABASE ATOMIC FLOW]**  
> *Use the prompt below with Gemini Imagen 3, Midjourney, or DALL-E 3 to generate a sequence flow diagram:*  
> **Prompt:** "A clean sequence flow diagram illustrating a web user registration process on a dark UI blueprint background.  
> - Left node: 'Client Web Form (POST Payload)' sending user data to Middle node: 'Django View (register_user in views.py)'.  
> - Middle node splits into two sequential database writing arrows pointing to Right node: 'PostgreSQL Database Engine'.  
> - Step 1 arrow: '1. Insert into auth_user (Hashed Password)'.  
> - Step 2 arrow: '2. Insert into store_customer (Linked Customer Profile)'.  
> Professional software engineering sequence diagram, clean arrows, labeled steps, neon cyan and violet highlighting."



### 2.1 Backend Implementation Logic (`store/views.py`)

```python
def register_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        membership = request.POST.get('membership_level', 'Regular')

        # 1. Validation check for existing user
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            return render(request, 'auth/register.html')

        # 2. Atomic creation of auth.User
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # 3. Creation of linked Customer record
        Customer.objects.create(
            user=user,
            full_name=full_name,
            email=email,
            phone=phone,
            address=address,
            membership_level=membership
        )

        messages.success(request, "Registration successful! Please log in.")
        return redirect('login')

    return render(request, 'auth/register.html')
```

---

## 3. Login, Session Management, & Access Control

### 3.1 Authentication Controller (`login_user`)
- Intercepts incoming `POST` request credentials.
- Invokes `django.contrib.auth.authenticate(username=username, password=password)`.
- If credentials match, `login(request, user)` attaches the user ID to the session engine and regenerates the session key to prevent Session Fixation attacks.

### 3.2 View Guarding via `@login_required`
Administrative routes (such as Product Create, Update, Delete dashboards) are protected using Python decorators:

```python
@login_required(login_url='login')
def product_crud_dashboard(request):
    # Route is inaccessible to unauthenticated guests
    products = Product.objects.all().order_by('product_id')
    return render(request, 'dashboard/product_list.html', {'products': products})
```

Attempting to access protected endpoints directly without an active session header triggers an automatic redirect to `/login/?next=/dashboard/`.

---

## 4. UI System & User Experience Features

### 4.1 Responsive Design & Grid System
The interface uses Bootstrap 5 flexbox grids and breakpoints (`sm`, `md`, `lg`, `xl`) to ensure usability across screen sizes:
- **Desktop (>= 1200px):** Multi-column dashboard grid displaying inventory metrics, side-by-side analytical reports, and data tables.
- **Mobile (< 768px):** Collapsible navigation menu, stacked table views, and full-width touch-friendly buttons.

### 4.2 Dynamic Navbar & Session State Management
The global navigation layout (`templates/components/navbar.html`) adjusts depending on the user's session state:

```html
<nav class="navbar navbar-expand-lg navbar-dark bg-dark shadow-sm">
  <div class="container-fluid">
    <a class="navbar-brand fw-bold" href="{% url 'home' %}">
      <i class="bi bi-cart3 me-2"></i>E-Commerce DBMS
    </a>
    <div class="collapse navbar-collapse" id="navbarNav">
      <ul class="navbar-nav me-auto">
        <li class="nav-item"><a class="nav-link" href="{% url 'home' %}">Home</a></li>
        <li class="nav-item"><a class="nav-link" href="{% url 'system_report' %}">System Reports</a></li>
        {% if user.is_authenticated %}
          <li class="nav-item"><a class="nav-link text-warning fw-bold" href="{% url 'dashboard' %}">Manage Inventory</a></li>
        {% endif %}
      </ul>
      <div class="d-flex align-items-center">
        {% if user.is_authenticated %}
          <span class="navbar-text text-light me-3">Welcome, <strong>{{ user.username }}</strong></span>
          <a href="{% url 'logout' %}" class="btn btn-outline-light btn-sm">Logout</a>
        {% else %}
          <a href="{% url 'login' %}" class="btn btn-outline-light btn-sm me-2">Login</a>
          <a href="{% url 'register' %}" class="btn btn-primary btn-sm">Register</a>
        {% endif %}
      </div>
    </div>
  </div>
</nav>
```

### 4.3 Interactive Asynchronous Toast Notifications
Server messages generated during ORM operations (e.g., "Product Updated", "Stock Trigger Blocked Insert") are rendered using fixed Bootstrap Toasts:

```html
<div class="toast-container position-fixed bottom-0 end-0 p-3" style="z-index: 1100;">
  {% for message in messages %}
    <div class="toast show align-items-center text-white bg-{{ message.tags }} border-0 shadow" role="alert">
      <div class="d-flex">
        <div class="toast-body">
          <i class="bi bi-info-circle-fill me-2"></i>{{ message }}
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
      </div>
    </div>
  {% endfor %}
</div>
```
JavaScript auto-dismisses toasts after 4,000 milliseconds.
